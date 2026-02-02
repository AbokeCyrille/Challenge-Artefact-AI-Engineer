# Artefact AI Engineer Challenge — Chat avec les Données Électorales(ELECTION DES DEPUTES A L'ASSEMBLEE NATIONALE)

#                                                               Contexte

Ce projet est une application d’analyse conversationnelle construite à partir d’un PDF officiel des résultats électoraux publié par la CEI (Commission Électorale Indépendante de Côte d’Ivoire).

L’objectif est de permettre à un utilisateur de dialoguer avec le jeu de données afin de :

      -Répondre à des questions factuelles, strictement basées sur le contenu du PDF

      -Calculer des agrégations, classements et statistiques

      -Générer des graphiques à la demande

      -Améliorer progressivement la robustesse, la sécurité et la readiness production

Le PDF est l’unique source de vérité.
Aucune information externe n’est utilisée.

Vue d’ensemble de la solution

La solution repose sur une architecture modulaire, déterministe et orientée production, couvrant les niveaux 1 à 4 du challenge.

#                                      1. Pipeline d’ingestion des données

Chargement du PDF officiel des résultats électoraux

Extraction des tableaux (gestion des en-têtes répétés, sauts de ligne, pieds de page)

Nettoyage et normalisation :

      -accents

      -casse

      -entités géographiques

      -partis politiques

Stockage des données structurées dans DuckDB

Versionnement du dataset via hash du PDF

détection automatique des changements

reindexation forcée si le PDF est modifié

#                                      2. Agent analytique SQL (Level 1)

Détection d’intention :

        -agrégation

        -classement

        -visualisation

Génération de SQL sécurisé et déterministe

Validation stricte :

      -SELECT uniquement

      -LIMIT imposé

      -schéma contrôlé

      - Exécution sur DuckDB

Restitution :

réponse textuelle

aperçu tabulaire

graphiques inline (bar, histogramme, camembert)

#                                                3. Routage hybride SQL + RAG (Level 2)

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

#                                     4. Couche agentique (Level 3)

Détection automatique des ambiguïtés :

localités multi-scopes (Abidjan, Tiapoum, Grand-Bassam…)

Interaction utilisateur :

questions de clarification

propositions numérotées

Mémoire de session :

conservation du choix utilisateur

réutilisation dans les requêtes suivantes

#                                      5. Observabilité & Évaluation (Level 4)
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

Structure du projet: 
<img width="467" height="323" alt="image" src="https://github.com/user-attachments/assets/617c0ca6-3b75-4ca5-90b0-62a104b17ae8" />

suite:

<img width="278" height="242" alt="image" src="https://github.com/user-attachments/assets/41c6342c-945a-42ce-9490-ae162601db6c" />

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

# Lancer l’application:
 -D'abord télécharger tous les fichiers sur ce repo pour mettre dans un dossier que vous
 allez nommé à votre choix; ex: "Mon_dossier". Mais avant ça créez un environnement virtuel.
 -Ensuite créez un dossiers models à l'intérieur de "Mon_dossier" et ajouter "sqlcoder-7b-q5_k_m.gguf" à l'intérieur
 dont le lien de téléchargement est :https://huggingface.co/TheBloke/sqlcoder-7B-GGUF/blob/main/sqlcoder-7b.Q5_K_M.gguf.
-Entrer dans le dossier "Mon_dossier" puis dans l'invite de commande activez l'environnement virtuel.


Tapez: 
   pip install -r requirements.txt
   streamlit run app.py


Observabilité et traçage

Architecture documentée

Limitations & prochaines étapes

Enrichissement du jeu de tests d’évaluation

Ajout de métriques de performance

Export des traces vers un backend d’observabilité

Tests de charge

#  Schema de l'application User-> Système

![Uploading image.png…]()


#                                                                 6. Conclusion

Ce projet démontre une approche end-to-end, depuis l’ingestion de données non structurées jusqu’à une application conversationnelle analytique , sécurisée et observable. 
