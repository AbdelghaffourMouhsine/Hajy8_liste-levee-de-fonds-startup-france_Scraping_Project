from bs4 import BeautifulSoup

class LinkProcessing :
    def __init__(self):
        self.max_len_link_name = 6
        
    def extract_links(self, contenu_html):
        soup = BeautifulSoup(contenu_html, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            links.append((href, text))
        return links

    def remove_empty_links(self, links):
        cleaned_links = [(href, text) for href, text in links if href.strip() not in ("#", "")]
        return cleaned_links

    def filter_valid_name_links(self, links):
        cleaned_links = [(href, text) for href, text in links if text.strip() and len(text.split()) <= self.max_len_link_name]
        return cleaned_links

    def preprocess_links(self, contenu_html):
        links = self.extract_links(contenu_html)
        cleaned_links = self.remove_empty_links(links)
        cleaned_links = self.filter_valid_name_links(cleaned_links)
        return cleaned_links
