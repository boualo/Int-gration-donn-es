# Atelier Pratique 1 : Extraction et Suggestion de Journaux Académiques


## Introduction
Ce projet a pour objectif de former les participants à l'extraction d'informations à partir de bases de données académiques (Scopus, Web of Science, Google Scholar) en utilisant des techniques de scrapping. Il vise également à développer un outil pour suggérer des revues scientifiques pertinentes pour la publication, basé sur les métadonnées des documents extraits.

## Objectifs
Objectif 1:
Extraction automatique d'informations d'auteurs : Obtenir les informations clés pour un auteur donné depuis les bases de données mentionnées.

Objectif 2:
Suggestion de journaux pour la publication : Utiliser les métadonnées extraites (titre, mots-clés, résumé) pour recommander des revues pertinentes pour la publication.


## Livrables
- Scripts de scrapping : Extraction d'informations d'auteur depuis Scopus, Web of Science, et Google Scholar.
- Mapping et matching de schémas : Intégration des données extraites dans un format standardisé.
- Fichier structuré : Informations détaillées d'un auteur et de ses publications.
- Algorithme de suggestion de journaux : Recommandation de revues scientifiques pour publication.

# Structure des Tâches
1. Extraction d'informations d'auteurs
- Informations extraites : nom, pays d'affiliation, H-index, FWCI, co-auteurs, citations totales, publications, etc.
2. Mapping et Matching de Schémas
- Intégration et fusion de données depuis plusieurs bases en un format unique.
3. Suggestion de Journaux
- Analyse des informations pour recommander des revues pertinentes via des techniques NLP (TF-IDF, Word2Vec).

- 
# Méthodologie et Technologies Utilisées
- Langage : Python (BeautifulSoup, Selenium, Scrapy).
- Bibliothèques : Pandas (traitement de données), Matplotlib (visualisation), NLP pour la suggestion de journaux.
- Outils de Fusion et Nettoyage : OpenRefine pour la standardisation, Dedupe pour la gestion des doublons.

# Installation et Prérequis
- Environnement Python :
Installez les bibliothèques nécessaires : commande : pip install pandas matplotlib BeautifulSoup4 selenium scrapy openrefine-python dedupe

- Accès aux Bases de Données :
Configurez les accès API ou l’utilisation de navigateurs pour les bases Scopus, Web of Science, et Google Scholar.

# Utilisation
1. Exécuter le script d'extraction :
Configurez et lancez le script pour récupérer les données d'un auteur.
2. Effectuer le mapping et matching de schémas :
Utilisez les scripts pour intégrer les données extraites en un format standardisé.
3. Générer des suggestions de journaux :
Exécutez l'algorithme de suggestion pour obtenir des recommandations de revues.

# Ressources Nécessaires
- Ordinateur avec Python et les bibliothèques installées.
- Accès à Scopus, Web of Science, et Google Scholar.
- Documentation pour les API utilisées (Scopus, Web of Science).

  
# Conclusion
- Ce projet apporte une approche pratique pour l'extraction d'informations académiques et la recommandation de revues, renforçant ainsi les compétences en scrapping et intégration de données
