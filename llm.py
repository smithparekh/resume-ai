from groq import Groq
import os
from dotenv import load_dotenv
from prompts import ANALYSIS_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_resume(resume_text, jd_text):

    prompt = ANALYSIS_PROMPT.format(
        resume=resume_text,
        jd=jd_text
    )

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content