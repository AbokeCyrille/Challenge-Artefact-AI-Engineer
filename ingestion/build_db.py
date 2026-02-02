import pandas as pd
import re
from ingestion.pdf_loader import PDFLoader
from ingestion.table_extractor import TableExtractor
from ingestion.cleaner import DataCleaner
from ingestion.normalizer import Normalizer
from ingestion.commune import get_communes_mapping
import duckdb
import os

def run_ingestion(pdf_path):
    loader = PDFLoader(pdf_path)
    extractor = TableExtractor(x_tolerance=12) 
    cleaner = DataCleaner()
    norm = Normalizer()
    
    all_final_data = []
    orphans = [] 
    
    # On initialise le contexte avec TOUTES les colonnes de nos données
    current_ctx = {
        "region": "AGNEBY-TIASSA",
        "code_circo": None, "commune": None,
        "nb_bv": 0, "inscrits": 0, "votants": 0, 
        "taux_part": None, "bull_nuls": 0, "suf_exprimes": 0,
        "bull_blancs_nom": 0, "bull_blancs_pct": None
    }

    for page in loader.get_pages():
        rows = extractor.extract(page) 
        
        for row in rows:
            cells = [c.strip() for c in row if c and c.strip()]
            if len(cells) < 3: continue 
            
            line_str = " ".join(cells).upper()

            # --- 1. FILTRE DE SÉCURITÉ ---
            if any(kw in line_str for kw in ["NB BV", "CIRCONSCRIPTION", "TOTAL", "8 597 092"]):
                continue

            # --- 2. DÉTECTION DE LA GRANDE LIGNE (COMMUNE + STATS) ---
            match_code = re.search(r"\b(\d{3})\b", line_str)
            # On garde les pourcentages pour le taux de participation et les blancs
            nums_with_pct = [c for c in cells if re.search(r'\d', c)]
            
            if match_code and len(nums_with_pct) >= 7:
                code = match_code.group(1)
                
                commune_parts = []
                for c in cells:
                    if code in c:
                        part = c.split(code)[0].strip()
                        if part: commune_parts.append(part)
                        break
                    commune_parts.append(c)
                
                commune_raw = " ".join(commune_parts).strip()

                # On mappe les colonnes selon l'ordre visuel de l'image
                # [CODE, NB_BV, INSCRITS, VOTANTS, TAUX, NULS, EXPRIMES, B_BLANCS, B_BLANCS_%]
                current_ctx.update({
                    "code_circo": code,
                    "commune": norm.simplify_text(commune_raw) if commune_raw else "COMMUNE " + code,
                    "nb_bv": cleaner.clean_numeric(nums_with_pct[1]),
                    "inscrits": cleaner.clean_numeric(nums_with_pct[2]),
                    "votants": cleaner.clean_numeric(nums_with_pct[3]),
                    "taux_part": nums_with_pct[4],
                    "bull_nuls": cleaner.clean_numeric(nums_with_pct[5]),
                    "suf_exprimes": cleaner.clean_numeric(nums_with_pct[6]),
                    "bull_blancs_nom": cleaner.clean_numeric(nums_with_pct[7]) if len(nums_with_pct) > 7 else 0,
                    "bull_blancs_pct": nums_with_pct[8] if len(nums_with_pct) > 8 else None
                })

                for orphan in orphans:
                    all_final_data.append({**current_ctx, **orphan})
                orphans = []
                continue

            # --- 3. DÉTECTION DES CANDIDATS ---
            if any("%" in c for c in cells[-3:]):
                is_elu = 1 if "ELU" in line_str else 0
                try:
                    pct_idx = next(i for i, c in enumerate(cells) if "%" in c)
                    v_idx = pct_idx - 1 
                    
                    left_elements = cells[:v_idx]
                    if not left_elements: continue

                    cand_info = {
                        "parti": norm.simplify_text(left_elements[0]),
                        "candidat": norm.simplify_text(" ".join(left_elements[1:])),
                        "voix": cleaner.clean_numeric(cells[v_idx]),
                        "voix_pct": cells[pct_idx],
                        "elu": is_elu
                    }

                    if current_ctx["code_circo"]:
                        all_final_data.append({**current_ctx, **cand_info})
                    else:
                        orphans.append(cand_info)
                except StopIteration:
                    continue

    return pd.DataFrame(all_final_data)


#Netoyage et traitement

