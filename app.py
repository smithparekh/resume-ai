import json
import streamlit as st
from parser import extract_text_from_pdf
from llm import analyze_resume

st.title("AI Resume + JD Analyzer")

resume_file = st.file_uploader("Upload Resume (PDF)")
jd_text = st.text_area("Paste Job Description")

if resume_file and jd_text:
    resume_text = extract_text_from_pdf(resume_file)

    if st.button("Analyze Resume"):
        with st.spinner("Analyzing with AI..."):
            result = analyze_resume(resume_text, jd_text)

        try:
            data = json.loads(result)

            st.metric("Resume Score", data["resume_score"])
            st.metric("JD Match %", data["jd_match_percentage"])

            st.subheader("Missing Skills")
            for skill in data["missing_skills"]:
                st.write("-", skill)

            st.subheader("Keyword Gaps")
            for k in data["keyword_gaps"]:
                st.write("-", k)

            st.subheader("Improvement Suggestions")
            for s in data["improvement_suggestions"]:
                st.write("-", s)

        except json.JSONDecodeError:
            st.subheader("AI Analysis")
            st.write(result)
