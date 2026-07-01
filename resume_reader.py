from pypdf import PdfReader

def load_resume():

    reader = PdfReader("Resume.pdf")

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            resume_text += text

    return resume_text