# 🚀 NCMB - CBT Examination & Assessment Platform

A high-performance, enterprise-grade Computer-Based Testing (CBT) platform tailored for **NCMB**, built with **FastAPI**, **vanilla JavaScript (zero-framework client)**, and dual-database support (**SQLite** for local offline LAN testing and **PostgreSQL** for cloud deployments).

Engineered for recruitment drives, professional promotion examinations, and staff competency assessments.

---

## 🌟 Key Platform Features

### 1. Candidate Examination Engine
- **Instant Candidate Accreditation**: Candidate logs in with their Employee ID / Registration Number and single-use 5-digit PIN / Token.
- **Biometric / Photocard Slip Support**: Visual identification with candidate photograph and bio-data before test initiation.
- **Dynamic Question Palette**: Fast navigation between questions with clear visual indicators (*Answered*, *Unanswered*, *Current*).
- **Synchronized Countdown Timer**: High-precision countdown timer with server synchronization and auto-submission on expiration.
- **Unanswered Warning Dialog**: Prevents accidental premature submission if questions remain unanswered.
- **Printable Result / Submission Slip**: Instant post-exam confirmation slip with unique clearance hash, timestamp, and audit trail.

### 2. Built-in Anti-Cheat & Security Suite
- **Tab-Switch & Window Blur Detection**: Instant visual blackout curtain when focus is lost.
- **Strike System**: Configurable multi-strike warning dialog for unauthorized window navigation.
- **Context Menu & Shortcut Lockdown**: Right-click, Copy, Paste, PrintScreen, and DevTools shortcuts (`F12`, `Ctrl+Shift+I`) disabled.
- **Security Incident Logging**: Every blur, shortcut attempt, and tab-switch is timestamped and recorded in `submissions.security_flags`.

### 3. Administrator Operations Center (`/#admin`)
- **Live Candidate Monitor**: Real-time overview of active sessions, scores, and completion percentages.
- **Candidate Session Reset**: Instantly unlock and reset any candidate's test session in case of local power outage or browser crash.
- **Exam Status Master Switch**: One-click master toggle to **Open** or **Close** the examination portal.
- **Token Management**: Batch generation and status tracking of single-use scratch-card PINs.
- **One-Click Export**: Download official consolidated score sheets directly to `.xlsx` (Excel) or `.csv`.
- **Question Editor**: In-browser inspection and editing of question text, options, and answer keys.

---

## 📁 Project Structure

```text
NCMB/
├── .env                      # Active platform configuration (NCMB branding, timer, passwords)
├── .env.example              # Configuration template
├── app.py                    # Core FastAPI backend & REST API
├── database.py               # Database abstraction layer (SQLite / PostgreSQL)
├── parser.py                 # Bulk Question Ingestion Engine (Word & Excel)
├── email_service.py          # Automated result email dispatch via SMTP
├── run_cbt.py                # Server launcher with auto-browser popup
├── start_cbt.bat             # One-click Windows runner
├── requirements.txt          # Python dependencies
├── master_tokens.json        # 3,500 master 5-digit single-use PINs
├── sample_questions/         # Place your NCMB question files (.docx / .xlsx) here
└── static/
    ├── index.html            # Single-Page Application (CBT + Admin)
    ├── css/style.css         # Modern, responsive UI design
    ├── js/cbt.js             # Core examination state machine
    └── images/               # NCMB logo and visual assets (logo.png)
```

---

## ⚡ Quick Start (Run in 2 Minutes)

### Step 1: Install Dependencies
Make sure you have **Python 3.10+** installed:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Your Exam Settings
Open `.env` in any text editor if you wish to adjust exam timing or admin passwords:
```env
ORGANIZATION_NAME="NCMB"
EXAM_TITLE="NCMB 2026 Professional Competency & Promotion Examination"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="admin123456"
DEFAULT_DURATION_MINUTES=30
QUESTIONS_PER_EXAM=40
```

### Step 3: Ingest Questions
Drop your question `.docx` or `.xlsx` files into `sample_questions/` and run:
```bash
python parser.py
```
*(Sample questions are already loaded into the local database).*

### Step 4: Launch the Server
- **On Windows**: Double-click **`start_cbt.bat`**  
  *OR*
- **Via Command Line**:
  ```bash
  python run_cbt.py
  ```

The browser will automatically open to:
- **NCMB Candidate Exam Portal**: `http://127.0.0.1:8000`
- **NCMB Admin Dashboard**: `http://127.0.0.1:8000/#admin`

---

## 📝 Preparing Questions

### Format A: Word Document (`.docx`)
Save your file in `sample_questions/` (e.g. `General_Cadre.docx`). Format questions using standard numbering:

```text
1. What is the primary purpose of public sector financial auditing?
A. To guarantee 100% profitability
B. To ensure statutory compliance and accountability
C. To reduce staff salaries
D. To eliminate tax returns
Correct Answer: B

2. A Memorandum submitted to Management should conclude with:
A. Personal remarks
B. Clear recommendations and prayer
C. A list of all staff complaints
D. Financial demands
Correct Answer: B
```

### Format B: Excel Spreadsheet (`.xlsx`)
Create a sheet with the following header row:

| Category | Question | Option A | Option B | Option C | Option D | Answer |
|:---|:---|:---|:---|:---|:---|:---:|
| General | What is GDP? | Gross Domestic Product | Gross Daily Profit | General Debt Pool | Global Direct Price | A |

Run `python parser.py` to ingest the new questions into the database.

---

## 🌐 Deployment Options

### Option 1: Offline Local Area Network (LAN)
For exam halls with no internet connectivity:
1. Run `python run_cbt.py` on the supervisor's laptop (connected to the hall's Wi-Fi router / LAN switch).
2. Note the supervisor's local IP address (e.g., `192.168.1.50`).
3. Candidate laptops/tablets navigate to `http://192.168.1.50:8000`.
4. All submissions are stored locally in `cbt.db`. Zero internet required!

### Option 2: Cloud Deployment (Vercel, Render, Railway, VPS)
1. Provision a PostgreSQL database (e.g., [Neon.tech](https://neon.tech), Supabase, or AWS RDS).
2. Set `DATABASE_URL` in your environment variables:
   ```env
   DATABASE_URL="postgresql://user:password@host/dbname?sslmode=require"
   ```
3. Deploy the repository. The application will automatically detect PostgreSQL and initialize all tables.
