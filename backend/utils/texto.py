import unicodedata

def normalizar_nome(s: str) -> str:
    if not isinstance(s, str):
        return ""
    return "".join(c for c in unicodedata.normalize("NFKD", s).lower() if not unicodedata.combining(c)).strip()
