import openai
import json

import openai
import json

# Configura tu API Key
openai.api_key = ""

# Cargar los datos "raw" del archivo JSON
with open("raw_data.json", "r") as file:
    raw_data = json.load(file)

# Función para limpiar un solo registro usando ChatGPT
def clean_data(record):
    # Crea el prompt para la limpieza
    prompt = f"""
    Limpia y corrige el siguiente registro JSON. Asegúrate de:
    - Quitar espacios en blanco innecesarios.
    - Estandarizar formatos de correo electrónico (todo en minúsculas).
    - Estandarizar formatos de fecha (YYYY-MM-DD).
    - Corregir errores obvios en los datos (si es posible).
    - Completar campos faltantes con "N/A" si no hay información disponible.

    Registro:
    {json.dumps(record, indent=2)}

    Devuelve el registro limpio en formato JSON.
    """
    try:
        # Llama a la API de ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        # Extraer la respuesta de ChatGPT
        cleaned_data = response['choices'][0]['message']['content']
        return json.loads(cleaned_data)  # Convertir la respuesta a JSON
    except Exception as e:
        print(f"Error al limpiar registro: {e}")
        return None

# Procesar todos los registros
cleaned_data = []
for record in raw_data:
    cleaned_record = clean_data(record)
    if cleaned_record:
        cleaned_data.append(cleaned_record)

# Guardar los datos limpios en un nuevo archivo JSON
with open("cleaned_data.json", "w") as file:
    json.dump(cleaned_data, file, indent=2)

print("Datos limpiados y guardados en 'cleaned_data.json'")
