from datetime import datetime
from flask import Flask, render_template, request, jsonify
from turnos_lib import optimize_schedule
import hashlib
import json
import os

SAVE_PATH = "saved_schedules"  # Carpeta donde se guardarán las programaciones

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

app = Flask(__name__)


def file_content_hash(filepath):
    """Retorna un hash basado en el contenido del archivo."""
    with open(filepath, 'r') as f:
        file_content = f.read()
        parsed_content = json.loads(file_content)
        return hashlib.md5(json.dumps(parsed_content, sort_keys=True).encode()).hexdigest()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    schedule = request.json

    # Comprobar si el horario está vacío
    if not schedule:
        return jsonify(success=False, message="La programación está vacía. No se guardará.")

    # Calcular el hash del horario recibido
    current_schedule_hash = hashlib.md5(json.dumps(schedule, sort_keys=True).encode()).hexdigest()

    # Verificar contra los hashes de archivos existentes
    for filename in os.listdir(SAVE_PATH):
        filepath = os.path.join(SAVE_PATH, filename)
        if file_content_hash(filepath) == current_schedule_hash:
            return jsonify(success=False, message="Esta programación ya ha sido guardada previamente.")

    # Si no se encontró coincidencia, guardar el archivo
    filename = "turnos_" + datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + ".json"
    filepath = os.path.join(SAVE_PATH, filename)

    with open(filepath, 'w') as f:
        json.dump(schedule, f, indent=4)

    return jsonify(success=True, message="Programación guardada exitosamente!")


@app.route('/load_file_schedule', methods=['POST'])
def load_file_schedule():
    filename = request.json.get('filename')
    if not filename:
        return jsonify(success=False, message="Nombre de archivo no proporcionado.")

    filepath = os.path.join(SAVE_PATH, filename)
    if not os.path.exists(filepath):
        return jsonify(success=False, message="El archivo no existe.")

    with open(filepath, 'r') as f:
        schedule = json.load(f)

    return jsonify(success=True, data=schedule)


@app.route('/list_schedules', methods=['GET'])
def list_schedules():
    files = os.listdir(SAVE_PATH)
    files.sort(reverse=True)  # Ordena los archivos del más reciente al más antiguo
    return jsonify(files)


@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    names = data['names']

    optimized_schedule = optimize_schedule(names, generations=200)
    return jsonify(optimized_schedule)


if __name__ == '__main__':
    app.run(debug=True)
