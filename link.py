from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para session

# Estructura para almacenar datos (en producción usarías una base de datos)
DATOS_USUARIO = {
    'perfil': {},
    'sintomas': {}
}

# Rutas principales
@app.route('/')
def inicio():
    return render_template('main.html', perfil=DATOS_USUARIO['perfil'])

@app.route('/templates/main.html')
def main():
    return render_template('main.html', perfil=DATOS_USUARIO['perfil'])

@app.route('/templates/editar_perfil.html')
def editar_perfil():
    return render_template('editar_perfil.html', perfil=DATOS_USUARIO['perfil'])

@app.route('/templates/com_em_trobo.html')
def estado():
    return render_template('estado.html', sintomas=DATOS_USUARIO['sintomas'])

# Rutas para el resto de páginas
@app.route('/templates/guia_urgencies.html')
def guia_urgencies():
    return render_template('guia_urgencies.html')

@app.route('/templates/historial_proves.html')
def historial_proves():
    return render_template('historial_proves.html')

@app.route('/templates/centres_medics.html')
def centres_medics():
    return render_template('centres_medics.html')

# Endpoints para guardar datos
@app.route('/guardar_perfil', methods=['POST'])
def guardar_perfil():
    datos = request.get_json()
    DATOS_USUARIO['perfil'].update(datos)
    guardar_datos()
    return jsonify({"status": "success"})

@app.route('/guardar_sintomas', methods=['POST'])
def guardar_sintomas():
    datos = request.get_json()
    fecha = datetime.now().strftime("%Y-%m-%d")
    if 'sintomas' not in DATOS_USUARIO:
        DATOS_USUARIO['sintomas'] = {}
    DATOS_USUARIO['sintomas'][fecha] = datos
    guardar_datos()
    return jsonify({"status": "success"})

# Funciones auxiliares para persistencia de datos
def guardar_datos():
    """Guarda los datos en un archivo JSON"""
    with open('datos_usuario.json', 'w', encoding='utf-8') as f:
        json.dump(DATOS_USUARIO, f, ensure_ascii=False, indent=4)

def cargar_datos():
    """Carga los datos desde el archivo JSON si existe"""
    try:
        with open('datos_usuario.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'perfil': {}, 'sintomas': {}}

# Inicialización de datos
DATOS_USUARIO.update(cargar_datos())

if __name__ == '__main__':
    # Configuración para desarrollo
    app.debug = True
    # Host '0.0.0.0' permite acceso desde cualquier IP
    app.run(host='0.0.0.0', port=5000)
