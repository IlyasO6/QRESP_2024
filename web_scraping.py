import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArticleFetcher:
    def __init__(self):
        self.api_key = "ca224e24f69d2a20d85b7f88618aa3dfb908"
        self.ild_terms = [
            "Interstitial lung disease (ILD)",
            "Pulmonary fibrosis",
            # ...existing terms...
            "Genetic predisposition in ILD"
        ]
        # Create search pattern for case-insensitive matching
        self.search_pattern = re.compile('|'.join(map(re.escape, self.ild_terms)), re.IGNORECASE)

    def _contains_ild_terms(self, text: str) -> bool:
        """Verifica si el texto contiene alguno de los términos ILD."""
        if not text:
            return False
        return bool(self.search_pattern.search(text))

    def get_all_articles(self) -> Dict[str, List[Dict]]:
        """Obtiene artículos de ambas fuentes."""
        return {
            "pubmed": self.get_pubmed_articles(),
            "bmc": self.get_bmc_articles()
        }

    def get_pubmed_articles(self) -> List[Dict]:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        
        # Modificar la búsqueda para incluir todos los términos ILD
        search_terms = ' OR '.join(f'"{term}"' for term in self.ild_terms)
        search_params = {
            "db": "pubmed",
            "term": f"({search_terms}) AND 2020:2024[dp]",
            "retmax": 5,
            "retmode": "xml",
            "api_key": self.api_key
        }

        try:
            response = requests.get(search_url, params=search_params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            pmids = [id_elem.text for id_elem in root.findall(".//Id")]
            
            articles = []
            for pmid in pmids:
                fetch_params = {
                    "db": "pubmed",
                    "id": pmid,
                    "rettype": "full",
                    "retmode": "xml",
                    "api_key": self.api_key
                }
                
                article_response = requests.get(fetch_url, params=fetch_params)
                article_response.raise_for_status()
                
                article_root = ET.fromstring(article_response.content)
                article = article_root.find(".//Article")
                
                if article is not None:
                    article_data = self._extract_pubmed_data(article, pmid, article_root)
                    # Solo agregar si contiene términos relevantes
                    if self._contains_ild_terms(article_data['title']) or \
                       self._contains_ild_terms(article_data['abstract']) or \
                       self._contains_ild_terms(article_data['full_text']):
                        articles.append(article_data)
            
            return articles

        except Exception as e:
            logger.error(f"Error en PubMed: {e}")
            return []

    def get_bmc_articles(self) -> List[Dict]:
        search_url = "https://www.biomedcentral.com/search"
        # Usar términos ILD para la búsqueda
        search_terms = ' OR '.join(self.ild_terms)
        search_params = {"query": search_terms, "page": 1}

        try:
            response = requests.get(search_url, params=search_params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            articles = []
            
            for result in soup.find_all("div", class_="search-result__content"):
                article_data = self._extract_bmc_data(result)
                if article_data and (self._contains_ild_terms(article_data['title']) or \
                   self._contains_ild_terms(article_data['summary'])):
                    articles.append(article_data)
            
            return articles

        except Exception as e:
            logger.error(f"Error en BMC: {e}")
            return []

    def _extract_pubmed_data(self, article, pmid, root) -> Dict:
        return {
            "source": "PubMed",
            "pmid": pmid,
            "title": self._get_xml_text(article.find(".//ArticleTitle")),
            "abstract": self._get_xml_text(article.find(".//Abstract/AbstractText")),
            "journal": self._get_xml_text(article.find(".//Journal/Title")),
            "publication_date": self._get_publication_date(article.find(".//PubDate")),
            "authors": self._get_authors(article.find(".//AuthorList")),
            "keywords": self._get_keywords(root.findall(".//Keyword")),
            "doi": self._get_xml_text(root.find(".//ArticleId[@IdType='doi']")),
            "full_text": self._get_full_text(article)
        }

    def _extract_bmc_data(self, result) -> Dict:
        title_elem = result.find("h2", class_="search-result__title")
        summary_elem = result.find("div", class_="search-result__summary")
        
        if title_elem and summary_elem:
            return {
                "source": "BMC",
                "title": title_elem.get_text(strip=True),
                "summary": summary_elem.get_text(strip=True)
            }
        return None

    # Mantener los métodos auxiliares existentes
    def _get_xml_text(self, element):
        return element.text if element is not None else None

    def _get_publication_date(self, pub_date):
        # ... existing code from get_publication_date ...
        pass

    def _get_authors(self, author_list):
        # ... existing code from get_authors ...
        pass

    def _get_keywords(self, keywords):
        # ... existing code from get_keywords ...
        pass

    def _get_full_text(self, article):
        if article is None:
            return None
        text_elements = article.findall(".//Text") + article.findall(".//Paragraph")
        return "\n".join([elem.text for elem in text_elements if elem.text is not None])

if __name__ == "__main__":
    fetcher = ArticleFetcher()
    all_articles = fetcher.get_all_articles()
    
    print("\nPubMed Articles:")
    for article in all_articles["pubmed"]:
        print("\n" + "="*50)
        print(f"Source: {article['source']}")
        print(f"PMID: {article['pmid']}")
        print(f"Title: {article['title']}")
        print(f"Authors: {', '.join(article['authors']) if article['authors'] else 'N/A'}")
        print(f"Journal: {article['journal']}")
        print(f"Date: {article['publication_date']}")
        print(f"DOI: {article['doi']}")
        print(f"Abstract: {article['abstract']}")
        print(f"Full Text: {article['full_text']}")
    
    print("\nBMC Articles:")
    for article in all_articles["bmc"]:
        print("\n" + "="*50)
        print(f"Source: {article['source']}")
        print(f"Title: {article['title']}")
        print(f"Summary: {article['summary']}")

