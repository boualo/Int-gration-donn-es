import csv
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Fonction pour extraire le lien d'un article
def extract_articles_link(driver, article_element):
    # Lien vers l'article
    try:
        article_link = article_element.find_element(By.CLASS_NAME, 'gsc_a_at').get_attribute('href')
        citations = article_element.find_element(By.CLASS_NAME, "gsc_a_ac").text
        year = article_element.find_element(By.CLASS_NAME, "gsc_a_h.gsc_a_hc.gs_ibl").text
    except Exception as e:
        print(f"Erreur lors de l'extraction du lien: {e}")
        article_link = ""
        citations = None
        year = None
    
    if article_link:
        title_element, authors, title_source, summary, doi, doc_type, keywords = access_article_page(driver, article_link)
    else:
        title_element = None
        authors = None
        title_source = None
        summary = None
        doi = None
        doc_type = None
        keywords = None
    
    return article_link, title_element, authors, year, title_source, citations, summary, doi, doc_type, keywords

# Fonction pour accéder à la page de l'article et extraire des informations supplémentaires
def access_article_page(driver, article_link):
    # Ouvrir un nouvel onglet 
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get(article_link)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'gsh_csp'))
        )
    except:
        print("Temps d'attente dépassé lors du chargement de la page de l'article.")
    
    # Extraction des informations
    try:
        title_element = driver.find_element(By.CLASS_NAME, 'gsc_oci_title_link').text
    except :
        title_element = None
    try:
        authors = driver.find_element(By.XPATH, ".//div[@class='gsc_oci_value']").text
    except:
        authors = None
    try:
        source_title = driver.find_element(By.XPATH, '//*[@id="gsc_oci_table"]/div[3]/div[2]').text
    except:
        source_title = None
    try:
        summary = driver.find_element(By.XPATH, '//*[@id="gsc_oci_descr"]/div').text
    except:
        summary = None
    try:
        doi = driver.find_element(By.CLASS_NAME, 'gsc_oci_title_link').get_attribute('href')
    except:
        doi = None
    
    try:
        # Type de document
        venue_element = driver.find_element(By.XPATH, '//*[@id="gsc_oci_table"]/div[3]/div[1]')
        venue_text = venue_element.text.lower()
        if 'conference' in venue_text or 'proceedings' in venue_text:
            doc_type = 'Conference'
        elif 'journal' in venue_text:
            doc_type = 'Article'
        elif 'book' in venue_text:
            doc_type = 'Book'
        elif 'Source' in venue_text:
            doc_type = 'Source'
        elif 'Revue' in venue_text:
            doc_type = 'Revue'
        else:
            doc_type = 'Other'
    except:
        doc_type = None
        
    keywords = None

    # Fermer l'onglet de l'article et revenir à l'onglet principal
    try:
        driver.close()
    except:
        print("Erreur lors de la fermeture de l'onglet de l'article.")
    
    driver.switch_to.window(driver.window_handles[0])

    return title_element, authors, source_title, summary, doi, doc_type, keywords

# Fonction pour extraire les articles d'un auteur donné
def extract_articles_from_author(author_id, driver):
    url = f"https://scholar.google.com/citations?user={author_id}&hl=en"
    driver.get(url)
    time.sleep(3)  # Attendre que la page charge

    articles_data = []  # Liste pour stocker les données des articles

    more_articles = True  # Indicateur pour continuer l'extraction si "Show more" est cliquable

    while more_articles:
        try:
            # Localiser tous les articles visibles sur la page
            articles = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'gsc_a_tr'))
            )
        except Exception as e:
            print(f"Erreur lors de la localisation des articles: {e}")
            break

        # Extraire les informations de chaque article non encore ajouté
        for article in articles[len(articles_data):]:  # Seules les nouvelles entrées sont traitées
            try:
                article_link, title, authors, year, source_title, citations, summary, doi, doc_type, keywords = extract_articles_link(driver, article)
                articles_data.append({
                    "Titre de l'article": title,
                    "Auteurs": authors,
                    "Année de publication": year,
                    "Titre de source": source_title,
                    "Nombre de citations": citations,
                    "Résumé": summary,
                    "DOI": doi,
                    "Mots-clés": keywords,
                    "Type de document": doc_type
                })
            except Exception as e:
                print(f"Erreur lors de l'extraction d'un article : {e}")
                continue

        # Essayer de cliquer sur "Show more articles" pour charger plus d'articles
        try:
            show_more_button = driver.find_element(By.ID, "gsc_bpf_more")
            if show_more_button.get_attribute("disabled") is not None:
                print("Aucun autre article à charger.")
                more_articles = False  # Fin de l'extraction
            else:
                show_more_button.click()
                time.sleep(3)  # Attendre que les nouveaux articles se chargent
        except Exception as e:
            print(f"Aucun bouton 'Show more' ou une erreur s'est produite: {e}")
            break

    return articles_data

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



