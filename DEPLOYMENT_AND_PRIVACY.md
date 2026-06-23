# Deployment and Privacy Notes

## Local Data

The app stores candidate and application data on the same machine running Streamlit.

- Candidate profile: `data/profile.json`
- Job tracker records: `data/jobs.json`
- Local environment variables: `.env`

Do not commit `data/` or `.env`. The current `.gitignore` excludes local data and environment files.

## AI Data Sharing

AI features send the following text to the Groq API:

- Resume text extracted from the uploaded PDF.
- Candidate profile context.
- Job descriptions.
- Saved job descriptions used during batch analysis.

Generated resume drafts and cover letters should be reviewed before use. The prompts instruct the model not to invent experience, employers, degrees, certifications, metrics, or projects, but the user remains responsible for checking the final material.

## Local Setup

Use a virtual environment and install dependencies from `requirements.txt`.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set the Groq API key in `.env`.

```bash
GROQ_API_KEY=your_groq_api_key_here
```

Optionally set a local access code if the Streamlit app will be shared on a network.

```bash
APP_ACCESS_CODE=choose-a-private-code
```

Enable user-scoped workspaces for a lightweight hosted-mode setup.

```bash
APP_MULTI_USER_MODE=true
```

When multi-user mode is enabled, the app asks for a workspace ID and stores data under `data/users/<workspace-id>/`.

Run the app locally.

```bash
streamlit run app.py
```

## Hosted Deployment Checklist

Before hosting this app for real users:

- Add authentication and user-specific data storage.
- Move local JSON storage to a database with backups.
- Store API keys in the hosting provider's secret manager.
- Add HTTPS, access logs, and error monitoring.
- Add a privacy notice that explains local storage, LLM API sharing, and retention.
- Add rate limiting for URL imports and AI calls.
- Confirm that job URL fetching complies with the target site's terms.

For a single-user local deployment, the existing local JSON storage and `.env` configuration are acceptable for MVP use.

## Optional OCR Setup

The default parser handles text-based PDFs. For scanned image-only PDFs, enable the OCR checkbox in the app after installing optional OCR tooling.

```bash
pip install pdf2image pytesseract
```

OCR also requires system tools:

- Tesseract OCR.
- Poppler, used by `pdf2image` to render PDF pages.

On macOS with Homebrew:

```bash
brew install tesseract poppler
```

## Optional Browser Import Setup

The default URL importer uses static HTML. For job boards that render descriptions with JavaScript, enable the browser rendering checkbox after installing Playwright.

```bash
pip install playwright
playwright install chromium
```

Browser rendering is useful for JavaScript-heavy pages, but some sites still block automated access or require login. In those cases, use the manual job form and paste the job description.
