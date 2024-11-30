import time
import random
import os
import pickle
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Import des modules existants
from auteur_file import search_author, extract_author_info, load_authors_from_file
from article_file import extract_articles_from_author
from journal_file import search_journal_by_issn

# Configuration du WebDriver
chrome_options = Options()
chromedriver_path = "C:\\chromedriver.exe"
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Chargement des données
def load_progress():
    if os.path.exists("treated_authors.pkl"):
        with open("treated_authors.pkl", "rb") as file:
            treated_authors = pickle.load(file)
    else:
        treated_authors = set()

    all_author_data = pd.read_csv('partial_auteur_info.csv').to_dict(orient="records") if os.path.exists('partial_auteur_info.csv') else []
    all_article_data = pd.read_csv('partial_article_info.csv').to_dict(orient="records") if os.path.exists('partial_article_info.csv') else []
    all_journal_data = pd.read_csv('partial_journal_info.csv').to_dict(orient="records") if os.path.exists('partial_journal_info.csv') else []

    existing_issns = set(journal.get('ISSN') for journal in all_journal_data if 'ISSN' in journal)

    return treated_authors, all_author_data, all_article_data, all_journal_data, existing_issns

def save_progress():
    with open("treated_authors.pkl", "wb") as file:
        pickle.dump(treated_authors, file)
    pd.DataFrame(all_author_data).to_csv('partial_auteur_info.csv', index=False)
    pd.DataFrame(all_article_data).to_csv('partial_article_info.csv', index=False)
    pd.DataFrame(all_journal_data).to_csv('partial_journal_info.csv', index=False)
    print("Progress saved to partial files.")

# Nettoyage des requêtes pour Google
def clean_search_query(query):
    query = query.replace(" in ", " \"in\" ")  # Gestion spécifique des mots-clés
    return f'"{query.strip()}"'

# Détection et gestion des blocages
def detect_and_handle_blocking():
    try:
        if "captcha" in driver.page_source.lower():
            print("CAPTCHA detected! Pausing for a longer time.")
            time.sleep(random.uniform(60, 120))
    except WebDriverException as e:
        print(f"Webdriver issue: {e}")

# Extraction récursive des auteurs et co-auteurs
def extract_author_and_coauthors(author_name, depth=0, max_depth=2):
    if depth > max_depth:
        return
    
    print(f"Processing author (level {depth}): {author_name}")
    
    if author_name in treated_authors:
        print(f"Author {author_name} already processed, skipping.")
        return

    profile_link = search_author(clean_search_query(author_name), driver)
    if profile_link:
        author_data = extract_author_info(profile_link, driver)
        if author_data:
            all_author_data.append(author_data)
            treated_authors.add(author_name)

            # Traitement des co-auteurs
            if 'Co-auteurs' in author_data and author_data['Co-auteurs']:
                co_authors = author_data['Co-auteurs'].split("; ")
                for co_author in co_authors:
                    extract_author_and_coauthors(co_author, depth + 1, max_depth)

    time.sleep(random.uniform(1, 3))
    save_progress()

# Extraction des articles
def process_articles():
    for author_data in all_author_data:
        author_id = author_data.get("ID de l'Auteur")
        if author_id not in [article.get("ID de l'Auteur") for article in all_article_data]:
            articles_data = extract_articles_from_author(author_id, driver)
            if articles_data:
                for article in articles_data:
                    article["ID de l'Auteur"] = author_id
                    all_article_data.append(article)
            time.sleep(random.uniform(5, 15))
            save_progress()

# Extraction des journaux
def process_journals():
    for article in all_article_data:
        source_title = article.get('Titre de source')
        if 'ISSN' not in article and source_title not in existing_issns:
            journal_data = search_journal_by_issn(source_title, driver)
            if journal_data:
                article['ISSN'] = journal_data.get('ISSN')
                all_journal_data.append(journal_data)
                existing_issns.add(journal_data.get('ISSN'))
            time.sleep(random.uniform(1, 3))
            save_progress()

# Fonction principale
def main():
    global treated_authors, all_author_data, all_article_data, all_journal_data, existing_issns
    treated_authors, all_author_data, all_article_data, all_journal_data, existing_issns = load_progress()

    authors = load_authors_from_file('authors.txt')

    if not authors:
        print("No authors to process.")
        driver.quit()
        return

    # Étape 1 : Traitement des auteurs
    for author_name in authors:
        extract_author_and_coauthors(author_name)

    # Étape 2 : Traitement des articles
    process_articles()

    # Étape 3 : Traitement des journaux
    process_journals()

    print("Processing complete.")
    save_progress()
    driver.quit()

if __name__ == "__main__":
    main()
