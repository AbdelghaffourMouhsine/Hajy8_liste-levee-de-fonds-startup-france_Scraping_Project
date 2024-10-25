import csv

class StartupStorage:
    def __init__(self, file_path, value=None):
        self.file_path = f"{file_path}.csv"
        self.fieldnames = ['Rang','startup_name','startup_amount_invested','startup_article_publication_date','startup_more_inf_url','startup_levée_de_fonds','startup_founders','startup_Number_of_employees','startup_web_site_url','startup_right_web_site_url','startup_valid_web_site_url','startup_linkedin_url','startup_facebook_url','startup_instagram_url','startup_phone','startup_email','startup_address','startup_phrasechoc','profiles','founder_name','founder_description','founder_profile_url']
        
        self.file = open(self.file_path, 'a', newline='', encoding='utf-8-sig')
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        
        # Check if the file is empty, then write the header
        if self.file.tell() == 0:
            self.writer.writeheader()

        if value:
            if type(value) == list:
                self.insert_startups(value)
            else:
                self.insert_startup(value)
            self.close_file()
            
    def insert_startup(self, startup):
        data = {
            'Rang' : startup.Rang,
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
            'profiles' : startup.profiles,
            'founder_name' : startup.founder_name,
            'founder_description' : startup.founder_description,
            'founder_profile_url' : startup.founder_profile_url
        }
        self.writer.writerow(data)
        
    def insert_startups(self, startups):
        for startup in startups:
            try:
                if type(startup) == list:
                    self.insert_startups(startup)
                else:
                    self.insert_startup(startup)
            except Exception as e:
                print('error in insert_startups : ',e)
            
    def close_file(self):
        self.file.close()