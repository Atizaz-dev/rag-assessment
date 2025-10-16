import PyPDF2
import docx
import markdown
from typing import Optional
import os

class FileProcessor:
    @staticmethod
    def process_file(file_path: str, filename: str) -> Optional[str]:
        """Process uploaded file and extract text content."""
        ext = os.path.splitext(filename)[1].lower()
        
        try:
            if ext == '.txt':
                return FileProcessor._process_txt(file_path)
            elif ext == '.pdf':
                return FileProcessor._process_pdf(file_path)
            elif ext == '.docx':
                return FileProcessor._process_docx(file_path)
            elif ext in ['.md', '.markdown']:
                return FileProcessor._process_markdown(file_path)
            else:
                return None
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
    
    @staticmethod
    def _process_txt(file_path: str) -> str:
        """Process plain text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _process_pdf(file_path: str) -> str:
        """Process PDF file."""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    @staticmethod
    def _process_docx(file_path: str) -> str:
        """Process DOCX file."""
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    
    @staticmethod
    def _process_markdown(file_path: str) -> str:
        """Process Markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
            html = markdown.markdown(md_text)
            return md_text
    
    @staticmethod
    def is_supported_file(filename: str) -> bool:
        """Check if file type is supported."""
        supported_extensions = ['.txt', '.pdf', '.docx', '.md', '.markdown']
        ext = os.path.splitext(filename)[1].lower()
        return ext in supported_extensions