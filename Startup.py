class Startup:
    def __init__(self):
        self.startup_name = None
        self.startup_amount_invested = None
        self.startup_article_publication_date = None
        self.startup_more_inf_url = None
        self.startup_levée_de_fonds = None
        self.startup_founders = None
        self.startup_Number_of_employees = None
        self.startup_web_site_url = None
        self.startup_right_web_site_url = None
        self.startup_valid_web_site_url = None
        self.startup_facebook_url = None
        self.startup_instagram_url = None
        self.startup_linkedin_url = None
        self.startup_phone = None
        self.startup_email = None
        self.startup_address = None
        self.startup_phrasechoc = None
        
    def init_from_dic(self, dic):
        self.startup_name = dic.get('startup_name')
        self.startup_amount_invested = dic.get('startup_amount_invested')
        self.startup_article_publication_date = dic.get('startup_article_publication_date')
        self.startup_more_inf_url = dic.get('startup_more_inf_url')
        self.startup_levée_de_fonds = dic.get('startup_levée_de_fonds')
        self.startup_founders = dic.get('startup_founders')
        self.startup_Number_of_employees = dic.get('startup_Number_of_employees')
        self.startup_web_site_url = dic.get('startup_web_site_url')
        self.startup_right_web_site_url = dic.get('startup_right_web_site_url')
        self.startup_valid_web_site_url = dic.get('startup_valid_web_site_url')
        self.startup_facebook_url = dic.get('startup_facebook_url')
        self.startup_instagram_url = dic.get('startup_instagram_url')
        self.startup_linkedin_url = dic.get('startup_linkedin_url')
        self.startup_phone = dic.get('startup_phone')
        self.startup_email = dic.get('startup_email')
        self.startup_address = dic.get('startup_address')
        self.startup_phrasechoc = dic.get('startup_phrasechoc')
        
    def __str__(self):
        return f'startup_name = {self.startup_name}\nstartup_amount_invested = {self.startup_amount_invested}\nstartup_article_publication_date = {self.startup_article_publication_date}\nstartup_more_inf_url = {self.startup_more_inf_url}\nstartup_levée_de_fonds = {self.startup_levée_de_fonds}\nstartup_founders = {self.startup_founders}\nstartup_Number_of_employees = {self.startup_Number_of_employees}\nstartup_web_site_url = {self.startup_web_site_url}\nstartup_right_web_site_url = {self.startup_right_web_site_url}\nstartup_valid_web_site_url = {self.startup_valid_web_site_url}\nstartup_facebook_url = {self.startup_facebook_url}\nstartup_instagram_url = {self.startup_instagram_url}\nstartup_linkedin_url = {self.startup_linkedin_url}\nstartup_phone = {self.startup_phone}\nstartup_email = {self.startup_email}\nstartup_address = {self.startup_address}\nstartup_phrasechoc = {self.startup_phrasechoc}\n'
