import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_pubmed_articles() -> List[Dict]:
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    
    search_params = {
        "db": "pubmed",
        "term": "interstitial lung disease OR diffuse interstitial lung disease AND 2020:2024[dp]",
        "retmax": 5,
        "retmode": "xml",
        "api_key": "ca224e24f69d2a20d85b7f88618aa3dfb908"
    }

    try:
        response = requests.get(search_url, params=search_params)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        pmids = [id_elem.text for id_elem in root.findall(".//Id")]
        
        articles = []
        for pmid in pmids:
            fetch_params = {
                "db": "pubmed",
                "id": pmid,
                "rettype": "abstract",
                "retmode": "xml",
                "api_key": "ca224e24f69d2a20d85b7f88618aa3dfb908"
            }
            
            abstract_response = requests.get(fetch_url, params=fetch_params)
            abstract_response.raise_for_status()
            
            abstract_root = ET.fromstring(abstract_response.content)
            abstract = abstract_root.find(".//Abstract/AbstractText")
            title = abstract_root.find(".//ArticleTitle")
            
            if abstract is not None and title is not None:
                articles.append({
                    "pmid": pmid,
                    "title": title.text,
                    "abstract": abstract.text
                })
            
        return articles

    except requests.RequestException as e:
        logger.error(f"Error en la solicitud a PubMed: {e}")
        return []
    except ET.ParseError as e:
        logger.error(f"Error al analizar XML: {e}")
        return []
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return []

if __name__ == "__main__":
    articles = get_pubmed_articles()
    for article in articles:
        print(f"\nPMID: {article['pmid']}")
        print(f"Title: {article['title']}")
        print(f"Abstract: {article['abstract']}\n")
