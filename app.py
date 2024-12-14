from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
import qrcode
import io
import os
import random
from bson.objectid import ObjectId  # Asegúrate de importar esto
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json


app = Flask(__name__)
app.secret_key = os.urandom(24)

port = random.randint(1000,9999)

# Configura la conexión con MongoDB Atlas
client = MongoClient("mongodb+srv://carlosnieves:Uo7pzJh5iDvlS37M@cluster0.9t4o9.mongodb.net/")
db = client["dbqr"]
users_collection = db["dbqrcol"]
scraped_data_collection = db["scraped_data"]

# Ruta principal (página de inicio)



@app.route("/home")
def home():
    return render_template("home.html")


def scrape_health_data():
    """
    Función para scrapear datos de un sitio web y capturar toda la información relevante.
    """
    scraped_results = []

    # URL del sitio a scrapear (puedes reemplazarla con otro sitio real)
    url = "https://www.ncbi.nlm.nih.gov/pmc/"

    try:
        # Realizar la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error si la solicitud falla

        # Analizar el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer encabezados, párrafos y enlaces
        for section in soup.find_all(['h1', 'h2', 'h3', 'p', 'a']):
            text = section.text.strip() if section.text else "No content"
            link = section.get('href') if section.name == 'a' else None

            scraped_item = {
                "source_url": url,
                "tag": section.name,
                "content": text,
                "link": link,
                "scraped_at": datetime.now()
            }
            scraped_results.append(scraped_item)

    except Exception as e:
        print(f"Error al scrapear la página: {e}")

    return scraped_results


