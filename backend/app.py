from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import json
from models import db, Video
from services.video_service import VideoService
from services.social_media_service import SocialMediaService
from config import Config
import time
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config.from_object(Config)

# Configurar CORS
CORS(app)

# Inicializar la base de datos
db.init_app(app)

# Servicios
video_service = VideoService()
social_service = SocialMediaService()

# Asegurar que la carpeta de uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Función robusta para inicializar la base de datos
def initialize_db():
    max_retries = 5
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            db.create_all()
            print("Database initialized successfully!")
            return
        except OperationalError as e:
            if "the database system is starting up" in str(e) and attempt < max_retries - 1:
                print(f"Database not ready, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to initialize database: {str(e)}")
                raise

# Crear las tablas si no existen con manejo de reintentos
with app.app_context():
    initialize_db()

# Configuración de archivos permitidos
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

# ... (el resto de las rutas permanecen iguales) ...

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)