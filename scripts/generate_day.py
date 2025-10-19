# scripts/generate_day.py
import json, yaml, os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

def load_cfg():
    with open("./config/00_config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_timerange(cfg):
    tz = cfg.get("tz", "Asia/Riyadh")
    start_hour = cfg["schedule"]["start_hour"]
    hours = cfg["schedule"]["hours_per_day"]
    res_min = cfg["schedule"]["minute_resolution"]
    # نستخدم وقت النظام الحالي ونستبدل الساعة فقط (كافي للتوليد اليومي)
    start = datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=hours)
    times = pd.date_range(start, end, freq=f"{res_min}min", inclusive="left")
    return times, start

def is_peak(ts, peak_windows):
    if not peak_windows:
        return False
    tod = ts.time()
    for w in peak_windows:
        s = datetime.strptime(w["start"], "%H:%M").time()
        e = datetime.strptime(w["end"], "%H:%M").time()
        if s <= tod <= e:
            return True
    return False

def cyclical_pick(seq, i):
    return seq[i % len(seq)]

def train_capacity(line_def):
    # لو موجود الحقل الجاهز استخدمه، وإلا احسبه من عدد العربات × سعة العربة
    if "train_total_capacity" in line_def and line_def["train_total_capacity"]:
        return line_def["train_total_capacity"]
    return line_def["cars_per_train"] * line_def["carriage_capacity"]

def ensure_outdir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def main():
    CFG = load_cfg()
    F = CFG["fields"]
    times, start = build_timerange(CFG)

    # تحميل البذور
    stations = load_json(CFG["seeds"]["stations_file"])
    lines_list = load_json(CFG["seeds"]["lines_file"])
    lines = {x["line_name"]: x for x in lines_list}

    dwell_min = CFG.get("assumptions", {}).get("avg_dwell_min", 12)
    out_dir = CFG["output"]["out_dir"]
    ensure_outdir(out_dir)

    all_chunks = []

    for st in stations:
        st_code = st.get(F["station_code"])
        st_name = st.get(F["station_name"])
        occ_cap = st.get(F["occupancy_cap_field"])
        plat_cap = st.get(F["platform_cap_field"])
        peak_cap = st.get(F["peak_cap_field"])
        lines_in_station = [l.get("line_name") for l in (st.get(F["lines_field"]) or [])]

        if not lines_in_station:
            # لا يوجد خطوط مرفقة بالمحطة
            continue

        for ln in lines_in_station:
            line_def = lines.get(ln)
            if not line_def:
                print(f"[WARN] line '{ln}' غير موجود في lines.json — سأتجاهله")
                continue

            peak_windows = line_def.get("peak_windows") or []
            hw_peak = (line_def.get("headway_patterns") or {}).get("peak_min") or []
            hw_off  = (line_def.get("headway_patterns") or {}).get("offpeak_min") or []
            if not hw_peak or not hw_off:
                print(f"[WARN] headway pattern ناقص لخط {ln} — سأتجاهله")
                continue

            rows = []
            cap_train = train_capacity(line_def)

            for i, ts in enumerate(times):
                peak = is_peak(ts, peak_windows)
                hw_min = cyclical_pick(hw_peak if peak else hw_off, i)  # توزيع دوري
                tph = 60.0 / hw_min                          # trains per hour
                ppm = (tph * cap_train) / 60.0               # passengers per minute (تدفق)
                est_present = ppm * dwell_min                 # تقدير الموجودين لحظيًا = تدفق × مدة البقاء

                row = {
                    "timestamp": ts,
                    "station_code": st_code,
                    "station_name": st_name,
                    "line_name": ln,
                    "is_peak": peak,
                    "headway_min": hw_min,
                    "trains_per_hour": round(tph, 3),
                    "train_capacity": cap_train,
                    "passengers_per_min": round(ppm, 3),
                    "estimated_present": round(est_present),
                }

                # نسب الازدحام (إن وجدت السعات)
                if occ_cap:
                    row["crowding_station_pct"] = round(100.0 * est_present / occ_cap, 2)
                if plat_cap:
                    # تقدير تقريبي: الموجودون على الرصيف ≈ 40% من الموجودين بالمحطة (قابل للتعديل لاحقًا)
                    est_on_platform = est_present * 0.4
                    row["crowding_platform_pct"] = round(100.0 * est_on_platform / plat_cap, 2)
                if peak_cap:
                    row["flow_vs_peak_pct"] = round(100.0 * (ppm * 60.0) / peak_cap, 2)  # تدفق الساعة مقابل قدرة الذروة

                rows.append(row)

            df = pd.DataFrame(rows)
            all_chunks.append(df)

    if not all_chunks:
        raise SystemExit("❌ لا توجد بيانات مولّدة. تأكدي من stations.json و lines.json.")

    day_df = pd.concat(all_chunks, ignore_index=True)

    # الإخراج
    stamp = start.strftime('%Y%m%d')
    fmt = (CFG["output"].get("format") or "parquet").lower()
    out_path = Path(out_dir) / f"day_{stamp}.{ 'csv' if fmt=='csv' else 'parquet' }"

    if fmt == "csv":
        day_df.to_csv(out_path, index=False, encoding="utf-8")
    else:
        # parquet (افتراضي)
        try:
            import pyarrow  # noqa
        except ImportError:
            print("[INFO] pyarrow غير مثبت — سأحفظ CSV.")
            out_path = Path(out_dir) / f"day_{stamp}.csv"
            day_df.to_csv(out_path, index=False, encoding="utf-8")
        else:
            day_df.to_parquet(out_path, index=False)

    # ملخص سريع
    print(f"✅ generated rows: {len(day_df):,}")
    print(f"➡️  file: {out_path}")
    agg = (day_df
           .groupby(["station_code","line_name"], as_index=False)
           .agg(passengers_per_min_peak=("passengers_per_min","max"),
                trains_per_hour_peak=("trains_per_hour","max")))
    print("\nTop per station/line (peak per-minute flow & tph):")
    print(agg.sort_values("passengers_per_min_peak", ascending=False).head(12).to_string(index=False))

if __name__ == "__main__":
    main()

