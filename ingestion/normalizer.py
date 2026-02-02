class Normalizer:
    @staticmethod
    def simplify_text(text):
        if not text: return ""
        return " ".join(str(text).split()).upper()