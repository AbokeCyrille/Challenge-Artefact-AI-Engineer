ENTITY_REGISTRY = {

    "region": {
    "type": "value",
    "table": "resultats",
    "column": "region",
    "fuzzy": True,
    "aliases": {
        "agneby tiassa": "AGNEBY-TIASSA",
        "agnéby-tiassa": "AGNEBY-TIASSA"
    },
    
    },

    "code_circo": {
        "type": "value",
        "table": "resultats",
        "column": "code_circo",
        "fuzzy": True,
        "aliases": {
            "circonscription": None
        }
    },

    "commune": {
        "type": "value",
        "table": "resultats",
        "column": "commune",
        "fuzzy": True
    },

    "parti": {
        "type": "value",
        "table": "resultats",
        "column": "parti",
        "fuzzy": True,
        "aliases": {
            "rhdp": "RHDP",
            "R.H.D.P": "RHDP",
            "pdci": "PDCI-RDA",
            "pdcirda": "PDCI-RDA"
        }
    },

    "candidat": {
        "type": "value",
        "table": "resultats",
        "column": "candidat",
        "fuzzy": True
    },

    "elu": {
        "type": "boolean"
    },
    # ---------- Metrics ----------
    "nb_bv": {"type": "metric"},
    "inscrits": {"type": "metric"},
    "votants": {"type": "metric"},
    "taux_part": {"type": "metric"},
    "bull_nuls": {"type": "metric"},
    "suf_exprimes": {"type": "metric"},
    "bull_blancs_nom": {"type": "metric"},
    "bull_blancs_pct": {"type": "metric"},
    "voix": {"type": "metric"},
    "voix_pct": {"type": "metric"}
}

