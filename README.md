# AI Resume Analyzer 📄

An AI-powered resume analyzer built with Python, Streamlit, and the Anthropic Claude API.

Upload a PDF resume, paste a job description, and get:
- **Match score** (0–100)
- **Matched & missing skills**
- **Category breakdown** (Technical, Experience, Education, Soft Skills)
- **Key strengths** for the role
- **Actionable improvement suggestions**
- **Overall summary**

---

## Setup

### 1. Clone / download
```bash
git clone <your-repo>
cd resume_analyzer
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

---

## Usage

1. Paste your **Anthropic API key** — get one free at https://console.anthropic.com
2. Upload your resume as a **PDF** (text-based, not scanned)
3. Paste the **job description**
4. Click **Analyze Resume**

---

## Project structure

```
resume_analyzer/
├── app.py            # Streamlit UI
├── analyzer.py       # PDF extraction + Claude API logic
├── requirements.txt
└── README.md
```

---

## Tech stack

| Layer | Library |
|-------|---------|
| UI    | Streamlit |
| PDF   | pypdf |
| AI    | Anthropic Claude (claude-sonnet-4-20250514) |

---

## Notes

- Your API key is **never stored** — it lives only in your browser session.
- Very large PDFs are truncated to ~8 000 characters of resume text to stay within token limits.
- Requires a text-based PDF; scanned PDFs will return empty results.
- Get your free Anthropic API key at https://console.anthropic.com
