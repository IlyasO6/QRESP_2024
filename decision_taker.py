import requests
import json
import logging
import pymongo
from decision_sintomas import analizar_sintomas
from decision_urgencias import gestionar_urgencias
from get_data import db_retriever

connection_url = ""

db_retrieve = db_retriever(connection= connection_url)
db_retrieve.connect()

def tomar_decision_medica(card_number, sintomas, en_urgencias, pruebas_complementarias = "No hechas aún"):
    """
    Toma decisiones médicas basándose en si el paciente está en urgencias o no.
    
    Args:
        datos_medicos: Diccionario con la información médica del paciente
        sintomas: Lista de síntomas actuales
        en_urgencias: Boolean que indica si es caso de urgencias
    
    Returns:
        Dict con los resultados de la decisión
    """
    datos_medicos = db_retrieve.get_user("health_card_number", card_number)['medical_info']


    try:
        if en_urgencias:
            resultado = gestionar_urgencias(
                historial_clinico=datos_medicos,
                sintomas=sintomas,
                pruebas_complementarias=pruebas_complementarias
            )
            logging.info("Procesando caso de urgencias")
        else:
            resultado = analizar_sintomas(
                sintomas=sintomas,
                historial_clinico=datos_medicos,
            )
            logging.info("Procesando caso regular de síntomas")
            
        return resultado
        
    except Exception as e:
        logging.error(f"Error en la toma de decisión: {str(e)}")
        return {
            "estado": "error",
            "mensaje": str(e),
            "tipo_gestion": "urgencias" if en_urgencias else "sintomas"
        }

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración básica de logging
    logging.basicConfig(level=logging.INFO)
    
    sintomas_paciente = ["fiebre", "tos seca", "dificultad para respirar"]
    pruebas_complementarias = {
        "gasometria": "PaO2/FiO2 280", 
        "rx_torax": "infiltrados bilaterales"
    }
    
    # Ejemplo de uso para caso normal
    resultado_normal = tomar_decision_medica(card_number= "11", 
                                             sintomas=sintomas_paciente, 
                                             en_urgencias=False
                                             )
    print("Resultado caso normal:", resultado_normal)
    
    # Ejemplo de uso para caso de urgencias
    resultado_urgencia = tomar_decision_medica(card_number= "12", 
                                               sintomas=sintomas_paciente, 
                                               en_urgencias=True, 
                                               pruebas_complementarias= pruebas_complementarias
                                               )
    print("Resultado caso urgencia:", resultado_urgencia)


db_retrieve.close_connection()
