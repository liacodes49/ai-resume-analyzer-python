import streamlit as st
import json
import re
from analyzer import extract_text_from_pdf, analyze_resume

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

  html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
  }

  .stApp {
    background: #0d0d0f;
    color: #e8e6e1;
  }

  /* Header */
  .hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
  }
  .hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2.4rem, 5vw, 3.8rem);
    font-weight: 400;
    letter-spacing: -0.02em;
    color: #f5f3ee;
    margin-bottom: 0.5rem;
    line-height: 1.1;
  }
  .hero h1 span { color: #6ee7b7; }
  .hero p {
    color: #8a8880;
    font-size: 1.05rem;
    font-weight: 300;
    max-width: 520px;
    margin: 0 auto;
  }

  /* Divider */
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2e2e35, transparent);
    margin: 1.5rem 0;
  }

  /* Score card */
  .score-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
  }
  .score-circle {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    font-weight: 400;
    border: 3px solid;
    margin-bottom: 0.75rem;
    position: relative;
  }
  .score-circle small {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: -4px;
  }
  .score-high  { color: #6ee7b7; border-color: #6ee7b7; background: rgba(110,231,183,.07); }
  .score-mid   { color: #fbbf24; border-color: #fbbf24; background: rgba(251,191,36,.07); }
  .score-low   { color: #f87171; border-color: #f87171; background: rgba(248,113,113,.07); }

  /* Section card */
  .card {
    background: #15151a;
    border: 1px solid #252530;
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.2rem;
  }
  .card h3 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    font-weight: 400;
    color: #f5f3ee;
    margin: 0 0 1rem 0;
  }

  /* Tag chips */
  .tags { display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .tag {
    padding: 0.3rem 0.8rem;
    border-radius: 99px;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.02em;
  }
  .tag-present  { background: rgba(110,231,183,.15); color: #6ee7b7; border: 1px solid rgba(110,231,183,.3); }
  .tag-missing  { background: rgba(248,113,113,.12); color: #f87171; border: 1px solid rgba(248,113,113,.3); }
  .tag-partial  { background: rgba(251,191,36,.12);  color: #fbbf24; border: 1px solid rgba(251,191,36,.3); }

  /* Strength / improvement items */
  .item {
    display: flex;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1e1e24;
    font-size: 0.92rem;
    color: #ccc8c0;
    line-height: 1.5;
  }
  .item:last-child { border-bottom: none; }
  .item-icon { flex-shrink: 0; margin-top: 1px; }

  /* Upload zone */
  .uploadedFile { background: #15151a !important; border-color: #252530 !important; }
  [data-testid="stFileUploader"] > div { background: #15151a; border: 2px dashed #2e2e38;
    border-radius: 12px; padding: 1.5rem; transition: border-color .2s; }
  [data-testid="stFileUploader"] > div:hover { border-color: #6ee7b7; }

  /* Textarea */
  textarea {
    background: #15151a !important;
    border: 1px solid #252530 !important;
    color: #e8e6e1 !important;
    border-radius: 8px !important;
  }

  /* Button */
  .stButton > button {
    background: linear-gradient(135deg, #6ee7b7 0%, #3b82f6 100%);
    color: #0d0d0f;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.04em;
    border: none;
    border-radius: 8px;
    padding: 0.65rem 2.5rem;
    transition: opacity .2s, transform .15s;
    width: 100%;
  }
  .stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }

  /* Progress bar */
  .progress-wrap { margin-bottom: 0.6rem; }
  .progress-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    color: #8a8880;
    margin-bottom: 4px;
  }
  .progress-bar-bg {
    height: 6px;
    background: #1e1e24;
    border-radius: 99px;
    overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 1s ease;
  }

  /* API key notice */
  .api-notice {
    background: rgba(59,130,246,.1);
    border: 1px solid rgba(59,130,246,.3);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    font-size: 0.85rem;
    color: #93c5fd;
    margin-bottom: 1.2rem;
  }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 0; }
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>AI <span>Resume</span> Analyzer</h1>
  <p>Upload your resume and paste a job description to get an instant match score and personalized suggestions.</p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── API Key ────────────────────────────────────────────────────────────────────
st.markdown('<div class="api-notice">🔑 Enter your Google Gemini API key below — it is never stored and only used for this session.</div>', unsafe_allow_html=True)
api_key = st.text_input("Google Gemini API Key", type="password", placeholder="AIza...", label_visibility="collapsed")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Input columns ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("#### 📄 Your Resume (PDF)")
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.success(f"✓ {uploaded_file.name} uploaded ({uploaded_file.size // 1024} KB)")

with col_right:
    st.markdown("#### 💼 Job Description")
    job_description = st.text_area(
        "Paste job description",
        height=200,
        placeholder="Paste the full job description here — include skills, responsibilities, and requirements for the best analysis...",
        label_visibility="collapsed",
    )

st.markdown("")

# ── Analyze button ─────────────────────────────────────────────────────────────
col_btn, _ = st.columns([1, 2])
with col_btn:
    analyze_btn = st.button("✦ Analyze Resume", use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Analysis ───────────────────────────────────────────────────────────────────
if analyze_btn:
    if not api_key:
        st.error("Please enter your Anthropic API key above.")
    elif not uploaded_file:
        st.error("Please upload a PDF resume.")
    elif not job_description.strip():
        st.error("Please paste a job description.")
    else:
        with st.spinner("Extracting resume text…"):
            resume_text = extract_text_from_pdf(uploaded_file)

        if not resume_text.strip():
            st.error("Could not extract text from the PDF. Make sure it's a text-based (not scanned) PDF.")
        else:
            with st.spinner("Analyzing with AI…"):
                result = analyze_resume(resume_text, job_description, api_key)

            if "error" in result:
                st.error(f"Analysis failed: {result['error']}")
            else:
                # ── Score ──────────────────────────────────────────────────
                score = result.get("match_score", 0)
                if score >= 70:
                    cls = "score-high"
                    verdict = "Strong Match"
                elif score >= 45:
                    cls = "score-mid"
                    verdict = "Partial Match"
                else:
                    cls = "score-low"
                    verdict = "Needs Work"

                sc1, sc2, sc3 = st.columns([1, 1, 1])
                with sc2:
                    st.markdown(f"""
                    <div class="score-wrap">
                      <div class="score-circle {cls}">
                        {score}<small>/ 100</small>
                      </div>
                      <div style="font-size:.95rem;font-weight:600;color:#f5f3ee;">{verdict}</div>
                      <div style="font-size:.8rem;color:#8a8880;margin-top:3px;">Overall Match Score</div>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Skill breakdown ────────────────────────────────────────
                r1, r2 = st.columns(2, gap="large")

                with r1:
                    # Present skills
                    present = result.get("matched_skills", [])
                    tags_html = "".join(f'<span class="tag tag-present">✓ {s}</span>' for s in present) or "<span style='color:#555'>None identified</span>"
                    st.markdown(f"""
                    <div class="card">
                      <h3>✅ Matching Skills</h3>
                      <div class="tags">{tags_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Category scores
                    cats = result.get("category_scores", {})
                    if cats:
                        bars_html = ""
                        for cat, pct in cats.items():
                            color = "#6ee7b7" if pct >= 70 else ("#fbbf24" if pct >= 40 else "#f87171")
                            bars_html += f"""
                            <div class="progress-wrap">
                              <div class="progress-label"><span>{cat}</span><span>{pct}%</span></div>
                              <div class="progress-bar-bg">
                                <div class="progress-bar-fill" style="width:{pct}%;background:{color};"></div>
                              </div>
                            </div>"""
                        st.markdown(f'<div class="card"><h3>📊 Category Breakdown</h3>{bars_html}</div>', unsafe_allow_html=True)

                with r2:
                    # Missing skills
                    missing = result.get("missing_skills", [])
                    tags_html2 = "".join(f'<span class="tag tag-missing">✗ {s}</span>' for s in missing) or "<span style='color:#555'>None — great job!</span>"
                    st.markdown(f"""
                    <div class="card">
                      <h3>🚫 Missing Skills</h3>
                      <div class="tags">{tags_html2}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Suggestions
                    suggestions = result.get("suggestions", [])
                    items_html = "".join(
                        f'<div class="item"><span class="item-icon">→</span><span>{s}</span></div>'
                        for s in suggestions
                    )
                    st.markdown(f'<div class="card"><h3>💡 Improvement Suggestions</h3>{items_html}</div>', unsafe_allow_html=True)

                # ── Strengths & Summary ────────────────────────────────────
                s1, s2 = st.columns(2, gap="large")

                with s1:
                    strengths = result.get("strengths", [])
                    items_html = "".join(
                        f'<div class="item"><span class="item-icon" style="color:#6ee7b7">✦</span><span>{s}</span></div>'
                        for s in strengths
                    )
                    st.markdown(f'<div class="card"><h3>⭐ Key Strengths</h3>{items_html}</div>', unsafe_allow_html=True)

                with s2:
                    summary = result.get("summary", "")
                    st.markdown(f'<div class="card"><h3>📝 Summary</h3><p style="color:#ccc8c0;font-size:.93rem;line-height:1.65;margin:0">{summary}</p></div>', unsafe_allow_html=True)
