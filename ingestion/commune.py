import pandas as pd
import re
from ingestion.pdf_loader import PDFLoader
from ingestion.normalizer import Normalizer

def get_communes_mapping(pdf_path):
    loader = PDFLoader(pdf_path)
    norm = Normalizer()
    
    mapping_data = []
    
    # Mots parasites à supprimer s'ils sont seuls ou en début de ligne
    noise = ["REGION", "PREFECTURES", "CIRCONSCRIPTION", "TOTAL", "PAGE", "NB BV", "S S A"]

    for page in loader.get_pages():
        # On extrait chaque mot avec sa position exacte (x, y)
        words = page.extract_words(horizontal_ltr=True)
        
        # 1. On identifie les CODES (les ancres) : 3 chiffres entre x=15 et x=60
        anchors = []
        for w in words:
            if 15 < w['x0'] < 60 and re.match(r'^\d{3}$', w['text']):
                anchors.append({
                    'code': w['text'],
                    'y_top': w['top'],
                    'y_bottom': w['bottom'],
                    'text_parts': []
                })
        
        if not anchors: continue

        # 2. On attribue chaque MOT de la zone centrale au code le plus proche
        for w in words:
            # On ne regarde que la zone "Circonscription" (entre x=60 et x=240)
            if 60 <= w['x0'] < 240:
                txt = w['text'].upper()
                if any(n in txt for n in noise) or len(txt) < 2:
                    continue
                
                # Trouver l'ancre la plus proche verticalement
                # (Une marge de 40 pixels couvre les noms multi-lignes)
                best_anchor = None
                min_dist = 50 
                
                for anchor in anchors:
                    # Si le mot est à peu près au niveau de l'ancre ou juste au-dessus/en-dessous
                    dist = abs(w['top'] - anchor['y_top'])
                    if dist < min_dist:
                        min_dist = dist
                        best_anchor = anchor
                
                if best_anchor:
                    best_anchor['text_parts'].append(w['text'])

        # 3. On compile les résultats de la page
        for a in anchors:
            full_name = " ".join(a['text_parts']).strip()
            # Nettoyage final des résidus de partis et ponctuation traînante
            full_name = re.sub(r"\b(RHDP|PDCI|FPI|ADCI|RDA|INDEPENDANT)\b", "", full_name, flags=re.IGNORECASE)
            full_name = re.sub(r'[,.\s-]+$', '', full_name).strip()
            
            if full_name:
                mapping_data.append({
                    "code_circo": a['code'],
                    "commune_complete": norm.simplify_text(full_name).upper()
                })

    df = pd.DataFrame(mapping_data)
    return df.drop_duplicates(subset=['code_circo']).sort_values('code_circo').reset_index(drop=True)