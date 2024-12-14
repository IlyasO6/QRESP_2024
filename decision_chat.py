import openai

# Configurar la API de OpenAI
openai.api_key = 'tu-api-key-aqui'

# Función para generar el prompt de la API de OpenAI para el escenario inicial de urgencias
def generar_prompt_urgencias(historial_clinico, pruebas_complementarias, sintomas):
    """
    Genera un prompt estructurado para la API de OpenAI basado en los datos del paciente
    y la valoración de urgencia.
    
    historial_clinico: diccionario con los datos clínicos del paciente.
    pruebas_complementarias: diccionario con los resultados de las pruebas.
    sintomas: lista de síntomas reportados por el paciente.
    
    Retorna la respuesta generada por la API (diagnóstico y tratamiento recomendado).
    """
    prompt = f"""
    Paciente con MPID. Historia clínica: {historial_clinico}.
    Resultados de pruebas complementarias: {pruebas_complementarias}.
    Sintomas reportados: {sintomas}.
    Realiza una valoración inicial y clasifica al paciente en uno de los siguientes escenarios clínicos:
    a) Diagnóstico concreto ≠ neumonía (devuelve tratamiento específico).
    b) Diagnóstico concreto de neumonía (distinción entre inmunosuprimidos e inmunocompetentes).
    c) No diagnóstico concreto (descartar TEP y realizar pruebas adicionales).
    """

    # Llamada a la API de OpenAI
    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        max_tokens=300
    )
    
    return response.choices[0].text.strip()

# Función para clasificar el escenario clínico según la respuesta de la API
def clasificar_escenario_clinico(respuesta_api):
    """
    Clasifica el escenario clínico según la respuesta de la API.
    
    respuesta_api: texto generado por la API que contiene el diagnóstico y tratamiento.
    
    Retorna el diagnóstico y las recomendaciones.
    """
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

# Función principal para gestionar los síntomas y la valoración
def gestionar_urgencias(sintomas, historial_clinico, pruebas_complementarias):
    """
    Gestiona la urgencia del paciente, genera el prompt, clasifica el escenario y devuelve
    el diagnóstico y tratamiento recomendado.
    
    sintomas: lista de síntomas reportados por el paciente.
    historial_clinico: diccionario con los datos clínicos del paciente.
    pruebas_complementarias: diccionario con los resultados de las pruebas realizadas.
    
    Retorna el diagnóstico final y las recomendaciones.
    """
    respuesta_api = generar_prompt_urgencias(historial_clinico, pruebas_complementarias, sintomas)
    clasificacion, recomendaciones = clasificar_escenario_clinico(respuesta_api)
    
    return clasificacion, recomendaciones

# Ejemplo de uso:
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
clasificacion, recomendaciones = gestionar_urgencias(sintomas_paciente, historial_clinico, pruebas_complementarias)
print(f"Clasificación: {clasificacion}")
print(f"Recomendaciones: {recomendaciones}")
