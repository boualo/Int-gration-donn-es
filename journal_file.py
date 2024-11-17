from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import random
import csv


# Function to search for a journal by ISSN on SJR
def search_journal_by_issn(source_title, driver):
    driver.get("https://www.scimagojr.com")

    # Check if source_title is None and handle it
    if source_title is None:
        print("Error: source_title is None.")
        return {
            'Nom': None, 'Editeur': None, 'ISSN': None, 'Index': None, 'H-index': None, 
            'Quartile': None, 'SJR': None, 'Impact factor': None, 'Portee thematique': None
        }

    try:
        # Find the search bar by its ID and input the source title
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchinput"))
        )
        search_box.clear()
        search_box.send_keys(source_title)
        search_box.submit()
        time.sleep(random.uniform(5, 15))

        # Check for "no results" message on the page
        no_results_message = "Sorry, no results were found."
        if no_results_message in driver.page_source:
            print(f"No results found for {source_title}.")
            return {
                'Nom': None, 'Editeur': None, 'ISSN': None, 'Index': None, 'H-index': None, 
                'Quartile': None, 'SJR': None, 'Impact factor': None, 'Portee thematique': None
            }

        # Wait for search results to load and get the links
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='search_results']/a[@href]")))
        links = driver.find_elements(By.XPATH, "//div[@class='search_results']/a[@href]")
        jrl_names = driver.find_elements(By.CLASS_NAME, 'jrnlname')

        # Check if any of the results match the exact journal title
        exact_match_found = False
        for i, name in enumerate(jrl_names):
            if name.text == source_title:
                links[i].click()  # Click on the exact matching link
                exact_match_found = True
                time.sleep(random.uniform(5, 10))
                break
        
        if not exact_match_found:
            # Click on the first search result if no exact match was found
            journal_link = driver.find_element(By.XPATH, "//div[@class='search_results']/a[@href]")
            journal_link.click()
            time.sleep(random.uniform(5, 15))

        # Extract journal information
        journal_info = {}

        # Journal name
        journal_info['Nom'] = driver.find_element(By.XPATH, "//h1").text
        
        # Publisher
        try:
            journal_info['Editeur'] = driver.find_element(By.XPATH, "//div[h2[text()='Publisher']]/p/a").text
        except NoSuchElementException:
            journal_info['Editeur'] = None

        # ISSN
        try:
            issn_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[h2[text()='ISSN']]/p"))
            )
            journal_info['ISSN'] = issn_element.text
        except (NoSuchElementException, TimeoutException):
            journal_info['ISSN'] = None
        
        # Indexing
        try:
            journal_info['Index'] = driver.find_element(By.XPATH, "//div[h2[text()='Coverage']]/p").text
        except NoSuchElementException:
            journal_info['Index'] = None
        
        # H-index
        try:
            journal_info['H-index'] = driver.find_element(By.XPATH, "//div[h2[text()='H-Index']]/p").text
        except NoSuchElementException:
            journal_info['H-index'] = None
        
        # Quartile
        try:
            journal_info['Quartile'] = driver.find_element(By.XPATH, "(//div[@class='cellcontent']//table/tbody/tr[last()]/td[3])[1]").text
        except NoSuchElementException:
            journal_info['Quartile'] = None
        
        # SJR Score
        try:
            journal_info['SJR'] = driver.find_element(By.XPATH, "(//div[@class='cellcontent']//table/tbody/tr[last()]/td[3])[2]").text
        except NoSuchElementException:
            journal_info['SJR'] = None

        # Impact factor (sometimes available)
        try:
            journal_info['Impact factor'] = driver.find_element(By.XPATH, "(//div[@class='cellcontent']//table/tbody/tr[last()]/td[3])[4]").text
        except NoSuchElementException:
            journal_info['Impact factor'] = None
        
        # Thematic scope
        try:
            journal_info['Portee thematique'] = driver.find_element(By.CLASS_NAME, 'fullwidth').text.split('\n', 1)[-1].strip()
        except NoSuchElementException:
            journal_info['Portee thematique'] = None
        
        return journal_info
    
    except Exception as e:
        print(f"An error occurred while searching for journal {source_title}: {e}")
        return None

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
