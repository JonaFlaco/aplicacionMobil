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

# Crear la aplicación Flask con configuración explícita de archivos estáticos
app = Flask(__name__, 
           static_folder='static',
           static_url_path='/static',
           template_folder='templates')

app.config.from_object(Config)

# Configurar CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost", "http://localhost:80", "http://localhost:5000", "http://localhost:5500"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

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

@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Obtener lista de videos"""
    try:
        search = request.args.get('search', '')
        tag = request.args.get('tag', '')
        sort_by = request.args.get('sort_by', 'date')
        order = request.args.get('order', 'desc')
        
        videos = video_service.get_videos(search, tag, sort_by, order)
        return jsonify({'data': videos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos', methods=['POST'])
def upload_video():
    """Subir un nuevo video"""
    try:
        print("🔍 Recibida solicitud POST a /api/videos")
        print(f"   - Content-Type: {request.content_type}")
        print(f"   - Files: {list(request.files.keys())}")
        print(f"   - Form data: {list(request.form.keys())}")
        
        if 'video' not in request.files:
            print("❌ Error: No se proporcionó archivo de video")
            return jsonify({'error': 'No se proporcionó archivo de video'}), 400
        
        file = request.files['video']
        print(f"   - Archivo recibido: {file.filename}")
        print(f"   - Tamaño del archivo: {file.content_length if hasattr(file, 'content_length') else 'N/A'}")
        
        if file.filename == '':
            print("❌ Error: No se seleccionó archivo")
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        if not allowed_file(file.filename):
            print(f"❌ Error: Formato de archivo no permitido: {file.filename}")
            return jsonify({'error': 'Formato de archivo no permitido'}), 400
        
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        tags = request.form.get('tags', '').strip()
        
        print(f"   - Título: {title}")
        print(f"   - Descripción: {description}")
        print(f"   - Tags: {tags}")
        
        if not title:
            print("❌ Error: El título es obligatorio")
            return jsonify({'error': 'El título es obligatorio'}), 400
        
        print("✅ Datos válidos, procediendo con la subida...")
        video_data = video_service.upload_video(file, title, description, tags)
        print(f"✅ Video subido exitosamente con ID: {video_data.get('id')}")
        return jsonify({'data': video_data}), 201
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Obtener un video específico"""
    try:
        video = video_service.get_video_by_id(video_id)
        if not video:
            return jsonify({'error': 'Video no encontrado'}), 404
        return jsonify({'data': video})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Eliminar un video"""
    try:
        success = video_service.delete_video(video_id)
        if not success:
            return jsonify({'error': 'Video no encontrado'}), 404
        return jsonify({'message': 'Video eliminado exitosamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<int:video_id>/delete', methods=['DELETE'])
def delete_video_endpoint(video_id):
    """Eliminar un video (endpoint alternativo)"""
    try:
        success = video_service.delete_video(video_id)
        if not success:
            return jsonify({'error': 'Video no encontrado'}), 404
        return jsonify({'message': 'Video eliminado exitosamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<int:video_id>/publish', methods=['POST'])
def publish_video(video_id):
    """Publicar video en redes sociales"""
    try:
        data = request.get_json()
        platforms = data.get('platforms', [])
        
        if not platforms:
            return jsonify({'error': 'No se especificaron plataformas'}), 400
        
        result = social_service.publish_video(video_id, platforms)
        # Devolver solo el array de resultados de plataformas
        return jsonify({'data': result.get('platforms', [])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Obtener estadísticas de la aplicación"""
    try:
        stats = video_service.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tags', methods=['GET'])
def get_tags():
    """Obtener lista de tags disponibles"""
    try:
        tags = video_service.get_all_tags()
        return jsonify(tags)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir archivos de video subidos"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)