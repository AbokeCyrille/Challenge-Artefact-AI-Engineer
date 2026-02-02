import re

class DataCleaner:
    @staticmethod
    def clean_numeric(value):
        if not value or str(value).strip().upper() == "NONE": return 0
        cleaned = re.sub(r'[^\d]', '', str(value))
        return int(cleaned) if cleaned else 0

    @staticmethod
    def clean_percentage(value):
        if not value: return "0,00%"
        return str(value).replace('.', ',').strip()