from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time , random
import os
import zipfile
from bs4 import BeautifulSoup

from ExceptionStorage import ExceptionStorage
from StartupStorage import StartupStorage
from Startup import Startup

class StartupScraping:
    
    def __init__(self, url=None, proxy=None, with_selenium_grid=True, file_path=None, startup=None, contact_link_classifier=None, contactOpenAIScraping=None, 
                 pageProcessing=None, sentenceProcessing= None):
        self.url = url
        self.file_path = file_path
        self.startup = startup
        self.proxy = proxy
        if self.proxy :
            self.PROXY_HOST = proxy["PROXY_HOST"] # rotating proxy or host
            self.PROXY_PORT = proxy["PROXY_PORT"] # port
            self.PROXY_USER = proxy["PROXY_USER"] # username
            self.PROXY_PASS = proxy["PROXY_PASS"] # password
            self.options = self.get_options_for_proxy()
        else:
            self.options = webdriver.ChromeOptions()
            
        self.with_selenium_grid = with_selenium_grid
        if self.with_selenium_grid:
            # IP address and port and server of the Selenium hub and browser options
            self.HUB_HOST = "localhost"
            self.HUB_PORT = 4444
            self.server = f"http://{self.HUB_HOST}:{self.HUB_PORT}/wd/hub"
            self.driver = webdriver.Remote(command_executor=self.server, options=self.options)
        else:
            self.driver = webdriver.Chrome(options=self.options)

        self.contact_link_classifier = contact_link_classifier
        self.contactOpenAIScraping = contactOpenAIScraping
        self.pageProcessing = pageProcessing
        self.sentenceProcessing = sentenceProcessing
        # self.start_scraping()
        

    def get_options_for_proxy(self):
        
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        
        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (self.PROXY_HOST, self.PROXY_PORT, self.PROXY_USER, self.PROXY_PASS)
        
        def get_chrome_options(use_proxy=True, user_agent=None):
            chrome_options = webdriver.ChromeOptions()
            if use_proxy:
                pluginfile = 'proxy_auth_plugin.zip'
        
                with zipfile.ZipFile(pluginfile, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
                chrome_options.add_extension(pluginfile)
            if user_agent:
                chrome_options.add_argument('--user-agent=%s' % user_agent)
            
            return chrome_options
        return get_chrome_options()
        
    def click_elem(self, click_elem):
        t=2
        check = 0
        i = 0
        while not check and i<5:
            try:
                click_elem.click()
                time.sleep(t) ######
                check = 1
            except Exception as e:
                check = 0
            i += 1
            
    def start_scraping(self):
        try:
            self.driver.get(self.url)
            time.sleep(random.uniform(0.5, 3.9))
            
            stop = False
            i=0
            len_results = 0
            while not stop :
                i+=1
                current_url = str(self.driver.current_url).strip()
                print(current_url)
                result = self.get_startups()
                if result["status"]:
                    len_results += result["data"]
                    current_page_number = self.get_element('//*[@role="navigation"]/span[@class="current"]')
                    if current_page_number["status"]:
                        current_page_number = current_page_number["data"]
                        if str(current_page_number.text)=="17":
                            stop = True
                        if not stop:
                            pagination_a_s = self.get_element('//*[@role="navigation"]/a', group=True)
                            if pagination_a_s["status"]:
                                pagination_a_s = pagination_a_s["data"]
                                if len(pagination_a_s)>0:
                                    url = str(pagination_a_s[-2].get_attribute("href")).strip()
                                    self.driver.get(url)
                                    time.sleep(random.uniform(0.5, 3.9))
                                else:
                                    stop = True
                    else:
                        print(f'/'*150)
                        print(i+1)
                        print(pagination_a_s["data"])
                        print(f'\\'*150)
                else:
                    print(result["data"])
                    stop = True
            print('3333333333')
            
            
            return {"status": True, "data": len_results }
            
        except Exception as e:
            print(f"Error : {e}")
            return {"status": False, "data": str(e) }
        finally :
            self.driver.quit()
            
    def get_element(self, path_to_elem, group=False, from_elem=None):
        i = 0
        while i<5:
            try:
                if not from_elem:
                    if not group:
                        elem = self.driver.find_element(By.XPATH, path_to_elem)
                    else :
                        elem = self.driver.find_elements(By.XPATH, path_to_elem)
                    return {"status": True, "data":elem }
                else:
                    if not group:
                        elem = from_elem.find_element(By.XPATH, path_to_elem)
                    else :
                        elem = from_elem.find_elements(By.XPATH, path_to_elem)
                    return {"status": True, "data":elem }
                        
            except Exception as e:
                i += 1
                if i == 5:
                    return {"status": False, "data":str(e) }

    def extract_startup(self, tr_startup):
        startup = Startup()
        a_name = self.get_element('td/a', from_elem=tr_startup)
        if a_name["status"]:
            a_name = a_name["data"]
            startup.startup_name = a_name.text
            startup.startup_more_inf_url = a_name.get_attribute("href")
        else:
            return {"status": False, "data":a_name["data"] }
        
        td_amount_invested = self.get_element('td[2]', from_elem=tr_startup)
        if td_amount_invested["status"]:
            td_amount_invested = td_amount_invested["data"]
            startup.startup_amount_invested = td_amount_invested.text
        else:
            return {"status": False, "data":td_amount_invested["data"] }

        td_article_publication_date = self.get_element('td[3]', from_elem=tr_startup)
        if td_article_publication_date["status"]:
            td_article_publication_date = td_article_publication_date["data"]
            startup.startup_article_publication_date = td_article_publication_date.text
        else:
            return {"status": False, "data":td_article_publication_date["data"] }
            
        return {"status": True, "data": startup }
        
                
    def get_startups(self):
        tr_startups = self.get_element('//*[@id="site-content"]/div/table/tbody/tr', group=True)
        if tr_startups["status"]:
            tr_startups = tr_startups["data"]
            startups_list = []
            for tr_startup in tr_startups:
                startup = self.extract_startup(tr_startup)
                if startup['status']:
                    startups_list.append(startup['data'])
                    # print(startup['data'])
            startupStorage = StartupStorage(self.file_path)
            startupStorage.insert_startups(startups_list)
            startupStorage.close_file()
            print('le nombre des startups est : ',len(tr_startups))
            print(f"*"*150)
            return {"status": True, "data": len(tr_startups)}
        else:
            return {"status": False, "data":tr_startups["data"] }

    def start_scraping_more_inf(self):
        try:
            self.driver.get(self.url)
            time.sleep(random.uniform(0.5, 3.9))
            self.get_startup_more_info()
            #time.sleep(random.uniform(5, 7))
            return {"status": True, "data": self.startup }
            
        except Exception as e:
            print(f"Error : {e}")
            return {"status": False, "data": str(e) }
        finally :
            self.driver.quit()

    def get_startup_more_info(self):
        lis_value = self.get_element('//*[@class="metastartup"]/li', group=True)
        if lis_value["status"] and len(lis_value["data"])>0:
            lis_value = lis_value["data"]
            for li in lis_value:
                span = self.get_element('span',from_elem=li)
                if span["status"]:
                    span = span["data"]
                    b_type = self.get_element('b',from_elem=span)
                    if b_type["status"]:
                        b_type = b_type["data"].text
                        if str(b_type).strip() == 'Fondateurs :':
                            self.startup.startup_founders = span.text
                        if str(b_type).strip() == "Nombre d'employés :":
                            self.startup.startup_Number_of_employees = span.text
                        if str(b_type).strip() == 'Levée de fonds :':
                            self.startup.startup_levée_de_fonds = span.text
        else:
            lis_value = self.get_element('//*[@class="metastartup float-right pr-3"]/li', group=True)
            if lis_value["status"]:
                lis_value = lis_value["data"]
                for li in lis_value:
                    span = self.get_element('span',from_elem=li)
                    if span["status"]:
                        span = span["data"]
                        b_type = self.get_element('b',from_elem=span)
                        if b_type["status"]:
                            b_type = b_type["data"].text
                            if str(b_type).strip() == 'Fondateurs :':
                                self.startup.startup_founders = span.text
                            if str(b_type).strip() == "Nombre d'employés :":
                                self.startup.startup_Number_of_employees = span.text
                            if str(b_type).strip() == 'Levée de fonds :':
                                self.startup.startup_levée_de_fonds = span.text

        a_web_site_url = self.get_element('//ul[@class="lien-startup"]/li/a[@class="btn btn-danger urlwebsite pb-2 text-white"]')
        if a_web_site_url["status"]:
            a_web_site_url = a_web_site_url["data"]
            self.startup.startup_web_site_url = a_web_site_url.get_attribute("href")
        else:
            a_web_site_url = self.get_element('//ul[@class="lien-startup"]/li/a[@class="urlwebsite pb-4"]')
            if a_web_site_url["status"]:
                a_web_site_url = a_web_site_url["data"]
                self.startup.startup_web_site_url = a_web_site_url.get_attribute("href")            

        a_fb = self.get_element('//ul[@class="lien-startup"]/li/a[@class="urlfacebook"]')
        if a_fb["status"]:
            a_fb = a_fb["data"]
            self.startup.startup_facebook_url = a_fb.get_attribute("href")

        a_insta = self.get_element('//ul[@class="lien-startup"]/li/a[@class="urlinsta"]')
        if a_insta["status"]:
            a_insta = a_insta["data"]
            self.startup.startup_instagram_url = a_insta.get_attribute("href")

        a_linkedin = self.get_element('//ul[@class="lien-startup"]/li/a[@class="urllinkedin"]')
        if a_linkedin["status"]:
            a_linkedin = a_linkedin["data"]
            self.startup.startup_linkedin_url = a_linkedin.get_attribute("href")
            
        p_phrasechoc = self.get_element('//p[@class="phrasechoc"]')
        if p_phrasechoc["status"]:
            p_phrasechoc = p_phrasechoc["data"]
            self.startup.startup_phrasechoc = p_phrasechoc.text
        else:
            p_phrasechoc = self.get_element('//blockquote[@class="quote_full blockquote"]/p')
            if p_phrasechoc["status"]:
                p_phrasechoc = p_phrasechoc["data"]
                self.startup.startup_phrasechoc = p_phrasechoc.text

    def start_verify_startup_web_site_url(self):
        try:
            origin_url = str(self.url).strip()
            print(f"origin_url : {origin_url}")
            self.driver.get(self.url)
            time.sleep(random.uniform(0.5, 2))
            current_url = str(self.driver.current_url).strip()
            print(f"current_url : {current_url}")
            print(f"*"*150)
            self.startup.startup_valid_web_site_url = True
            self.startup.startup_right_web_site_url = current_url
            
            return {"status": True, "data": self.startup }
            
        except Exception as e:
            self.startup.startup_right_web_site_url = str(self.driver.current_url).strip()
            self.startup.startup_valid_web_site_url = False
            return {"status": False, "data": self.startup }
        finally :
            self.driver.quit()

    def get_all_contact_page_links(self):
        try:
            if self.startup.startup_valid_web_site_url:
                print(self.url)
                self.driver.get(self.url)
                time.sleep(2)
        
                addresses = []
                emails, phones = self.get_contact_info_from_page()
                
                html_source = self.driver.page_source
                results = self.get_contact_info_with_openAI(html_source)
                emails += list(results['content']['emails'])
                phones += list(results['content']['phones'])
                addresses += list(results['content']['addresses'])
        
                
                contact_links = list(set(self.contact_link_classifier.get_contact_links(html_source)))
                print(contact_links)
                
                for index, contact_link in enumerate(contact_links):
                    if index != 0:
                        self.driver.get(self.url)
                        time.sleep(random.uniform(2, 3))
                    a_elem = self.get_element(f'//a[@href="{contact_link[0]}"]')
                    # print(a_elem)
                    if a_elem["status"]:
                        a_elem = a_elem["data"]
                        first_url = str(self.driver.current_url)
                        self.click_elem(a_elem)
                        time.sleep(random.uniform(1, 2))
                        current_url = str(self.driver.current_url)
                        if first_url != current_url:
                            print(current_url)
                            emails_contact_page, phones_contact_page = self.get_contact_info_from_page()
                            emails += emails_contact_page
                            phones += phones_contact_page
                            html_source = self.driver.page_source
                            results = self.get_contact_info_with_openAI(html_source)
                            emails += list(results['content']['emails'])
                            phones += list(results['content']['phones'])
                            addresses += list(results['content']['addresses'])
                        else:
                            try:
                                if 'http' in a_elem.get_attribute('href'):
                                    print(a_elem.get_attribute('href'))
                                    self.driver.get(a_elem.get_attribute('href'))
                                    time.sleep(random.uniform(1, 2))
                                    emails_contact_page, phones_contact_page = self.get_contact_info_from_page()
                                    emails += emails_contact_page
                                    phones += phones_contact_page
                                    html_source = self.driver.page_source
                                    results = self.get_contact_info_with_openAI(html_source)
                                    emails += list(results['content']['emails'])
                                    phones += list(results['content']['phones'])
                                    addresses += list(results['content']['addresses'])
                                else:
                                    built_contact_link = '/'.join((self.url.split('/'))[:3]) + a_elem.get_attribute('href')
                                    print(built_contact_link)
                                    self.driver.get(built_contact_link)
                                    time.sleep(random.uniform(1, 2))
                                    emails_contact_page, phones_contact_page = self.get_contact_info_from_page()
                                    emails += emails_contact_page
                                    phones += phones_contact_page
                                    html_source = self.driver.page_source
                                    results = self.get_contact_info_with_openAI(html_source)
                                    emails += list(results['content']['emails'])
                                    phones += list(results['content']['phones'])
                                    addresses += list(results['content']['addresses'])
                            except Exception as e:
                                print('cannot click on the contact page link ****************************************************************************************')
                    else:
                        print(a_elem)
        
                self.startup.startup_phone = list(set(phones))
                self.startup.startup_email = list(set(emails))
                self.startup.startup_address = list(set(addresses))
                
                for fake_email in ['info@company.com', 'support@company.com','contact@company.com', 'sales@company.com','contact@example.com', 'support@example.com', 'info@example.com', 'sales@example.com']:
                    if fake_email in self.startup.startup_email:
                        self.startup.startup_email.remove(fake_email)
                        
                return {"status": True, "data": self.startup }
            else:
                return {"status": False, "data": self.startup }
        except Exception as e:
            print(f'ERRRRRRRRRRRRRRRRRRRRRRRROR: {e}')
            ExceptionStorage(self.startup, str(e))
            return {"status": False, "data": self.startup }
        finally:
            self.driver.quit()
            
    def get_contact_info_from_page(self):
        # Trouver toutes les balises <a> de la page
        liens = self.driver.find_elements(By.TAG_NAME, "a")
        
        # Listes pour stocker les e-mails et téléphones
        emails = []
        phones = []
        
        # Boucler sur chaque lien trouvé
        for lien in liens:
            href = lien.get_attribute("href")  # Extraire l'attribut href
            
            # Vérifier si le lien est un mailto:
            if href and "mailto:" in href:
                emails.append(href.split("mailto:")[1])  # Extraire l'adresse e-mail
            
            # Vérifier si le lien est un tel:
            elif href and "tel:" in href:
                phones.append(href.split("tel:")[1])  # Extraire le numéro de téléphone
        emails = list(set(emails))
        phones = list(set(phones))
        # Afficher les résultats
        # print("Emails trouvés :", emails)
        # print("Téléphones trouvés :", phones)
        return emails, phones

    def get_contact_info_with_openAI(self, html_source):
        clean_text = self.pageProcessing.get_clean_html_text_from_source_page(html_source)
        new_clean_text = self.sentenceProcessing.get_new_clean_text(clean_text)
        results = self.contactOpenAIScraping.predict(new_clean_text)
        # print(results)
        return results