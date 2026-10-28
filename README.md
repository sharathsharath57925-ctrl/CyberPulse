# 🛡️ CyberPulse — AI-Powered Cybersecurity Dashboard

CyberPulse is a cybersecurity dashboard designed to help users identify potential phishing links, suspicious email content, and network traffic indicators through a simple, interactive Streamlit interface.

## 🚀 Features

### 🔗 LinkShield — URL Scanner
- Scan URLs for suspicious characteristics.
- Identify potential phishing indicators.
- Display scan results through the dashboard.

### 📧 EmailGuard — Email Security
- Analyze email text for potential phishing indicators.
- Highlight suspicious wording and warning signs.
- Help users recognize potentially fraudulent messages.

### 🌐 NetworkWatch — Network Analysis
- Display local network information, such as hostname and IP address.
- Analyze uploaded PCAP and PCAPNG network capture files.
- Show packet information and network traffic indicators.

### 📊 Security Dashboard
- View security scan statistics.
- Review scan activity across modules.
- Explore visual summaries of scan history.

### 🗂️ Scan History
- Store and review previous scan results using SQLite.
- Track scan activity across supported modules.

## 🧰 Technologies Used

- **Python** — Core programming language
- **Streamlit** — Interactive web dashboard
- **SQLite** — Local database for scan history
- **Scapy** — Network packet analysis
- **Pandas** — Data handling and analysis
- **Plotly** — Interactive visualizations, where configured

## 📁 Project Structure

```text
CyberPulse/
├── app.py
├── requirements.txt
├── backend/
│   ├── email_scanner.py
│   └── url_scanner.py
├── database/
│   └── db.py
└── frontend/
    ├── dashboard.py
    └── dashboard_backup.py
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/sharathsharath57925-ctrl/CyberPulse.git
cd CyberPulse
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

The application should open in your browser. If it does not, Streamlit will display a local URL in the terminal.

## 🔒 Security Notice

- Do not upload `.env` files, passwords, API keys, or other secrets to GitHub.
- Do not upload private network captures or sensitive scan records.
- Treat scan results as indicators, not definitive proof that a URL, email, or network packet is malicious.

## ⚠️ Disclaimer

CyberPulse is an educational cybersecurity project intended for authorized security analysis and awareness. It should not be treated as a replacement for professional security tools or expert investigation.

## 👨‍💻 Author

**Sharath VT**

Developed as a cybersecurity learning and dashboard project.
