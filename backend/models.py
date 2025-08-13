from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Video(db.Model):
    """Modelo para almacenar información de videos"""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Tamaño en bytes
    duration = db.Column(db.Float)  # Duración en segundos
    tags = db.Column(db.String(500))  # Tags separados por comas
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con publicaciones
    publications = db.relationship('Publication', backref='video', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convertir el objeto a diccionario"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'duration': self.duration,
            'tags': self.tags.split(',') if self.tags else [],
            'upload_date': self.upload_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'publications': [pub.to_dict() for pub in self.publications]
        }
    
    def get_tags_list(self):
        """Obtener lista de tags"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def set_tags_from_list(self, tags_list):
        """Establecer tags desde una lista"""
        if tags_list:
            self.tags = ','.join([tag.strip() for tag in tags_list if tag.strip()])
        else:
            self.tags = ''

class Publication(db.Model):
    """Modelo para almacenar información de publicaciones en redes sociales"""
    __tablename__ = 'publications'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # instagram, tiktok, facebook, twitter
    platform_post_id = db.Column(db.String(100))  # ID del post en la plataforma
    status = db.Column(db.String(20), default='pending')  # pending, published, failed
    message = db.Column(db.Text)  # Mensaje de estado o error
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convertir el objeto a diccionario"""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'platform': self.platform,
            'platform_post_id': self.platform_post_id,
            'status': self.status,
            'message': self.message,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Platform(db.Model):
    """Modelo para almacenar configuración de plataformas de redes sociales"""
    __tablename__ = 'platforms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    api_config = db.Column(db.Text)  # JSON con configuración de API
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convertir el objeto a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_api_config(self):
        """Obtener configuración de API como diccionario"""
        if self.api_config:
            try:
                return json.loads(self.api_config)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_api_config(self, config_dict):
        """Establecer configuración de API desde diccionario"""
        self.api_config = json.dumps(config_dict)

class VideoTag(db.Model):
    """Modelo para almacenar tags únicos y su frecuencia de uso"""
    __tablename__ = 'video_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100), unique=True, nullable=False)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convertir el objeto a diccionario"""
        return {
            'id': self.id,
            'tag': self.tag,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Función para inicializar datos predeterminados
def init_default_data():
    """Inicializar datos predeterminados en la base de datos"""
    
    # Plataformas predeterminadas
    default_platforms = [
        {
            'name': 'instagram',
            'display_name': 'Instagram',
            'api_config': {
                'endpoint': 'https://graph.facebook.com/v18.0',
                'requires_auth': True
            }
        },
        {
            'name': 'tiktok',
            'display_name': 'TikTok',
            'api_config': {
                'endpoint': 'https://open-api.tiktok.com',
                'requires_auth': True
            }
        },
        {
            'name': 'facebook',
            'display_name': 'Facebook',
            'api_config': {
                'endpoint': 'https://graph.facebook.com/v18.0',
                'requires_auth': True
            }
        },
        {
            'name': 'twitter',
            'display_name': 'X (Twitter)',
            'api_config': {
                'endpoint': 'https://api.twitter.com/2',
                'requires_auth': True
            }
        }
    ]
    
    for platform_data in default_platforms:
        existing_platform = Platform.query.filter_by(name=platform_data['name']).first()
        if not existing_platform:
            platform = Platform(
                name=platform_data['name'],
                display_name=platform_data['display_name']
            )
            platform.set_api_config(platform_data['api_config'])
            db.session.add(platform)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error inicializando datos predeterminados: {e}")