# Ruta para realizar web scraping
@app.route('/scrape_health_data', methods=['GET'])
def scrape_and_store_data():
    """
    Ruta para realizar scraping y guardar los datos en MongoDB.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        # Llamar a la función de scraping
        scraped_data = scrape_health_data()

        if scraped_data:
            # Insertar los datos en la base de datos
            result = scraped_data_collection.insert_many(scraped_data)

            return jsonify({
                "message": f"Scrapeados y guardados {len(result.inserted_ids)} elementos",
                "data_ids": [str(_id) for _id in result.inserted_ids]
            })
        else:
            return jsonify({"message": "No se encontraron datos para scrapear"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ruta para consultar datos scrapeados
@app.route('/scraped_health_data', methods=['GET'])
def get_scraped_data():
    """
    Ruta para obtener datos scrapeados previamente desde MongoDB.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        # Obtener todos los datos scrapeados (ordenados por fecha)
        scraped_data = list(scraped_data_collection.find().sort('scraped_at', -1))

        # Convertir ObjectId y timestamps a formatos legibles
        for item in scraped_data:
            item['_id'] = str(item['_id'])
            item['scraped_at'] = item['scraped_at'].isoformat()

        return jsonify(scraped_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/scraped_data', methods=['GET'])
def visualize_scraped_data():
    """
    Página para mostrar los datos scrapeados en formato tabla.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Obtener todos los datos scrapeados desde MongoDB
    scraped_data = list(scraped_data_collection.find().sort('scraped_at', -1))

    # Convertir ObjectId y formatear fechas
    for item in scraped_data:
        item['_id'] = str(item['_id'])
        item['scraped_at'] = item['scraped_at'].strftime('%Y-%m-%d %H:%M:%S')

    return render_template('scraped_data.html', data=scraped_data)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Captura los datos del formulario
        username = request.form.get("full_name")  # Renombramos full_name como username
        health_card_number = request.form.get("health_card_number")  # Consideramos health_card_number como único identificador
        password = request.form.get("password")  # Agrega un campo de contraseña al formulario si falta

        # Información médica y personal
        medical_info = {
            "age": request.form.get("age"),
            "sex": request.form.get("sex"),
            "blood_type": request.form.get("blood_type"),
            "diseases": request.form.get("diseases"),
            "medications": request.form.get("medications"),
            "MPID": request.form.get("MPID"),
            "base_treatment": request.form.get("base_treatment"),
            "immunosuppression": request.form.get("immunosuppression"),
            "comorbidities": request.form.get("comorbidities"),
            "smoker": request.form.get("smoker"),
            "physical_activity": request.form.get("physical_activity"),
            "alcohol_consumption": request.form.get("alcohol_consumption"),
            "asma": request.form.get("asma"),
        }

        # Validar campos requeridos
        required_fields = [username, health_card_number, password]
        if not all(required_fields):
            return "Por favor completa todos los campos obligatorios", 400

        # Verifica si el usuario ya está registrado por health_card_number (email en tu lógica actual)
        if users_collection.find_one({"health_card_number": health_card_number}):
            return "El número de tarjeta sanitaria ya está registrado", 400

        # Hash de la contraseña para mayor seguridad
        hashed_password = generate_password_hash(password)

        # Inserta el usuario en la base de datos
        user = {
            "username": username,
            "health_card_number": health_card_number,
            "password": hashed_password,
            "medical_info": medical_info,
        }
        result = users_collection.insert_one(user)

        session["user_id"] = str(result.inserted_id)
        session["username"] = username

        # Genera el QR del usuario
        user_id = str(result.inserted_id)
        qr_code = qrcode.make(f"http://localhost:{port}/user/{user_id}")
        qr_io = io.BytesIO()
        qr_code.save(qr_io, "PNG")
        qr_io.seek(0)

        # Guarda el QR en un archivo
        with open(f"static/qrcodes/{user_id}.png", "wb") as qr_file:
            qr_file.write(qr_io.read())

        # Redirige al inicio de sesión después del registro
        return redirect(url_for("dashboard"))

    # Renderiza el formulario de registro
    return render_template("register.html")


# Ruta de login

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        health_card_number = request.form.get('health_card_number')
        password = request.form.get('password')

        if not health_card_number or not password:
            flash('Por favor completa todos los campos.', 'error')
            return redirect(url_for('login'))
        
        # Buscar al usuario en la base de datos
        user = users_collection.find_one({"health_card_number": health_card_number})
        
        # Verificar si el usuario existe y la contraseña es correcta
        # Use check_password_hash instead of bcrypt
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])  # Convertir _id a cadena
            session["username"] = user["username"]
            return redirect(url_for('dashboard'))  # Redirigir al dashboard
        else:
            flash("Número de tarjeta sanitaria o contraseña incorrectos.", "error")  # Mensaje de error
            return redirect(url_for("login"))
            
    return render_template('login.html')

# Ruta de dashboard (área privada)
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')  # Obtener el user_id de la sesión
    if not user_id:
        return redirect(url_for('login'))  # Redirigir al login si no hay sesión activa
    
    # Convertir el user_id de vuelta a ObjectId
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return "Usuario no encontrado."

    # Construir la ruta del código QR
    qr_code_path = f"qrcodes/{user_id}.png"

    # Lógica para mostrar el dashboard
    return render_template('dashboard.html', user=user, qr_code_path=qr_code_path)



# Ruta para mostrar la información del usuario a través del QR
@app.route("/user/<user_id>")
def user_info(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return "Usuario no encontrado", 404

    # Mostrar solo la información médica
    return render_template("user_info.html", medical_info=user["medical_info"], username=user["username"])

@app.route('/medical_data/<user_id>')
def medical_data(user_id):
    # Verificar si el usuario está autenticado
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))
    
    # Buscar el usuario
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return "Usuario no encontrado", 404

    # Mostrar información médica
    return render_template('medical_data.html', 
                           medical_data=user.get('medical_info', {}), 
                           user=user)

# Ruta para logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    # Crea el directorio para guardar los códigos QR si no existe
    if not os.path.exists("static/qrcodes"):
        os.makedirs("static/qrcodes")

    app.run(debug=True, port=port)
