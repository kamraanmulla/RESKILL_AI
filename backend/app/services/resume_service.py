import io
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any
from .gemini_service import gemini_service

class ResumeService:
    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
        """Extract text from uploaded PDF, DOCX, or plain text bytes."""
        text = ""
        filename_lower = (filename or "").lower()

        if filename_lower.endswith(".pdf"):
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                for page in doc:
                    text += page.get_text() + "\n"
            except Exception:
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                        for page in pdf.pages:
                            extracted = page.extract_text()
                            if extracted:
                                text += extracted + "\n"
                except Exception:
                    text = file_bytes.decode("utf-8", errors="ignore")
        elif filename_lower.endswith(".docx"):
            # Robust zero-dependency extraction of .docx Word XML via standard library zipfile
            try:
                with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                    xml_content = z.read("word/document.xml")
                    tree = ET.fromstring(xml_content)
                    # Extract text content from all document XML elements
                    extracted_parts = []
                    for node in tree.iter():
                        if node.tag.endswith("t") and node.text:
                            extracted_parts.append(node.text)
                        elif node.tag.endswith("p"):
                            extracted_parts.append("\n")
                    text = "".join(extracted_parts)
            except Exception:
                text = file_bytes.decode("utf-8", errors="ignore")
        else:
            # Plain text / fallback
            text = file_bytes.decode("utf-8", errors="ignore")

        return text.strip()

    @classmethod
    def analyze_resume(cls, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        text = cls.extract_text_from_bytes(file_bytes, filename)
        if not text:
            return {
                "name": None,
                "email": None,
                "degree": None,
                "institution": None,
                "graduationYear": 2026,
                "skills": [],
                "projects": [],
                "experience": []
            }
        return gemini_service.parse_resume_text(text)

resume_service = ResumeService()
