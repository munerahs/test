<h1 align="center">Masar 🚆</h1>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?size=20&duration=4000&pause=800&color=808080&center=true&vCenter=true&width=1000&lines=AI-Powered+Digital+Twin+System+for+Enhanced+Riyadh+Metro+Services" />
</p>

---

## Introduction
**Masar** is an AI-powered **Digital Twin system** designed to enhance passenger experience and optimize metro operations in the Riyadh Metro.  
The system predicts station crowd levels 30 minutes ahead, provides real-time congestion visualizations, and offers an intelligent dashboard for metro staff to monitor and manage high-traffic situations.  
Masar supports the goals of **Saudi Vision 2030** by enabling smarter, safer, and more efficient public transportation.

---

## Key Features

### Passenger Mobile App
- User registration, login, password reset, and logout
- Station search and map-based station selection
- Location access to identify the nearest station
- Current station crowd level display
- 30-minute predicted crowd level display
- Upcoming trips view
- Carriage crowd level view
- Station notification preferences
- AI chatbot for passenger support
- Lost item reporting through the chatbot
- Lost report tracking from the passenger profile

### Staff Dashboard
- Staff login and logout
- Map-based station selection
- Station KPIs for selected stations
- Current and predicted station crowd levels
- Incoming train monitoring
- Carriage crowd level monitoring
- Crowd flow analytics for previous hours
- Staff-side notifications for important updates
- Lost & Found notifications when new items or reports are added
- Found items and lost reports management
- AI-assisted found item form auto-fill
- AI-based matching between lost and found items
- OTP-supported item collection workflow

---

## Technology Stack

### Frontend (Mobile App)
- **Flutter (Dart)**
- Google Maps integration
- Real-time UI updates via Firestore

### Web Dashboard (Staff)
- **React**
- **Vite**
- Firebase Hosting
- Real-time crowd monitoring for metro stations
- Integration with XGBoost-based crowd prediction outputs
- Staff notifications and Lost & Found management

### AI & Prediction Models
- **Python** (NumPy, Pandas, Scikit-Learn, XGBoost)
- Pre-trained **XGBoost model** for 30-minute crowd forecasting
- **OpenAI API** for chatbot-based passenger support
- Digital Twin–based data simulation (`masar-sim`)
- Training notebooks located in: `masar_forecasting/notebooks`

### Backend & Services
- **FastAPI** for REST APIs
- Deployed on **Render**
- Endpoints for trips, live snapshots, alerts, and predictions
- Firebase Admin SDK for secure Firestore access

### Databases & Cloud
- **Firestore NoSQL Database**
- Firebase Authentication
- Firebase Hosting
- Cloud Storage for assets/configs

---

## Live Deployment

- Staff Dashboard: https://masarapp-b9521.web.app/
- Backend API Docs: https://masar-sim.onrender.com/docs

---

## Smart Lost & Found System

Masar includes a smart Lost & Found workflow that helps passengers report lost items and helps staff manage found items through the dashboard.

### Passenger Side
- Submit lost item reports through the chatbot
- Track submitted reports from the profile
- Receive email updates when a possible match is found
- Complete the collection process using OTP verification

### Staff Side
- View lost reports and found items
- Add found items through the dashboard
- Upload a found item image
- Use AI-assisted auto-fill to complete item details
- Review AI-based matching suggestions
- Confirm matched items and support OTP-based collection

---

## Crowd Prediction and Digital Twin

Masar uses a Digital Twin simulation environment to model metro crowd behavior and generate passenger-flow data.  
The forecasting module uses an XGBoost model to predict station crowd levels 30 minutes ahead.

### Prediction Outputs
- Current occupancy
- Predicted occupancy after 30 minutes
- Station capacity
- Utilization ratio
- Predicted crowd level
- Crowd level code

---

## API Endpoints

The backend provides several endpoints for live snapshots and 30-minute forecasting.

```text
POST /predict_30min
GET  /predict_30min_live/{station_code}
GET  /health
GET  /snapshot/all
GET  /snapshot/{station_id}
GET  /backfill_last_2h
```

API documentation is available through Swagger UI:

```text
https://masar-sim.onrender.com/docs
```

---

## Launch Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

---

### 2️⃣ Run the Flutter App

```bash
flutter pub get
flutter run
```

For web:

```bash
flutter run -d chrome
```

---

### 3️⃣ Run the Staff Dashboard

```bash
cd web
npm install
npm run dev
```

---

### 4️⃣ Run the FastAPI Backend

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

---

### 5️⃣ Run the Forecasting Module

Since the project uses **notebooks** instead of `.py` scripts:

```bash
cd masar_forecasting
pip install -r requirements.txt
```

To **train or retrain** the XGBoost model:

- Open the notebook:

```text
notebooks/XGBoost_Training_CrowdPrediction.ipynb
```

- Run all cells to generate a new model under:

```text
models/masar_xgb_30min_model.pkl
```

To **generate predictions**:

- Use the prediction cells inside the same notebook.
- Export results to CSV as needed for the backend.

---

### 6️⃣ Firebase Setup

Make sure the following files are added (not committed):

- `google-services.json` → **Android**
- `GoogleService-Info.plist` → **iOS**
- Backend service account key → For FastAPI Firestore access
- Firebase configuration file → For the staff dashboard

---

## Project Structure

```text
lib/                 # Flutter mobile app
masar-sim/           # Digital Twin data simulation
masar_forecasting/   # XGBoost forecasting notebooks + model
web/                 # React/Vite staff dashboard
assets/              # Images and static files
android/ios/web/     # Flutter platform folders
```

---

## Vision 2030 Alignment

Masar supports Saudi Vision 2030 by contributing to:
- Smart transportation systems
- AI-powered public services
- Improved passenger experience
- Safer and more efficient metro operations
- Smart city transformation initiatives

---
