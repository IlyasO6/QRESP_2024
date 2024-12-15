from web_scraping import ArticleFetcher
import requests
import json
import logging
from typing import List, Dict
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovementAnalyzer:
    def __init__(self):
        self.api_key = "t8-Mzz5B4NpqZ3EfkywLN1rPZUbEcs9KJfacVOwylSZ9XngsUQF"
        self.api_base_url = "https://api.straico.com/v0"
        self.categories = {
            "1": "treatments",
            "2": "diagnostic_procedures",
            "3": "risk_factors",
            "4": "symptoms",
            "5": "recommendations"
        }

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
            
            # Si hay error, devolver mensaje en lugar de None
            return "No se pudieron generar recomendaciones. Por favor, intente de nuevo."

        except Exception as e:
            logger.error(f"Error al procesar con Straico API: {e}")
            return "Error al generar recomendaciones. Por favor, intente de nuevo."

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

    def save_to_med_data(self, recommendation: str, category: str) -> bool:
        """Guarda una recomendación en med_data.json."""
        try:
            # Cargar datos existentes
            with open('med_data.json', 'r', encoding='utf-8') as f:
                med_data = json.load(f)
            
            # Añadir nueva recomendación si no existe
            if category in med_data:
                if isinstance(med_data[category], list):
                    if recommendation not in med_data[category]:
                        med_data[category].append(recommendation)
                    else:
                        return False
                else:
                    med_data[category] = [recommendation]
            else:
                med_data[category] = [recommendation]

            # Guardar datos actualizados
            with open('med_data.json', 'w', encoding='utf-8') as f:
                json.dump(med_data, f, indent=4, ensure_ascii=False)
            return True

        except Exception as e:
            logger.error(f"Error al guardar en med_data.json: {e}")
            return False

    def interactive_save_recommendations(self, recommendations: str):
        """Permite al usuario guardar recomendaciones en med_data.json."""
        print("\n=== ¿Desea guardar alguna recomendación en la base de datos? ===")
        print("Las recomendaciones guardadas serán consideradas en futuras consultas.")
        print("\nCategorías disponibles:")
        for key, value in self.categories.items():
            print(f"{key}. {value.replace('_', ' ').title()}")
        
        while True:
            print("\nOpciones:")
            print("- Ingrese 'número_categoría:texto' para guardar una recomendación")
            print("- Ingrese 'q' para salir")
            
            user_input = input("\nIngrese su selección: ").strip()
            
            if user_input.lower() == 'q':
                break
                
            try:
                category_num, text = user_input.split(':', 1)
                if category_num in self.categories:
                    category = self.categories[category_num]
                    if self.save_to_med_data(text.strip(), category):
                        print(f"✓ Recomendación guardada en {category}")
                    else:
                        print("× La recomendación ya existe o hubo un error")
                else:
                    print("× Categoría no válida")
            except ValueError:
                print("× Formato incorrecto. Use 'número_categoría:texto'")

def main():
    # Obtener artículos
    fetcher = ArticleFetcher()
    articles = fetcher.get_all_articles()
    
    # Analizar y generar recomendaciones
    analyzer = ImprovementAnalyzer()
    recommendations = analyzer.process_articles(articles)
    
    if recommendations:
        print("\n=== Recomendaciones para Mejora del Algoritmo MPID ===\n")
        print(recommendations)
        
        while True:
            try:
                respuesta = input("\n¿Desea guardar alguna de estas recomendaciones en la base de datos? (s/n): ").lower().strip()
                if respuesta == 's':
                    print("\nProcediendo al guardado de recomendaciones...")
                    analyzer.interactive_save_recommendations(recommendations)
                    break
                elif respuesta == 'n':
                    print("\nNo se guardarán recomendaciones. Programa finalizado.")
                    break
                else:
                    print("\nPor favor, ingrese 's' para sí o 'n' para no.")
            except Exception as e:
                print(f"\nError al procesar la respuesta: {e}")
                print("Por favor, intente de nuevo.")
    else:
        print("No se obtuvieron recomendaciones para procesar.")

if __name__ == "__main__":
    main()
