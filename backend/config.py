import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    # Configuración de base de datos
    # Para desarrollo local usaremos SQLite, pero se puede cambiar fácilmente a PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        # SQLite por defecto para desarrollo local
        basedir = os.path.abspath(os.path.dirname(__file__))
        DATABASE_URL = f'sqlite:///{os.path.join(basedir, "socialman.db")}'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de archivos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB máximo por archivo
    
    # Crear directorio de uploads si no existe
    upload_path = os.path.join(os.path.dirname(__file__), UPLOAD_FOLDER)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    # Configuración de AWS (para futuro uso)
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET', 'socialman-videos')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Configuración de APIs de redes sociales
    # Instagram
    INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    
    # TikTok
    TIKTOK_ACCESS_TOKEN = os.environ.get('TIKTOK_ACCESS_TOKEN')
    TIKTOK_CLIENT_KEY = os.environ.get('TIKTOK_CLIENT_KEY')
    TIKTOK_CLIENT_SECRET = os.environ.get('TIKTOK_CLIENT_SECRET')
    
    # Facebook
    FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
    FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID')
    
    # Twitter/X
    TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN')
    
    # Configuración de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Configuración de desarrollo/producción
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
    
    @staticmethod
    def init_app(app):
        """Inicializar configuración específica de la aplicación"""
        pass

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configuraciones específicas de producción
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/socialman.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('SocialMan App startup')

class TestConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}