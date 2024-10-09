from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup, Comment

import time
import csv

import pandas as pd

class PageProcessing:
    def __init__(self):
        # IP address and port and server of the Selenium hub and browser options
        self.HUB_HOST = "localhost"
        self.HUB_PORT = 4444
        self.server = f"http://{self.HUB_HOST}:{self.HUB_PORT}/wd/hub"
        self.options = webdriver.ChromeOptions()
        self.driver = None

        self.MIN_LENGTH_PHONE = 5
        
    def count_numbers(self, word):
        i=0
        word = word.split(' ')
        word = ''.join(word)
        for char in word:
            if char.isdigit():
                i += 1
        return i
        
    def get_source_page_from_url(self, url):
        try:
            self.driver = webdriver.Remote(command_executor=self.server, options=self.options)

            self.driver.get(url)

            # Attendre que la page soit complètement chargée
            wait = WebDriverWait(self.driver, 5)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            source_page = self.driver.page_source
            
            self.driver.quit()
            
            return source_page
        except Exception as e:
            print(f"Errooooooor : Une exception s'est produite : {e}")
            
    def get_clean_html_text_from_source_page(self, source_page):
        soup = BeautifulSoup(source_page, 'html.parser')

        # Vider le contenu de la balise <head>
        before = len(str(soup).split())
        head_tag = soup.find('head')
        head_tag.clear()
        after = len(str(soup).split())
        # print(f"-----------> Vider le contenu de la balise <head>: {after - before} deleted words")

        # supprimer les commentaires
        before = len(str(soup).split())
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()
        after = len(str(soup).split())
        # print(f"-----------> supprimer les commentaires : {after - before} deleted words")
        
        # Supprimer les balises script... avec leur contenu
        before = len(str(soup).split())
        for script in soup(["script", "noscript", "style", "img","input", "textarea"]):
            script.extract()
        after = len(str(soup).split())
        # print(f"-----------> Supprimer les balises avec leur contenu : script, noscript, style, ul, form, table, footer :  {after - before} deleted words")

        # Supprimer les balises de formatage de text sans suppression du contenu de balise
        # before = len(str(soup).split())
        # for tag in soup(["b", "strong", "i", "em", "u", "s", "sub", "sup", "small", "abbr", "mark", "del", "ins", "span"]):
        #     tag.unwrap()
        # after = len(str(soup).split())
        # print(f"-----------> Supprimer les balises de formatage de text sans suppression du contenu de balise: {after - before} deleted words")

        # # Sélection de toutes les balises <a>
        before = len(str(soup).split())
        for tag in soup.find_all('a'):
            if '@' not in tag.get_text() and '@' not in tag.get('href', '') and self.count_numbers(tag.get_text()) <= self.MIN_LENGTH_PHONE:
                tag.extract()
        after = len(str(soup).split())
        # print(f"-----------> Sélection et filtrer de toutes les balises <a>: {after - before} deleted words")

        # Récupérer le HTML nettoyé
        return soup.text

    def get_clean_html_text_from_url(self, url):
        print("Start get_source_page_from_url")
        start = time.perf_counter()
        source_page = self.get_source_page_from_url(url)
        end = time.perf_counter()
        print(f"Execution time of get_source_page_from_url : {end - start:.6f} seconds")
        print(f"number of words in the source_page : {len(str(source_page).split())}")
        print(f"number of characters in the source_page : {len(str(source_page))}\n{'-'*100}")

        print("Start get_clean_html_from_source_page")
        start = time.perf_counter()
        clean_html = self.get_clean_html_text_from_source_page(source_page)
        end = time.perf_counter()
        print(f"Execution time of get_clean_html_from_source_page : {end - start:.6f} seconds")
        print(f"number of words in the clean_html : {len( str(clean_html).split() )}")
        print(f"number of characters in the clean_html : {len(str(clean_html))}\n{'-'*100}")

        return clean_html