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