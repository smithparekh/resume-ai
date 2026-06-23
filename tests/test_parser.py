import unittest
from unittest.mock import Mock, patch

from parser import ResumeParseError, extract_text_from_pdf


class ParserTest(unittest.TestCase):
    @patch("parser._open_pdf")
    def test_extract_text_from_pdf_joins_page_text(self, mock_open_pdf):
        page_one = Mock()
        page_one.extract_text.return_value = "Page one"
        page_two = Mock()
        page_two.extract_text.return_value = "Page two"
        pdf = Mock()
        pdf.pages = [page_one, page_two]
        mock_open_pdf.return_value.__enter__.return_value = pdf

        text = extract_text_from_pdf(Mock())

        self.assertEqual(text, "Page one\n\nPage two")

    @patch("parser._open_pdf")
    def test_extract_text_from_pdf_raises_for_empty_extraction(self, mock_open_pdf):
        page = Mock()
        page.extract_text.return_value = None
        pdf = Mock()
        pdf.pages = [page]
        mock_open_pdf.return_value.__enter__.return_value = pdf

        with self.assertRaises(ResumeParseError) as error:
            extract_text_from_pdf(Mock())

        self.assertIn("Could not extract readable text", str(error.exception))

    @patch("parser._extract_text_with_ocr", return_value="OCR text")
    @patch("parser._open_pdf")
    def test_extract_text_from_pdf_uses_ocr_when_enabled(self, mock_open_pdf, _mock_ocr):
        page = Mock()
        page.extract_text.return_value = None
        pdf = Mock()
        pdf.pages = [page]
        mock_open_pdf.return_value.__enter__.return_value = pdf

        text = extract_text_from_pdf(Mock(), enable_ocr=True)

        self.assertEqual(text, "OCR text")

    @patch("parser._open_pdf")
    def test_extract_text_from_pdf_raises_for_pdf_without_pages(self, mock_open_pdf):
        pdf = Mock()
        pdf.pages = []
        mock_open_pdf.return_value.__enter__.return_value = pdf

        with self.assertRaises(ResumeParseError) as error:
            extract_text_from_pdf(Mock())

        self.assertIn("does not contain any pages", str(error.exception))


if __name__ == "__main__":
    unittest.main()
