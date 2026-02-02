INTENTS = [

# ======================================================
# GLOBAL / NATIONAL
# ======================================================

{
    "id": "NATIONAL_GLOBAL_RESULTS",
    "examples": [
        "Résultats globaux nationaux",
        "Quelle est la statistique total observée dans cette élections",
        "National election results",
        "Overall election results"
    ],
    "required_params": [],
    "sql": """
        SELECT 
            SUM(nb_bv) AS total_nb_bv,
            (SELECT COUNT(DISTINCT candidat) FROM resultats) AS total_nb_candidats,
            SUM(inscrits) AS total_inscrits,
            SUM(votants) AS total_votants,
            (SUM(votants) * 100.0 / SUM(inscrits)) AS taux_part_global,
            SUM(bull_nuls) AS total_bull_nuls,
            SUM(suf_exprimes) AS total_suf_exprimes,
            SUM(bull_blancs_nom) AS total_bull_blancs_nom,
            (SUM(bull_blancs_nom) * 100.0 / SUM(votants)) AS bull_blancs_pct_global
        FROM (
             -- On isole chaque circonscription une seule fois
             SELECT 
                code_circo, 
                MAX(nb_bv) as nb_bv, 
                MAX(inscrits) as inscrits, 
                MAX(votants) as votants, 
                MAX(bull_nuls) as bull_nuls, 
                MAX(suf_exprimes) as suf_exprimes,
                MAX(bull_blancs_nom) as bull_blancs_nom
             FROM resultats
             GROUP BY code_circo
        )
    """,
    "chart_capable": ["bar"]
},
# ======================================================
# REGIONS
# ======================================================

{
    "id": "LIST_REGIONS",
    "examples": [
        "Quelles sont les régions présentes",
        "quel est la liste des région présentes dans cette élection",
        "List of regions",
        "Available regions"
    ],
    "required_params": [],
    "sql": """
        SELECT DISTINCT region
        FROM resultats
        ORDER BY region
    """,
    "chart_capable": []
},

{
    "id": "REGION_GLOBAL_RESULTS",
    "examples": [
        "Résultats globaux pour la région AGNEBY-TIASSA",
        "Results for AGNEBY-TIASSA region"
    ],
    "required_params": ["region"],
    "sql": """
        SELECT
            region,
            SUM(inscrits) AS inscrits,
            SUM(votants) AS votants,
            AVG(taux_part) AS taux_part,
            SUM(bull_nuls) AS bull_nuls,
            SUM(suf_exprimes) AS suf_exprimes
        FROM resultats
        WHERE region = :region
        GROUP BY region
    """,
    "chart_capable": ["bar"]
},

{
    "id": "REGION_TURNOUT_RANKING",
    "examples": [
        "Fait le diagramme du taux de participation par région",
        "Participation rate by region"
    ],
    "required_params": [],
    "sql": """
        SELECT region, AVG(taux_part) AS taux_part
        FROM resultats
        GROUP BY region
        ORDER BY taux_part DESC
        LIMIT 50
    """,
    "chart_capable": ["bar"]
},

{
    "id": "ELECTED_BY_REGION",
    "examples": [
        "Candidats élus dans la région X",
        "Elected candidates in region X"
    ],
    "required_params": ["region"],
    "sql": """
        SELECT candidat, parti, code_circo
        FROM resultats
        WHERE region = :region AND elu = 1
        ORDER BY code_circo
    """,
    "chart_capable": []
},

# ======================================================
# CIRCONSCRIPTIONS
# ======================================================

{
    "id": "CIRCO_BY_REGION",
    "examples": [
        "Circonscriptions de la région X",
        "Districts in region X"
    ],
    "required_params": ["region"],
    "sql": """
        SELECT DISTINCT code_circo
        FROM resultats
        WHERE region = :region
        ORDER BY code_circo
    """,
    "chart_capable": []
},

{
    "id": "CIRCO_RESULTS",
    "examples": [
        "Résultats de la circonscription 001",
        "Results of district 001"
    ],
    "required_params": ["code_circo"],
    "sql": """
        SELECT
            code_circo,
            SUM(inscrits) AS inscrits,
            SUM(votants) AS votants,
            AVG(taux_part) AS taux_part,
            SUM(bull_nuls) AS bull_nuls,
            SUM(suf_exprimes) AS suf_exprimes
        FROM resultats
        WHERE code_circo = :code_circo
        GROUP BY code_circo
    """,
    "chart_capable": ["bar"]
},

{
    "id": "WINNER_BY_CIRCO",
    "examples": [
        "Qui a gagné dans la circonscription 001",
        "Winner in district 001"
    ],
    "required_params": ["code_circo"],
    "sql": """
        SELECT candidat, parti, voix_pct
        FROM resultats
        WHERE code_circo = LPAD(:code_circo, 3, '0')
        ORDER BY voix_pct DESC
        LIMIT 1
    """,
    "chart_capable": []
},

# ======================================================
# COMMUNES
# ======================================================

{
    "id": "COMMUNES_BY_CIRCO",
    "examples": [
        "Communes de la circonscription 001",
        "Municipalities in district 001"
    ],
    "required_params": ["code_circo"],
    "sql": """
        SELECT DISTINCT commune
        FROM resultats
        WHERE code_circo = :code_circo
        ORDER BY commune
    """,
    "chart_capable": []
},

{
    "id": "COMMUNE_RESULTS",
    "examples": [
        "Résultats pour la commune ABOUDE",
        "Results for ABOUDE municipality"
    ],
    "required_params": ["commune"],
    "sql": """
        SELECT candidat, parti, voix, voix_pct
        FROM resultats
        WHERE commune = :commune
        ORDER BY voix_pct DESC
    """,
    "chart_capable": ["bar"]
},

# ======================================================
# PARTIS
# ======================================================

{
    "id": "LIST_PARTIES",
    "examples": [
        "Liste des partis politiques présents dans cette élection",
        "List political parties in this election"
    ],
    "required_params": [],
    "sql": """
        SELECT DISTINCT parti
        FROM resultats
        ORDER BY parti
    """,
    "chart_capable": []
},

{
  "id": "PARTY_OF_CANDIDATE",
  "examples": ["quel est le parti du candidat X",
               "what is the party of candidate X"],
  "required_params": ["candidat"],  
  "sql": """
    SELECT DISTINCT parti
    FROM resultats
    WHERE UPPER(candidat) LIKE UPPER(:candidat)
  """,
  "chart_capable": []
},


{
    "id": "CANDIDATES_BY_PARTY",
    "examples": [
        "Liste des candidats du RHDP",
        "Candidats du parti RHDP",
        "Candidates from RHDP"
    ],
    "sql": """
        SELECT DISTINCT candidat
        FROM resultats
        WHERE parti = :parti
        ORDER BY candidat
        LIMIT 100
    """,
    "chart_capable": []
},


{
    "id": "SEATS_BY_PARTY",
    "examples": [
        "Répartition des sièges remportés par parti",
        "Diagramme circulaire de la répartition des sièges remportés par parti",
        "Seats won by party",
        "Diagram of seats won by party"
    ],
    "required_params": [],
    "sql": """
        SELECT parti, COUNT(*) AS seats
        FROM resultats
        WHERE elu = 1
        GROUP BY parti
        ORDER BY seats DESC
    """,
    "chart_capable": ["pie"]
},

{
    "id": "SEATS_WON_PARTY",
    "examples": [
        "Quel est le nombre de sièges remportés par le parti PDCI-RDA",
        "Number of seats won by party RHDP"
    ],
    "required_params": ["parti"],
    "sql": """
        SELECT parti, COUNT(*) AS seats
        FROM resultats
        WHERE elu = 1 AND parti = :parti
        GROUP BY parti
    """,
    "chart_capable": []
},

{
    "id": "PARTY_NATIONAL_SCORE",
    "examples": [
        "Score national du parti RHDP",
        "Quelle est le total de vote pour le parti RHDP",
        "Total votes for party RHDP"
    ],
    "required_params": ["parti"],
    "sql": """
        SELECT parti, SUM(voix) AS total_votes
        FROM resultats
        WHERE parti = :parti
        GROUP BY parti
    """,
    "chart_capable": ["bar"]
},

# ======================================================
# FILTRES NUMÉRIQUES (GÉNÉRALISTES)
# ======================================================

{
    "id": "FILTER_BY_PERCENT_RANGE",
    "examples": [
        "Candidats avec un pourcentage de voix entre 30% et 50%",
        "Candidates with more than 40% of votes",
        "Candidats avec au moins 25% de voix"
    ],
    "required_params": ["min_pct", "max_pct"],
    "sql": """
        SELECT candidat, code_circo, voix_pct
        FROM resultats
        WHERE voix_pct BETWEEN :min_pct AND :max_pct
        ORDER BY voix_pct DESC
    """,
    "chart_capable": ["bar"]
},

# ======================================================
# CORRÉLATIONS
# ======================================================

{
    "id": "TURNOUT_VS_NULLS",
    "examples": [
        "Corrélation participation et bulletins nuls",
        "Turnout vs null ballots correlation"
    ],
    "required_params": [],
    "sql": """
        SELECT taux_part, bull_nuls
        FROM resultats
        LIMIT 500
    """,
    "chart_capable": ["scatter"]
}

]
