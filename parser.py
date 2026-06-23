class ResumeParseError(Exception):
    pass


def extract_text_from_pdf(file, enable_ocr: bool = False):
    text_parts = []

    try:
        with _open_pdf(file) as pdf:
            if not pdf.pages:
                raise ResumeParseError("This PDF does not contain any pages.")

            for page in pdf.pages:
                page_text = page.extract_text(layout=True)

                if page_text:
                    text_parts.append(page_text)
    except Exception as error:
        if isinstance(error, ResumeParseError):
            raise
        raise ResumeParseError(f"Could not read this PDF: {error}") from error

    text = "\n\n".join(text_parts).strip()

    if not text and enable_ocr:
        text = _extract_text_with_ocr(file).strip()

    if not text:
        raise ResumeParseError(
            "Could not extract readable text from this PDF. If it is scanned or image-based, enable OCR or export it as a text-based PDF and try again."
        )

    return text


def _open_pdf(file):
    import pdfplumber

    return pdfplumber.open(file)


def _extract_text_with_ocr(file) -> str:
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
    except ImportError as error:
        raise ResumeParseError(
            "OCR support requires optional packages. Install them with: pip install pdf2image pytesseract"
        ) from error

    try:
        file.seek(0)
        pdf_bytes = file.read()
        images = convert_from_bytes(pdf_bytes)
        return "\n\n".join(pytesseract.image_to_string(image) for image in images)
    except Exception as error:
        raise ResumeParseError(f"OCR failed for this PDF: {error}") from error
