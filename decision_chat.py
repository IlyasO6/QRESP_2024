import requests
import json

# Reemplazar con tu clave API de Straico
api_key = "tu_api_key_de_straico"

# Función para generar el prompt para Straico
def generar_prompt_urgencias(historial_clinico, pruebas_complementarias="No hechas aún", sintomas="Sin especificar"):
    prompt = f"""
    Paciente con MPID. Historia clínica: {historial_clinico}.
    Resultados de pruebas complementarias: {pruebas_complementarias}.
    Sintomas reportados: {sintomas}.
    Realiza una valoración inicial y clasifica al paciente en uno de los siguientes escenarios clínicos:
    a) Diagnóstico concreto ≠ neumonía (devuelve tratamiento específico).
    b) Diagnóstico concreto de neumonía (distinción entre inmunosuprimidos e inmunocompetentes).
    c) No diagnóstico concreto (descartar TEP y realizar pruebas adicionales).
    """
    return prompt

# Función para obtener la respuesta de la API de Straico
def obtener_respuesta_straico(prompt):
    url = 'https://api.straico.com/v1/completion'  # Endpoint de ejemplo
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "text-davinci-003",  # Reemplaza con el modelo adecuado según la API de Straico
        "prompt": prompt,
        "max_tokens": 300,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['text']
    else:
        print(f"Error: {response.status_code}")
        return None

# Función para clasificar el escenario clínico según la respuesta
def clasificar_escenario_clinico(respuesta_api):
    if "neumonía" in respuesta_api:
        if "inmunosuprimido" in respuesta_api:
            return "Neumonía en inmunosuprimido", respuesta_api
        elif "inmunocompetente" in respuesta_api:
            return "Neumonía en inmunocompetente", respuesta_api
    elif "diagnóstico concreto" in respuesta_api:
        return "Diagnóstico concreto ≠ neumonía", respuesta_api
    elif "no diagnóstico concreto" in respuesta_api:
        return "No diagnóstico concreto", respuesta_api
    else:
        return "Resultado indeterminado", respuesta_api

# Función principal
def gestionar_urgencias(historial_clinico, sintomas="Sin especificar", pruebas_complementarias="No hechas aún"):
    prompt = generar_prompt_urgencias(historial_clinico, pruebas_complementarias, sintomas)
    respuesta_api = obtener_respuesta_straico(prompt)
    if respuesta_api:
        clasificacion, recomendaciones = clasificar_escenario_clinico(respuesta_api)
        return clasificacion, recomendaciones
    return "Error al obtener respuesta", ""

# Ejemplo de uso
sintomas_paciente = ["fiebre", "tos seca", "dificultad para respirar"]
historial_clinico = {
    "tipo_MPID": "UIP", 
    "cronicidad": "alta", 
    "tratamiento_base": "corticosteroides",
    "estado_inmunitario": "bajo",  # Inmunosuprimido
    "comorbilidades": ["hipertensión"]
}
pruebas_complementarias = {
    "gasometria": "PaO2/FiO2 280", 
    "rx_torax": "infiltrados bilaterales"
}

# Ejecutar el sistema de urgencias
clasificacion, recomendaciones = gestionar_urgencias(historial_clinico, sintomas_paciente, pruebas_complementarias)
print(f"Clasificación: {clasificacion}")
print(f"Recomendaciones: {recomendaciones}")
