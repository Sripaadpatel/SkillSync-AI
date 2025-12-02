import os
import re
from pypdf import PdfReader

class ResumeParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    
    
    def _clean_text(self, text):
        """
        Internal method to clean extracted text.
        
        :param text: Raw text extracted from PDF
        :return: Cleaned text
        """
        # Replace multiple newlines/tabs with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove weird characters but keep basic punctuation
        # (This regex allows letters, numbers, standard punctuation, and @ for emails)
        # You can adjust this if you need to support more symbols.
        text = re.sub(r'[^\w\s.,@%()-]', '', text)

        return text.strip()
    
    def extract_text(self):
        """
        Docstring for extract_text
        
        :param self: Description
        """
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file '{self.pdf_path}' not found.")

        print(f"Extracting text from PDF: {self.pdf_path}")
        reader = PdfReader(self.pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        if not text:
            raise ValueError("No text found in the PDF document.")
        
        # Clean up the text
        text = re.sub(r'\s+', ' ', text).strip()
        return self._clean_text(text)
    
    def extract_email(self, text):
        """
        Extract email address from the text.
        
        :param text: Text to search for email
        :return: Extracted email or None
        """
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "Unknown User"
    
# --- Testing Block (Run this file directly to test) ---
if __name__ == "__main__":
    # Create a dummy PDF for testing if one doesn't exist
    # (In your real usage, you will pass the path to the uploaded PDF)
    try:
        parser = ResumeParser("sample_resume.pdf")
        print("ℹ️  To test, place a 'sample_resume.pdf' in this folder.")
        
        # Example usage:
        text = parser.extract_text()
        text = parser._clean_text(text)
        print(f"✅ Extracted {(text)} characters.")
        print(f"👤 Detected User: {parser.extract_email(text)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")  