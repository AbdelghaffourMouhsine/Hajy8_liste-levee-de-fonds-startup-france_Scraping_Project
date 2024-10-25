from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import time , random
import os, re, json, copy
import zipfile
from bs4 import BeautifulSoup

from ExceptionStorage import ExceptionStorage
from StartupStorage import StartupStorage
from Startup import Startup

class StartupScraping:
    
    def __init__(self, url=None, proxy=None, with_selenium_grid=True, file_path=None, startup=None, contact_link_classifier=None, contactOpenAIScraping=None, 
                 pageProcessing=None, sentenceProcessing= None, foundersOpenAIClassification=None, filterFoundersOneByOneOpenAI=None):
        self.url = url
        self.file_path = file_path
        self.startup = startup
        self.item = startup
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
        self.foundersOpenAIClassification = foundersOpenAIClassification
        self.filterFoundersOneByOneOpenAI = filterFoundersOneByOneOpenAI
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

    ########################################################################################################
    def get_linkedin_authentication(self):
        email = 'abdelghaffourmh@gmail.com'
        pwd = 'abdo12345'
        email = 'abdelghaffourm@gmail.com'
        pwd = 'abdo@#%&)Mouhsine//2001*10'
        email = 'hs45@gmx.fr'
        pwd = 'LZidaneNE1010!N'
        
        url = 'https://www.linkedin.com/login/fr?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
        self.driver.get(url)

        self.driver.maximize_window()
        time.sleep(2)
        
        input_username = self.get_element('//*[@id="username"]')
        if input_username["status"]:
            input_username = input_username["data"]
            input_username.send_keys(email)
            input_username.send_keys(Keys.ENTER)
        else:
            print({"status": False, "data":input_username["data"] })
        time.sleep(2)

        input_password = self.get_element('//*[@id="password"]')
        if input_password["status"]:
            input_password = input_password["data"]
            input_password.send_keys(pwd)
            input_password.send_keys(Keys.ENTER)
        else:
            print({"status": False, "data":input_password["data"] })
        time.sleep(20)
        
    def get_LinkedIn_profiles_of_company_founders(self, item):
        self.item = item
        time.sleep(random.uniform(1,1.5))
        try:
            if str(self.item.startup_linkedin_url).strip() != "nan" and self.item.startup_linkedin_url.strip() != "" and self.item.startup_linkedin_url != None and self.item.startup_linkedin_url != 'none' and self.item.startup_linkedin_url != 'None' and self.item.startup_linkedin_url != 'null' and  'company' in self.item.startup_linkedin_url:
                # print(self.item.startup_linkedin_url, type(self.item.startup_linkedin_url))
        
            
                self.driver.get(self.item.startup_linkedin_url)
                time.sleep(random.uniform(2,3.5))
    
                a_personnes_link = None
                a_personnes_button = self.get_element('/html/body/div[6]/div[3]/div/div[2]/div/div[2]/main/div[1]/section/div/div[2]/div[3]/nav/ul/li[5]/a')
                if a_personnes_button["status"]:
                    a_personnes_button = a_personnes_button["data"]
                    a_personnes_link = a_personnes_button.get_attribute('href')
    
                if type(a_personnes_button) == dict or a_personnes_button.text.strip() != 'Personnes':
                    # print('at else ...')
                    time.sleep(random.uniform(1,2.5))
                    a_personnes_button = self.get_element('//li/a', group=True)
                    if a_personnes_button["status"]:
                        a_personnes_button = a_personnes_button["data"]
                        for a in a_personnes_button:
                            if a.text.strip() == 'Personnes':
                                a_personnes_link = a.get_attribute('href')
                                break
                    else:
                        print({"status": False, "data": a_personnes_button["data"] })
                    
    
                if a_personnes_link:
                    self.driver.get(a_personnes_link)
                    time.sleep(random.uniform(2,4.5))
                    
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    second = False
                    while True:
                        # Scroll down to bottom
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        # Wait to load page
                        time.sleep(random.uniform(2.5, 4))
                        # Calculate new scroll height and compare with total scroll height
                        new_height = self.driver.execute_script("return document.body.scrollHeight")
                        
                        if new_height == last_height:
                            
                            temp = False
                            if not temp:
                                buttons = self.get_element('//button', group=True)
                                if buttons["status"]:
                                    buttons = buttons["data"]
                                    if len(buttons)>0:
                                        for button in buttons:
                                            if button.text.lower() == 'afficher plus de résultats':
                                                button.click()
                                                print("yeeeees : if button.text.lower() == 'afficher plus de résultats':")
                                                temp = True
                                                break
                    
                            if second and not temp:
                                break
                            else:
                                second = True
                                time.sleep(random.uniform(1.5,2.5))
                                
                        last_height = new_height
                        
                personnes_li_s = self.get_element('//div[@class="artdeco-card org-people-profile-card__card-spacing org-people__card-margin-bottom"]/div/div/ul/li', group=True)
                if personnes_li_s["status"]:
                    personnes_li_s = personnes_li_s["data"]
                    # print(f'le nombre de personnes avant extract est: {len(personnes_li_s)}')
                    profiles = []
                    for li in personnes_li_s:
                        profile = self.get_personne_profile_from_li(li)
                        if profile["status"]:
                            # print(profile["data"])
                            profiles.append(profile["data"])
                    # print(f'le nombre de personnes apres extract est : {len(profiles)}')
                else:
                    print({"status": False, "data": personnes_li_s["data"] })
    
                self.item.profiles = profiles
                print(f'{self.item.startup_name} : {len(self.item.profiles)}')
                return {"status": True, "data": self.item }
                            
            else:
                return {"status": True, "data": self.item }
                
        except Exception as e:
            print(f'ERRRRRRRRRRRRRRRRRRRRRRRROR: ({self.item.startup_linkedin_url},{type(self.item.startup_linkedin_url)}) {e}')
            ExceptionStorage(self.item, str(e))
            return {"status": False, "data": self.item }
            
    def get_personne_profile_from_li(self, personne_li):
        personne_dic = {}
        a_profile_url = self.get_element('div/section/div/div/div[2]/div[1]/a[@class="app-aware-link  link-without-visited-state"]', from_elem=personne_li)
        if a_profile_url["status"]:
            a_profile_url = a_profile_url["data"]
            personne_dic['profile_url'] = a_profile_url.get_attribute('href')
            personne_dic['person_name'] = a_profile_url.get_attribute("innerText")
        else:
            return {"status": False, "data": a_profile_url["data"] }

        div_profile_description = self.get_element('div/section/div/div/div[2]/div[@class="artdeco-entity-lockup__subtitle ember-view"]', from_elem=personne_li)
        if div_profile_description["status"]:
            div_profile_description = div_profile_description["data"]
            personne_dic['profile_description'] = div_profile_description.get_attribute("innerText")
            
        else:
            print({"status": False, "data": div_profile_description["data"] })
            
        return {"status": True, "data": personne_dic }

    ########################################################################################################
    def get_Founder_Profiles_using_OpenAi(self, item):        
        self.item = item

        def clean_invalid_escapes(json_string):
            # Supprime les séquences d'échappement invalides
            cleaned_string = re.sub(r'\\U[0-9a-fA-F]{8}', '', json_string)
            cleaned_string = re.sub(r'\\x[0-9a-fA-F]{2}', '', cleaned_string)
            return cleaned_string
            
        try:
            if self.item.startup_name.strip() : # == "Groupe SYD" :
                # with self.lock_print:
                print(f"{self.item.Rang} {'@'*50}  {self.item.startup_name}  {'@'*50}")
                    
                if str(self.item.profiles).strip() != "nan" and self.item.profiles != None and self.item.profiles.lower() != 'none' and self.item.profiles != 'null' and item.profiles.strip() != '[]' and self.item.profiles.strip() != "":
                    
                    profiles = []
                    for i, profile in enumerate('}&&||&&'.join(item.profiles[1:-1].split('},')).split('&&||&&')):
                        profile = profile.replace('"', "'")
                        
                        profile = profile.replace("{'", '{"')
                        
                        profile = profile.replace("', '", '", "')
                        profile = profile.replace("\", '", '", "')
                        profile = profile.replace("', \"", '", "')
                        
                        profile = profile.replace("': '", '": "')
                        profile = profile.replace("': \"", '": "')
                        profile = profile.replace("\": '", '": "')
                        
                        profile = profile.replace("'}", '"}')
    
                        profile = profile.replace("'", "\'")
                        profile = profile.replace("\\'", "\'")
                        
                        profile = clean_invalid_escapes(profile)
                        
                        # print(f'{i} : {profile}')
                        
                        profile = json.loads(profile)
                        # print(f'{i} : {profile["profile_description"]}')
                        # print(f'*'*150)

                        profiles.append(profile)
                    
                    items = self.get_valid_items_from_profiles(profiles)
                        
                    # print(f'='*150)
                    # for i in items:
                    #     print(f'{i.founder_name} : {i.founder_description}')
                        
                else:
                    return {"status": False, "data": self.item }

            if items:
                return {"status": True, "data": items }
            else:
                return {"status": True, "data": self.item }
                
        except Exception as e:
            print(f"Errooooor at {self.item.startup_name}")
            print(e.args[0])
            ExceptionStorage(self.item, str(e))
            return {"status": False, "data": self.item }


    def is_founder_director(self, description):
        keywords = [
            "general director", "directeur général", "directrice générale",
            " CEO", " PDG", " CFO", "CEO ", "PDG ", "CFO ",
            "president", "président", "présidente",
            "founder", "fondateur", "fondatrice",
            "co-founder", "Co-fondatrice", "Co-fondateur",
            " CTO", "CTO ",
            "Chief",
            "HR director", "DRH", "directeur RH", "directrice RH",
            "partner", "associé", "associée",
            "owner",
            "Investor", "investeur", "Entrepreneur"
        ]
    
        # Exclude "product owner" explicitly
        if "product owner" in str(description).lower():
            return {"response": False}
    
        # Check if any keyword is in the description
        for keyword in keywords:
            if keyword.lower() in str(description).lower():
                return {"response": True}
        
        return {"response": False}

    def get_valid_items_from_profiles(self, profiles):
        profiles_for_openAI = []
        valid_profiles = []
        
        for profile in profiles:
            result=self.is_founder_director(profile["profile_description"])
            if result['response']:
                print(f'+++ valid profil : {profile["profile_description"]}')
                valid_profiles.append(profile)
            else:
                profiles_for_openAI.append(profile)
    
        profiles = profiles_for_openAI
        step = 50
        founder_profiles = []
        for i in range(0,len(profiles),step):
            chunk = [ f'{profile["person_name"]}, {profile["profile_description"]}' for profile in profiles[i:i+step]]
    
            result = self.foundersOpenAIClassification.predict(chunk)
            # display(chunk)
            # print(f'*'*150)
            
            # print('Founder profiles:')
            
            for name, value in result['content'].items():
                try:
                    if value:
                        profile = [profile for profile in profiles if profile['person_name'].strip() == name.strip()][0]
                        founder_profiles.append(profile)
                        print(f'--- valid profil : {profile["profile_description"]}')
                        # display(profile)
                        # print(f'*'*150)
                except Exception as e:
                    print(f'===> error at founder name : {name}')
                    ExceptionStorage(self.item, f'===> error at founder name : {name}')
            #print(f'$'*150)
    
        final_valid_profiles = valid_profiles + founder_profiles
        items = []
        for profile in final_valid_profiles:
            item_copy = copy.deepcopy(self.item)
            item_copy.founder_name = profile['person_name']
            item_copy.founder_description = profile['profile_description']
            item_copy.founder_profile_url = profile['profile_url']
            items.append(item_copy)
            
        return items
        
    def filter_Founder_Profiles_using_OpenAi(self, item):        
        self.item = item

        result = self.is_founder_director(self.item.founder_description)
        if result["response"]:
            self.item.valid_profile_description = True
            print(f'+'*150)
            print(f'{self.item.founder_description} : {result["response"]}')
            print(f'+'*150)
        else:
            result = self.filterFoundersOneByOneOpenAI.predict(self.item.founder_description)
            print(f'-'*150)
            print(f'{self.item.founder_description} : {result['content']}')
            print(f'-'*150)
            self.item.valid_profile_description = result['content']['response']
        
        return {"status": True, "data": self.item }
        
    ########################################################################################################