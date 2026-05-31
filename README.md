# Resume AI Analyzer

> Instant AI-powered resume feedback using Groq LLaMA-3.3-70b — fast, free, and brutally honest

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-orange?style=flat)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)

---

## What It Does

Upload your resume PDF and get structured AI feedback in seconds:

- **Strengths** — what's working well
- **Weaknesses** — what needs improvement
- **Missing keywords** — skills or experience that are absent
- **Actionable suggestions** — specific rewrites to improve impact

Powered by Groq's ultra-fast inference (LLaMA-3.3-70b) — results in under 3 seconds.

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq API (LLaMA-3.3-70b) |
| PDF Parsing | PyPDF2 |
| Frontend | Streamlit |
| Prompt Design | Custom structured prompts |

---

## Project Structure

```
resume-ai/
├── app.py          # Streamlit UI entry point
├── llm.py          # Groq API client, model config
├── parser.py       # PDF text extraction
├── prompts.py      # Prompt templates
└── requirements.txt
```

---

## Setup

```bash
git clone https://github.com/smithparekh/resume-ai
cd resume-ai
pip install -r requirements.txt

# Add your Groq API key (free at console.groq.com)
export GROQ_API_KEY=your_key_here

streamlit run app.py
```

---

## Key Features

- Clean modular code — 4 separate modules, under 150 lines total
- Temperature 0.2 for consistent, reproducible output
- Upload any PDF resume — no formatting requirements
- Free to run (Groq API has a generous free tier)