# Dictionnaire de mapping code_circo -> région
def get_region_mapping():
    mapping = {}
    
    # Agneby-Tiassa (001 à 008)
    for i in range(1, 9): mapping[f"{i:03}"] = "AGNEBY-TIASSA"
    
    # Bafing (009 à 013)
    for i in range(9, 14): mapping[f"{i:03}"] = "BAFING"
    
    # Bagoué (014 à 018)
    for i in range(14, 19): mapping[f"{i:03}"] = "BAGOUÉ"
    
    # Bélier (019 à 022)
    for i in range(19, 23): mapping[f"{i:03}"] = "BELIER"
    
    # Béré (023 à 027)
    for i in range(23, 28): mapping[f"{i:03}"] = "BERE"
    
    # Bounkani (028 à 035) 
    for i in range(28, 36): mapping[f"{i:03}"] = "BOUNKANI"
    
    # Cavally (036 à 037) 
    for i in range(36, 38): mapping[f"{i:03}"] = "CAVALLY"
    
    # District Autonome d'Abidjan (038 à 050) 
    for i in range(38, 51): mapping[f"{i:03}"] = "DISTRICT AUTONOME D'ABIDJAN"
    
    # Folon (054 à 061) 
    for i in range(54, 62): mapping[f"{i:03}"] = "FOLON"
    
    # Gbêkê (062 à 066) 
    for i in range(62, 67): mapping[f"{i:03}"] = "GBEKE"
    
    # Gôh (069 à 073) 
    for i in range(69, 74): mapping[f"{i:03}"] = "GOH"
    
    # Gontougo (074 à 083)
    for i in range(74, 84): mapping[f"{i:03}"] = "GONTOUGO"
    
    # Kabadougou (116 à 123) 
    for i in range(116, 124): mapping[f"{i:03}"] = "KABADOUGOU"
    
    # Lôh-Djiboua (124 à 128)
    for i in range(124, 129): mapping[f"{i:03}"] = "LOH-DJIBOUA"
    
    # Marahoué (133 à 140)
    for i in range(133, 141): mapping[f"{i:03}"] = "MARAHOUE"

    for i in [154, 157, 158, 161, 162]: mapping[f"{i:03}"] = "MORONOU"
    #NAWA (148 à 153)
    for i in range(148, 154): mapping[f"{i:03}"] = "NAWA"
    #N'ZI
    for i in [155, 156, 159, 160]: mapping[f"{i:03}"] = "N'ZI"
    
    # Pôrô (163 à 174) 
    for i in range(163, 175): mapping[f"{i:03}"] = "PORO"
    
    # San-Pédro (175 à 177) 
    for i in range(175, 178): mapping[f"{i:03}"] = "SAN-PEDRO"
    
    # Sud-Comoé (178 à 184) 
    for i in range(178, 185): mapping[f"{i:03}"] = "SUD-COMOE"
    # TCHOLOGO (185 à 189) 
    for i in range(185, 190): mapping[f"{i:03}"] = "TCHOLOGO"
    # TONKPI (190 à 199) 
    for i in range(190, 200): mapping[f"{i:03}"] = "TONKPI"
    # WORODOUGOU (200 à 205) 
    for i in range(200, 206): mapping[f"{i:03}"] = "WORODOUGOU"
    
    return mapping


#Correction des régions selon le code_circo
def apply_correction(df):
    region_map = get_region_mapping()
    
    # On force le code_circo en format 001, 002...
    df['code_circo'] = df['code_circo'].astype(str).str.zfill(3)
    
    # On remplace la région par la valeur du dictionnaire
    df['region'] = df['code_circo'].map(region_map).fillna(df['region'])
    
    return df


def build_and_clean_db():
    pdf_path = "data/raw/EDAN_2025_RESULTAT_NATIONAL_DETAILS.pdf"
    # db_path = "data/db/elections.duckdb"

    #  Extraction des deux datasets
    print("Extraction des données en cours...")
    extractor_commune = get_communes_mapping(pdf_path) # [code_circo, commune_complete]
    extractor_df = run_ingestion(pdf_path)             # [code_circo, commune, candidats, voix, etc.]

    #  Mise à jour de la colonne 'commune' 
    # On transforme le référentiel en dictionnaire pour un mapping ultra-rapide
    mapping_dict = extractor_commune.set_index('code_circo')['commune_complete'].to_dict()
    extractor_df['commune'] = extractor_df['code_circo'].map(mapping_dict)

    # Nettoyage pour la BD
    # Suppression des lignes vides, conversion des types et gestion des noms de colonnes
    df_supprLigne = extractor_df.dropna(subset=['code_circo', 'commune'])
    
    # Nettoyage des noms de colonnes (pas d'espaces ou de points pour SQL)
    df_supprLigne.columns = [c.lower().replace(" ", "_").replace(".", "") for c in df_supprLigne.columns]
    df_final = apply_correction(df_supprLigne)
    # J'identifie les colonnes qui contiennent des pourcentages
    cols_pct = ['taux_part', 'bull_blancs_pct', 'voix_pct']
    for col in cols_pct:
        # On convertit en string, on retire le %, on change la virgule en point
        df_final[col] = df_final[col].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False)
    
        # On convertit enfin en nombre (float)
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

    # 4. Stockage CSV (Intermédiaire)
    os.makedirs("data/processed", exist_ok=True)
    df_final.to_csv("data/processed/results_clean_003.csv", index=False, encoding='utf-8-sig')
    return df_final

#Insertion des données dans la base de données
def setup_and_insert(df_to_inject, db_path="data/db/elections.duckdb"):
    #Création de la BD
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    # Connexion à la base de données (crée le fichier s'il n'existe pas)
    con = duckdb.connect(db_path)

    # 2. Création de la table avec les types de données explicites
    con.execute("""
        CREATE OR REPLACE TABLE resultats (
            region VARCHAR,
            code_circo VARCHAR,
            commune VARCHAR,
            nb_bv INTEGER,
            inscrits INTEGER,
            votants INTEGER,
            taux_part FLOAT,
            bull_nuls INTEGER,
            suf_exprimes INTEGER,
            bull_blancs_nom INTEGER,
            bull_blancs_pct FLOAT,
            parti VARCHAR,
            candidat VARCHAR,
            voix INTEGER,
            voix_pct FLOAT,
            elu INTEGER
        );
    """)

    # 3. Injection des données du DataFrame Pandas directement dans la table
    con.execute("INSERT INTO resultats SELECT * FROM df_to_inject")

    # Vérification rapide
    count = con.execute("SELECT COUNT(*) FROM resultats").fetchone()[0]
    print(f"Succès ! {count} lignes injectées dans DuckDB.")
    #Premier element de la bd
    print(con.execute("SELECT * FROM resultats LIMIT 1").df())
    
    con.close()
df = build_and_clean_db()
# Appel de la fonction
setup_and_insert(df)