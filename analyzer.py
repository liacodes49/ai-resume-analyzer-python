"""
analyzer.py — Resume extraction and AI analysis logic.
"""

import json
import re
import google.generativeai as genai
from pypdf import PdfReader
import io


# ─── PDF TEXT EXTRACTION ───────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    try:
        pdf_bytes = uploaded_file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            try:
                text = page.extract_text() or ""
                pages.append(text)
            except Exception:
                pages.append("")
        return "\n\n".join(pages)
    except Exception:
        return ""


# ─── AI ANALYSIS ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert technical recruiter and career coach.
Your task is to analyze a candidate's resume against a job description and return a
structured JSON evaluation. Be specific, honest, and actionable.

Always respond with ONLY valid JSON — no markdown, no preamble, no backticks."""

USER_TEMPLATE = """
Analyze the following resume against the job description and return JSON in EXACTLY this schema:

{{
  "match_score": <integer 0-100>,
  "matched_skills": [<list of skills/keywords found in BOTH resume and JD>],
  "missing_skills": [<list of important skills in JD but NOT in resume>],
  "category_scores": {{
    "Technical Skills": <0-100>,
    "Experience": <0-100>,
    "Education": <0-100>,
    "Soft Skills": <0-100>
  }},
  "strengths": [<3-5 specific strengths of this candidate for this role>],
  "suggestions": [<3-5 concrete, actionable improvement suggestions>],
  "summary": "<2-3 sentence overall assessment>"
}}

──────────────────────────────────────────
RESUME:
{resume}

──────────────────────────────────────────
JOB DESCRIPTION:
{job_description}
──────────────────────────────────────────

Return ONLY the JSON object. No markdown, no backticks, no explanation.
"""


def clean_json(raw: str) -> str:
    """Extract the JSON object from a response that may contain markdown or extra text."""
    # Remove markdown fences (```json ... ``` or ``` ... ```)
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw.strip())
    raw = raw.strip()
    # Extract the first { ... } block in case there's surrounding text
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return match.group(0)
    return raw


def analyze_resume(resume_text: str, job_description: str, api_key: str) -> dict:
    resume_text = resume_text[:8000]
    job_description = job_description[:4000]

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )

        response = model.generate_content(
            USER_TEMPLATE.format(
                resume=resume_text,
                job_description=job_description,
            ),
            generation_config=genai.GenerationConfig(max_output_tokens=8192),
        )

        raw = clean_json(response.text)
        print("RAW RESPONSE:", repr(response.text))
        data = json.loads(raw)

        data["match_score"] = max(0, min(100, int(data.get("match_score", 0))))
        for cat in data.get("category_scores", {}):
            data["category_scores"][cat] = max(
                0, min(100, int(data["category_scores"][cat]))
            )

        return data

    except json.JSONDecodeError as e:
        return {"error": f"Could not parse AI response as JSON: {e}"}
    except Exception as e:
        return {"error": str(e)}
