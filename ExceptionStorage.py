import csv

class ExceptionStorage:
    def __init__(self, startup, error ,file_path='results/exceptions_1'):
        self.file_path = f"{file_path}.csv"
        self.fieldnames = ['startup_name','startup_amount_invested','startup_article_publication_date','startup_more_inf_url','startup_levée_de_fonds','startup_founders','startup_Number_of_employees','startup_web_site_url','startup_right_web_site_url','startup_valid_web_site_url','startup_linkedin_url','startup_facebook_url','startup_instagram_url','startup_phone','startup_email','startup_address','startup_phrasechoc', 'error']
        
        self.file = open(self.file_path, 'a', newline='', encoding='utf-8-sig')
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        
        # Check if the file is empty, then write the header
        if self.file.tell() == 0:
            self.writer.writeheader()
            
        self.insert_item(startup, error)
        self.close_file()
        
    def insert_item(self, startup, error):
        data = {
            'startup_name' : startup.startup_name, 
            'startup_amount_invested' : startup.startup_amount_invested, 
            'startup_article_publication_date' : startup.startup_article_publication_date,
            'startup_more_inf_url' : startup.startup_more_inf_url, 
            'startup_levée_de_fonds' : startup.startup_levée_de_fonds, 
            'startup_founders' : startup.startup_founders,
            'startup_Number_of_employees' : startup.startup_Number_of_employees, 
            'startup_web_site_url' : startup.startup_web_site_url, 
            'startup_right_web_site_url' : startup.startup_right_web_site_url, 
            'startup_valid_web_site_url' : startup.startup_valid_web_site_url, 
            'startup_linkedin_url' : startup.startup_linkedin_url, 
            'startup_facebook_url' : startup.startup_facebook_url, 
            'startup_instagram_url' : startup.startup_instagram_url, 
            'startup_phone' : startup.startup_phone,
            'startup_email' : startup.startup_email,
            'startup_address' : startup.startup_address,
            'startup_phrasechoc' : startup.startup_phrasechoc,
            'error' : error
        }
        self.writer.writerow(data)
        
    def insert_startups(self, startups):
        for startup in startups:
            self.insert_startup(startup)
            
    def close_file(self):
        self.file.close()