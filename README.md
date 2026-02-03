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

Liste détaillée des échecs avec diagnostic.






# Archietecture du projet: 


<img width="467" height="323" alt="image" src="https://github.com/user-attachments/assets/617c0ca6-3b75-4ca5-90b0-62a104b17ae8" />




suite:

![Image_rag](https://github.com/user-attachments/assets/04eb3977-ad89-4a22-a9e3-cd3b097aa55c)


-Stack technique

-Python

-DuckDB (moteur analytique local)

-Streamlit (interface web)

-SQLCoder (LLM local pour génération SQL)

-RAG / Vector Search

-Matplotlib (visualisation)

Sécurité & garde-fous

-Réponses limitées strictement au contenu du PDF

-Interdiction des opérations SQL destructrices

-LIMIT forcé sur toutes les requêtes

-Rejets explicites des requêtes hors périmètre

-Comportement non-réponse clair si l’information n’est pas dans le dataset.

L'application utilise une stratégie à deux niveaux pour garantir à la fois la précision des données et la souplesse de l'interaction :

# Niveau Déterministe (Fast & Reliable)
Modèle utilisé : all-MiniLM-L6-v2 (via Sentence-Transformers).

Fonctionnement : Ce modèle léger transforme la question de l'utilisateur en un vecteur numérique. Il compare ensuite ce vecteur avec les exemples stockés dans agents/intent_catalog.py (Calcul de similarité cosinus).

Cas d'usage : Si la question correspond à une intention connue (ex: "Top 5 des candidats", "Résultats par commune"), le système appelle directement la requête SQL pré-optimisée du catalogue. Cela garantit 0% d'erreur de syntaxe SQL et une réponse instantanée.

 # Niveau Génératif (Fallback / Complex Queries)
Modèle utilisé : sqlcoder-7b-q5_k_m.gguf (via Llama-cpp-python).

Fonctionnement : Si le score de similarité avec le catalogue est trop faible (intention inconnue), le système passe le relais à SQLCoder.

Cas d'usage : Pour les requêtes croisées complexes que nous n'avons pas anticipées dans le catalogue. Le LLM analyse le schéma de la base DuckDB et génère dynamiquement la requête SQL nécessaire pour répondre précisément à l'utilisateur.
# agents/router.py :
C'est lorchestrateur de notre système, toute la chaine décrite précédement est géré là.

# Lancer l’application:
 -D'abord télécharger tous les fichiers sur ce repo pour mettre dans un dossier que vous
 allez nommé à votre choix; ex: "Mon_dossier". Mais avant ça créez un environnement virtuel.
 -Ensuite créez un dossiers models à l'intérieur de "Mon_dossier" et ajouter "sqlcoder-7b-q5_k_m.gguf" à l'intérieur
 dont le lien de téléchargement est :https://huggingface.co/TheBloke/sqlcoder-7B-GGUF/blob/main/sqlcoder-7b.Q5_K_M.gguf.
-Entrer dans le dossier "Mon_dossier" puis dans l'invite de commande activez l'environnement virtuel.


Tapez: 


#   pip install -r requirements.txt

   
#   streamlit run Application.py

#  python Evaluation_final.py : Pour l'évalution offline


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
