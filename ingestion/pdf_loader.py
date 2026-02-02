import pdfplumber

class PDFLoader:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_pages(self):
        with pdfplumber.open(self.filepath) as pdf:
            for page in pdf.pages:
                yield page