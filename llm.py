import os
from prompts import ANALYSIS_PROMPT, COVER_LETTER_PROMPT, TAILORING_PROMPT

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"
MAX_INPUT_CHARS = 12000


class LLMError(Exception):
    pass


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise LLMError("GROQ_API_KEY is missing. Add it to your .env file before using AI features.")

    try:
        from groq import Groq
    except ImportError as error:
        raise LLMError("The groq package is not installed. Run: pip install -r requirements.txt") from error

    return Groq(api_key=api_key)


def _chat_completion(prompt: str) -> str:
    try:
        response = _get_client().chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
    except Exception as error:
        raise LLMError(f"AI request failed: {error}") from error

    return response.choices[0].message.content


def analyze_resume(resume_text, jd_text):

    prompt = ANALYSIS_PROMPT.format(
        resume=_limit_text(resume_text),
        jd=_limit_text(jd_text)
    )

    return _chat_completion(prompt)


def tailor_resume(resume_text, jd_text, profile_context):
    prompt = TAILORING_PROMPT.format(
        profile=_limit_text(profile_context),
        resume=_limit_text(resume_text),
        jd=_limit_text(jd_text),
    )

    return _chat_completion(prompt)


def generate_cover_letter(resume_text, jd_text, profile_context):
    prompt = COVER_LETTER_PROMPT.format(
        profile=_limit_text(profile_context),
        resume=_limit_text(resume_text),
        jd=_limit_text(jd_text),
    )

    return _chat_completion(prompt)


def _limit_text(value: str, max_chars: int = MAX_INPUT_CHARS) -> str:
    text = value or ""

    if len(text) <= max_chars:
        return text

    return f"{text[:max_chars]}\n\n[Content truncated to {max_chars} characters.]"
