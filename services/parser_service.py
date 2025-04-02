import PyPDF2
from docx import Document
import re
from typing import Dict, Optional

class ResumeParser:
    def __init__(self):
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    def parse_file(self, file_content: bytes, file_name: str) -> Dict:
        """Parse resume file and extract information"""
        if file_name.lower().endswith('.pdf'):
            return self._parse_pdf(file_content)
        elif file_name.lower().endswith(('.doc', '.docx')):
            return self._parse_docx(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_name}")
    
    def _parse_pdf(self, file_content: bytes) -> Dict:
        """Parse PDF file"""
        pdf_reader = PyPDF2.PdfReader(file_content)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return self._extract_information(text)
    
    def _parse_docx(self, file_content: bytes) -> Dict:
        """Parse DOCX file"""
        doc = Document(file_content)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return self._extract_information(text)
    
    def _extract_information(self, text: str) -> Dict:
        """Extract information from text"""
        emails = re.findall(self.email_pattern, text)
        email = emails[0] if emails else None
        
        # Split text into sections
        sections = text.split('\n\n')
        
        # Basic information extraction
        info = {
            'email': email,
            'raw_text': text,
            'sections': sections
        }
        
        return info
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        emails = re.findall(self.email_pattern, text)
        return emails[0] if emails else None 