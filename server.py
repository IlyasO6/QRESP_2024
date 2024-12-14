from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'clave_segura_2024'

class DataStore:
    def __init__(self):
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.perfil = self.cargar_datos('perfil.json')
        self.sintomas = self.cargar_datos('sintomas.json')
        self.pruebas = self.cargar_datos('pruebas.json')

    def cargar_datos(self, archivo):
        try:
            with open(f'{self.data_dir}/{archivo}', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def guardar_datos(self, datos, archivo):
        with open(f'{self.data_dir}/{archivo}', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)

db = DataStore()

# Rutas principales
@app.route('/')
def inicio():
    return redirect(url_for('main'))

@app.route('/main')
def main():
    return render_template('main.html', perfil=db.perfil)

@app.route('/editar_perfil')
def editar_perfil():
    return render_template('editar_perfil.html', perfil=db.perfil)

@app.route('/com_em_trobo')
def estado():
    return render_template('estado.html', sintomas=db.sintomas)

@app.route('/guia_urgencies')
def guia_urgencies():
    return render_template('guia_urgencies.html', pruebas=db.pruebas)

@app.route('/historial_proves')
def historial_proves():
    return render_template('historial_proves.html', pruebas=db.pruebas)

@app.route('/centres_medics')
def centres_medics():
    return render_template('centres_medics.html')

@app.route('/novetats')
def novetats():
    return render_template('novetats.html')

# API endpoints
@app.route('/api/guardar_perfil', methods=['POST'])
def guardar_perfil():
    datos = request.get_json()
    db.perfil.update(datos)
    db.guardar_datos(db.perfil, 'perfil.json')
    return jsonify({"status": "success"})

@app.route('/api/guardar_sintomas', methods=['POST'])
def guardar_sintomas():
    datos = request.get_json()
    fecha = datetime.now().strftime("%Y-%m-%d")
    db.sintomas[fecha] = datos
    db.guardar_datos(db.sintomas, 'sintomas.json')
    return jsonify({"status": "success"})

# Manejador de rutas antiguas
@app.route('/templates/<path:path>')
def handle_templates(path):
    routes_map = {
        'main.html': url_for('main'),
        'editar_perfil.html': url_for('editar_perfil'),
        'com_em_trobo.html': url_for('estado'),
        'guia_urgencies.html': url_for('guia_urgencies'),
        'historial_proves.html': url_for('historial_proves'),
        'centres_medics.html': url_for('centres_medics'),
        'novetats.html': url_for('novetats')
    }
    return redirect(routes_map.get(path, url_for('main')))

# Manejador de errores 404
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return redirect(url_for('main'))

if __name__ == '__main__':
    # Asegurarse de que existe el directorio de datos
    os.makedirs('data', exist_ok=True)
    
    print("Servidor iniciado en http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)