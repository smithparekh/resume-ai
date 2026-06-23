ANALYSIS_PROMPT = """
You are an expert AI recruiter.

Compare the following RESUME and JOB DESCRIPTION.

Return the response strictly in JSON format.

Required JSON format:

{{
 "resume_score": number,
 "jd_match_percentage": number,
 "missing_skills": [],
 "keyword_gaps": [],
 "improvement_suggestions": []
}}

RESUME:
{resume}

JOB DESCRIPTION:
{jd}
"""


TAILORING_PROMPT = """
You are an expert resume strategist.

Create a complete, ready-to-use tailored resume draft for the candidate using
the RESUME, CANDIDATE PROFILE, and JOB DESCRIPTION below.

Rules:
- Do not invent experience, employers, degrees, certifications, or project outcomes.
- Keep the candidate's background truthful.
- Rewrite the resume content yourself. Do not tell the user what to replace,
  rewrite, add, or consider.
- Do not include placeholders, bracketed instructions, editing notes, or TODOs.
- Only include skills, tools, links, and achievements supported by the
  resume/profile.
- Target the wording to the job description's responsibilities, skills, and
  keywords where truthful.
- Return polished Markdown that the user can copy into a resume document.

Required sections:
1. Name and Contact
2. Targeted Professional Summary
3. Core Skills
4. Professional Experience
5. Projects
6. Education
7. Certifications

CANDIDATE PROFILE:
{profile}

RESUME:
{resume}

JOB DESCRIPTION:
{jd}
"""


COVER_LETTER_PROMPT = """
You are an expert career coach.

Write a complete, ready-to-send tailored cover letter using the CANDIDATE
PROFILE, RESUME, and JOB DESCRIPTION below.

Rules:
- Do not invent experience, employers, degrees, certifications, metrics, or projects.
- Keep it professional and direct.
- Use specific strengths that are supported by the resume/profile.
- Apply the candidate's background directly to this job's responsibilities and
  required skills.
- Do not include placeholders, bracketed instructions, editing notes, or TODOs.
- Keep it under 350 words.
- Return only the cover letter text.

CANDIDATE PROFILE:
{profile}

RESUME:
{resume}

JOB DESCRIPTION:
{jd}
"""
