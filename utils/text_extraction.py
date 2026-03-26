import os
import PyPDF2
import docx

def extract_text(file_path):
    """
    Detect file type and extract text
    """
    if file_path.endswith(".pdf"):
        return extract_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_docx(file_path)
    else:
        return ""


def extract_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print("PDF extraction error:", e)
    return text


def extract_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print("DOCX extraction error:", e)
    return text