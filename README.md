# Artefact AI Engineer Challenge — Chat avec les Données Électorales(ELECTION DES DEPUTES A L'ASSEMBLEE NATIONALE)
Contexte

Ce projet est une application d’analyse conversationnelle construite à partir d’un PDF officiel des résultats électoraux publié par la CEI (Commission Électorale Indépendante de Côte d’Ivoire).

L’objectif est de permettre à un utilisateur de dialoguer avec le jeu de données afin de :

Répondre à des questions factuelles, strictement basées sur le contenu du PDF

Calculer des agrégations, classements et statistiques

Générer des graphiques à la demande

Améliorer progressivement la robustesse, la sécurité et la readiness production

Le PDF est l’unique source de vérité.
Aucune information externe n’est utilisée.

Vue d’ensemble de la solution

La solution repose sur une architecture modulaire, déterministe et orientée production, couvrant les niveaux 1 à 4 du challenge.

1. Pipeline d’ingestion des données

Chargement du PDF officiel des résultats électoraux

Extraction des tableaux (gestion des en-têtes répétés, sauts de ligne, pieds de page)

Nettoyage et normalisation :

accents

casse

entités géographiques

partis politiques

Stockage des données structurées dans DuckDB

Versionnement du dataset via hash du PDF

détection automatique des changements

reindexation forcée si le PDF est modifié

2. Agent analytique SQL (Level 1)

Détection d’intention :

agrégation

classement

visualisation

Génération de SQL sécurisé et déterministe

Validation stricte :

SELECT uniquement

LIMIT imposé

schéma contrôlé

Exécution sur DuckDB

Restitution :

réponse textuelle

aperçu tabulaire

graphiques inline (bar, histogramme, camembert)

3. Routage hybride SQL + RAG (Level 2)

SQL pour :

statistiques

comptages

rankings

RAG pour :

recherche floue

narration

grounding textuel

Résolution d’entités :

fautes de frappe

accents

alias (ex. RHDP, R.H.D.P, forme longue)

4. Couche agentique (Level 3)

Détection automatique des ambiguïtés :

localités multi-scopes (Abidjan, Tiapoum, Grand-Bassam…)

Interaction utilisateur :

questions de clarification

propositions numérotées

Mémoire de session :

conservation du choix utilisateur

réutilisation dans les requêtes suivantes

5. Observabilité & Évaluation (Level 4)
Observabilité

Traçage complet de chaque requête :

classification d’intention

décisions de routage

SQL généré et validé

appels outils (graphiques)

temps d’exécution

Visualisation des traces dans l’interface Streamlit (mode debug)

Évaluation offline

Jeu de tests automatisé :

exactitude factuelle

validité des agrégations

comparaison numérique avec tolérance

Résumé des métriques :

taux de succès global

résultats par type de requête

Liste détaillée des échecs avec diagnostic

Structure du projet
Artefact_ChatVote/
├── ingestion/
│   ├── ingest_pdf.py          # Pipeline PDF → DataFrame → DuckDB
│   ├── clean_tables.py        # Nettoyage, normalisation, accents
│   ├── commune_mapping.py     # Mapping et standardisation des communes
│   └── versioning.py          # Hash du PDF (dataset versioning)
│
├── data/
│   ├── elections.duckdb       # Base analytique finale
│   ├── raw/                   # PDF source (single source of truth)
│   └── processed/             # CSV intermédiaires, index FAISS
│
├── agents/
│   ├── router.py              # Orchestrateur principal (intent → tool)
│   ├── intent_matcher.py      # Classification sémantique des questions
│   ├── sql_agent.py           # SQL déterministe (requêtes sûres)
│   ├── sqlcoder_agent.py      # LLM local (SQL complexe)
│   ├── disambiguator.py       # Ambiguïtés (Abidjan, Tiapoum…)
│   ├── entity_resolver.py     # Fuzzy matching + regex (partis, lieux)
│   ├── param_extractor.py     # Extraction des nombres, plages, seuils
│   └── agents_normalizer.py   # Normalisation texte pour agents
│
├── rag/
│   ├── indexer.py             # Construction de l’index FAISS
│   ├── retriever.py           # Recherche sémantique
│   └── rag_agent.py           # Réponses textuelles narratives
│
├── app/
│   ├── ui.py                  # Interface Streamlit (chat)
│   ├── state.py               # Session state (messages, entités)
│   └── charts.py              # Visualisations Matplotlib / Plotly
│
├── observability/
│   └── tracer.py              # Tracing end-to-end (TraceRun)
│
├── eval/
│   ├── datasets.py            # Jeux de tests (EVAL_SET)
│   └── run_eval.py            # Logique d’évaluation unitaire
│
├── safety/
│   ├── policy.py              # Guardrails (contenu interdit)
│   └── sql_validator.py       # Sécurité SQL (SELECT-only, LIMIT)
│
├── Evaluation_final.py        #  Script principal d’évaluation offline
│                              #     run_eval()
│                              #     summarize()
│                              #     affichage des échecs
│
├── app.py                     # Point d’entrée Streamlit
├── .env.example               # Variables d’environnement
├── requirements.txt           # Dépendances
└── README.md                  # Documentation recruteur

Stack technique

Python

DuckDB (moteur analytique local)

Streamlit (interface web)

SQLCoder (LLM local pour génération SQL)

RAG / Vector Search

Matplotlib (visualisation)

Sécurité & garde-fous

Réponses limitées strictement au contenu du PDF

Interdiction des opérations SQL destructrices

LIMIT forcé sur toutes les requêtes

Rejets explicites des requêtes hors périmètre

Comportement non-réponse clair si l’information n’est pas dans le dataset

Lancer l’application
pip install -r requirements.txt
streamlit run app.py

Livrables

Code source reproductible

Pipeline d’ingestion

Application web

Tests et évaluation offline

README détaillé

Observabilité et traçage

Architecture documentée

Limitations & prochaines étapes

Enrichissement du jeu de tests d’évaluation

Ajout de métriques de performance

Export des traces vers un backend d’observabilité

Tests de charge

Déploiement cloud

Ce projet démontre une approche complète allant de l’extraction de données à une application conversationnelle robuste, sécurisée et observable, conforme aux attentes d’un poste d’AI Engineer chez Artefact.
