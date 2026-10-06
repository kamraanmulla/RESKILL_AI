# ReSkillAI — Dual-Platform Career Intelligence Platform

> **"One ReSkillAI platform, available on Web and Mobile, sharing the same backend, account, data, intelligence, and AI services."**

ReSkillAI transforms academic engineering potential into industry-ready capability through deterministic career intelligence, adaptive assessment, personalized skill gap mapping, verified learning pathways, and official job tracking.

This repository powers both the **Web Application (Laptop / Desktop)** and the **Android Mobile Application (Phone)** from a single, unified codebase.

---

## 🏗️ Target Architecture

```
                  +----------------------------------------------+
                  |                  ReSkillAI                   |
                  +----------------------+-----------------------+
                                         |
                  +----------------------+-----------------------+
                  |                                              |
                  v                                              v
      +------------------------+                    +------------------------+
      |    Web Application     |                    |   Android Application  |
      |     (React + Vite)     |                    |  (React + Capacitor)   |
      |    Laptop / Desktop    |                    |         Phone          |
      +------------------------+                    +------------------------+
                  |                                              |
                  +----------------------+-----------------------+
                                         |
                                         v
                         +-------------------------------+
                         |        FastAPI Backend        |
                         |   (Python / SQLAlchemy / DB)  |
                         +---------------+---------------+
                                         |
                                         v
                         +-------------------------------+
                         |      Google Gemini API        |
                         |     (Server-Side ONLY)        |
                         +-------------------------------+
```

- **Single Source of Truth**: Desktop and mobile share the exact same FastAPI backend, user accounts, canonical profiles, and career analytics.
- **Zero Duplicate Business Logic**: All scoring, calibration, gap detection, and roadmap generation execute centrally.
- **Server-Side AI Security**: Google Gemini API keys are strictly confined to the backend server runtime and never bundled in the frontend or Android APK.

---

## 🔒 Gemini & API Security Architecture

1. **Server-Side Isolation**: The Google Gemini API key resides solely in `backend/.env`.
2. **Zero Client Leakage**: Neither the React web application nor the Android APK bundle includes Gemini keys or direct Google AI endpoints.
3. **Controlled Gateway**: All intelligence features (Resume Analysis, Adaptive Assessment, AI Career Coach) pass through authenticated FastAPI endpoints (`/api/...`).
4. **Resilient Intelligence**: If the external Gemini service is temporarily unavailable, deterministic server-side heuristics provide stable, continuous career intelligence without crashes.

---

## 📱 Dual-Platform Experience

| Feature | Desktop Web | Android Mobile App |
| :--- | :--- | :--- |
| **Interface** | Spacious editorial layout with persistent sidebar and split-pane analytics | Touch-optimized, safe-area padded layout with 6-tab bottom navigation |
| **Navigation** | Full-width Sidebar + Topbar breadcrumb | Bottom Nav: **Home · Assess · Roadmap · Learn · Jobs · Profile** + Drawer |
| **Hardware Back** | Browser back / forward buttons | Native Android back button closes modals, steps back to dashboard, or exits |
| **External Links** | Opens in new browser tab (`target="_blank"`) | Uses `@capacitor/browser` (Chrome Custom Tabs) with seamless return to app |
| **Resume Upload** | Drag & drop or file dialog (PDF, DOCX, TXT) | System Document Picker / File Chooser (PDF, DOCX, TXT) |
| **Session Sync** | Canonical backend profile via SQLite/PostgreSQL | Canonical backend profile via SQLite/PostgreSQL |

---

## 🚀 Getting Started

### 1. Prerequisites

- **Node.js**: v18+ (v20+ recommended)
- **Python**: v3.10+ (tested with Python 3.12 - 3.14)
- **Git**
- **Android Studio & JDK 17+** *(Only required for building the Android `.apk` binary)*

---

### 2. Backend Setup (FastAPI)

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. (Optional) Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # macOS/Linux:
   source venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `backend/.env`:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-3.6-flash
   HOST=0.0.0.0
   PORT=8000
   ```

5. Run the backend server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *Note: Using `--host 0.0.0.0` allows the server to listen on all interfaces, enabling connections from Android emulators and physical devices.*

6. Verify backend health:
   ```bash
   curl http://localhost:8000/api/health
   # Returns: {"status": "healthy", ...}
   ```

7. Run backend test suite:
   ```bash
   pytest
   # Or: python -m pytest
   ```

---

### 3. Web Application Setup (React + Vite)

1. From the project root, install frontend dependencies:
   ```bash
   npm install
   ```

2. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

3. Type-check and production build:
   ```bash
   npx tsc --noEmit
   npm run build
   ```

---

### 4. Android Mobile Application Setup (Capacitor)

ReSkillAI uses **Capacitor 8** to wrap the existing React + Vite frontend for Android.

#### Application Identifiers
- **App Name**: `ReSkillAI`
- **Application ID / Package Name**: `com.reskillai.app`
- **Web Asset Directory**: `dist`
- **Android Project Location**: `android/`

#### Networking Configuration (Crucial for Local Development)

Inside the Android environment, `localhost` refers to the **mobile device itself**, not your development laptop.

| Platform / Context | Backend URL | Setup Note |
| :--- | :--- | :--- |
| **Desktop Web Browser** | `/api` | Vite dev server proxies `/api` to `http://127.0.0.1:8000` |
| **Android Emulator** | `http://10.0.2.2:8000/api` | Built-in default in `resolveApiBaseUrl()`; 10.0.2.2 routes to host computer |
| **Physical Android Phone** | `http://<YOUR_LAN_IP>:8000/api` | Set `VITE_API_BASE_URL=http://192.168.x.x:8000/api` in `.env` before building |
| **Production Cloud** | `https://api.yourdomain.com/api` | Set `VITE_API_BASE_URL=https://api.yourdomain.com/api` in `.env.production` |

#### Building and Syncing the Android App

1. Build the web assets:
   ```bash
   npm run build
   ```

2. Synchronize assets and Capacitor plugins into the Android native project:
   ```bash
   npx cap sync android
   ```

3. Open the Android project in Android Studio:
   ```bash
   npx cap open android
   ```

4. Alternatively, build the debug APK directly via command line (requires JDK 17+ and Android SDK configured):
   ```bash
   cd android
   # Windows:
   .\gradlew.bat assembleDebug
   # macOS/Linux:
   ./gradlew assembleDebug
   ```
   The compiled APK will be generated at:
   `android/app/build/outputs/apk/debug/app-debug.apk`

---

## 🧪 Verification & Test Commands Summary

```bash
# 1. Run all 58+ backend tests
cd backend
python -m pytest

# 2. Frontend TypeScript typecheck
cd ..
npx tsc --noEmit

# 3. Production web build
npm run build

# 4. Capacitor Android synchronization
npx cap sync android
```

---

## 📄 License & Attribution

Designed and maintained for candidate career intelligence, skills discovery, and verified workforce mobility.
