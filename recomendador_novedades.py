from web_scraping import ArticleFetcher
import requests
import json
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovementAnalyzer:
    def __init__(self):
        self.api_key = "t8-Mzz5B4NpqZ3EfkywLN1rPZUbEcs9KJfacVOwylSZ9XngsUQF"
        self.api_base_url = "https://api.straico.com/v0"

    def process_articles(self, articles: Dict[str, List[Dict]]) -> str:
        """Procesa los artículos y genera recomendaciones usando Straico API."""
        articles_text = self._prepare_articles_text(articles)
        
        try:
            url = f'{self.api_base_url}/prompt/completion'
            
            payload = json.dumps({
                "model": "anthropic/claude-3.5-sonnet",
                "message": """Eres un experto en medicina pulmonar especializado en MPID. 
                Analiza los siguientes artículos científicos y proporciona recomendaciones 
                concretas para mejorar el algoritmo de tratamiento MPID actual.

                ARTÍCULOS A ANALIZAR:
                --------------------
                """ + articles_text + """

                Por favor, proporciona:
                1. Nuevos tratamientos o terapias identificadas
                2. Mejoras en protocolos de diagnóstico
                3. Factores pronósticos relevantes
                4. Biomarcadores importantes
                5. Criterios de evaluación de respuesta al tratamiento

                Estructura tu respuesta en secciones claramente definidas y 
                basa tus recomendaciones en la evidencia de los artículos analizados."""
            })
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, data=payload)
            if response.status_code == 201:  # Straico returns 201 for successful completion
                data = response.json()
                if data['success']:
                    return data['data']['completion']['choices'][0]['message']['content'].strip()
                else:
                    logger.error(f"API error: {data.get('error', 'Unknown error')}")
            else:
                logger.error(f"Error: Received status code {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Error al procesar con Straico API: {e}")
            return "Error al generar recomendaciones."

    def _prepare_articles_text(self, articles: Dict[str, List[Dict]]) -> str:
        """Prepara el texto de los artículos para el análisis."""
        text_parts = []
        
        for source, article_list in articles.items():
            for article in article_list:
                text_parts.append("\n=== Artículo ===")
                if article.get('title'):
                    text_parts.append(f"Título: {article['title']}")
                if article.get('abstract'):
                    text_parts.append(f"Resumen: {article['abstract']}")
                if article.get('full_text'):
                    text_parts.append(f"Texto completo: {article['full_text'][:1000]}...")
        
        return "\n".join(text_parts)

def main():
    # Obtener artículos
    fetcher = ArticleFetcher()
    articles = fetcher.get_all_articles()
    
    # Analizar y generar recomendaciones
    analyzer = ImprovementAnalyzer()
    recommendations = analyzer.process_articles(articles)
    
    print("\n=== Recomendaciones para Mejora del Algoritmo MPID ===\n")
    print(recommendations)

if __name__ == "__main__":
    main()
