from selenium.webdriver.common.by import By
import time
import random
import csv
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs


#Recherche un auteur sur Google Scholar et retourne le lien vers son profil.
def search_author(author_name, driver):
    driver.get("https://scholar.google.com/")
    time.sleep(random.uniform(5, 15))

    # Trouver la barre de recherche et entrer le nom de l'auteur
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(author_name)
    search_box.submit()
    time.sleep(2) 

    # Tenter de trouver le lien vers le profil de l'auteur
    try:
        author_profile = driver.find_element(By.XPATH, f"//h4/a[contains(@href, '/citations?user=')]")
        profile_link = author_profile.get_attribute('href')
        return profile_link
    except NoSuchElementException:
        print("Profil de l'auteur non trouvé.")
        return None



#Extrait les informations de l'auteur depuis son profil Google Scholar.
def extract_author_info(profile_link, driver):
    driver.get(profile_link)
    time.sleep(2) 

    author_info = {}

    # Extraire l'ID de l'auteur à partir de l'URL
    parsed_url = urlparse(profile_link)
    query_params = parse_qs(parsed_url.query)
    author_id = query_params.get('user', [None])[0]
    author_info['ID de l\'Auteur'] = author_id

    try:
        # Nom complet
        name = driver.find_element(By.ID, "gsc_prf_in").text
        author_info['Nom Complet'] = name
    except NoSuchElementException:
        author_info['Nom Complet'] = None

    try:
        # Affiliation et pays
        affiliation = driver.find_element(By.CLASS_NAME, "gsc_prf_ila").text
        author_info['Pays d\'Affiliation'] = affiliation
    except NoSuchElementException:
        author_info['Pays d\'Affiliation'] = None

    try:
        # H-index et Citations
        metrics = driver.find_elements(By.CLASS_NAME, "gsc_rsb_std")
        if len(metrics) >= 4:
            author_info['Citations Totales'] = metrics[0].text
            author_info['H-index'] = metrics[2].text
            # FWCI n'est pas disponible sur Google Scholar
            author_info['FWCI'] = 'N/A'
        else:
            author_info['Citations Totales'] = None
            author_info['H-index'] = None
            author_info['FWCI'] = 'N/A'
    except NoSuchElementException:
        author_info['Citations Totales'] = None
        author_info['H-index'] = None
        author_info['FWCI'] = 'N/A'

    try:
        # Co-auteurs
        co_authors = []
        view_all_coauthors_button = driver.find_elements(By.XPATH, '//button[@id="gsc_coauth_opn"]')
        if len(view_all_coauthors_button) > 0 and view_all_coauthors_button[0].is_displayed():
            view_all_coauthors_button[0].click()
            co_authors_elements = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//h3[@class='gs_ai_name']/a"))
            )
            for elem in co_authors_elements:
                co_authors.append(elem.text)
            # Fermer la modal des co-auteurs
            cancel_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "gsc_md_cod-x"))
            )
            cancel_button.click()
        else:
            co_authors_elements = driver.find_elements(By.XPATH, "//span[@class='gsc_rsb_a_desc']/a")
            for elem in co_authors_elements:
                co_authors.append(elem.text)

        author_info['Co-auteurs'] = "; ".join(co_authors) if co_authors else None
    except NoSuchElementException:
        author_info['Co-auteurs'] = None

    return author_info


# Charge la liste des auteurs depuis un fichier texte.
def load_authors_from_file(file_path='authors.txt'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            authors = [line.strip() for line in f if line.strip()]
        return authors
    except FileNotFoundError:
        print(f"Fichier '{file_path}' non trouvé.")
        return []


def load_from_csv(filename):
    """
    Load data from a CSV file and return it as a list of dictionaries.
    Each row in the CSV is returned as a dictionary with column names as keys.
    """
    data = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"File {filename} not found. Starting with an empty list.")
    except Exception as e:
        print(f"An error occurred while loading data from {filename}: {e}")
    return data

