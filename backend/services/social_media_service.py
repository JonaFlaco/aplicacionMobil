import requests
import json
import time
from datetime import datetime
from flask import current_app
from models import db, Publication, Platform
import logging

logger = logging.getLogger(__name__)

class SocialMediaService:
    """Servicio para gestión de publicaciones en redes sociales"""
    
    def __init__(self):
        self.platforms = {
            'instagram': InstagramPublisher(),
            'tiktok': TikTokPublisher(),
            'facebook': FacebookPublisher(),
            'twitter': TwitterPublisher()
        }
    
    def get_available_platforms(self):
        """Obtener lista de plataformas disponibles"""
        try:
            platforms = Platform.query.filter_by(is_active=True).all()
            return [platform.to_dict() for platform in platforms]
        except Exception as e:
            logger.error(f"Error obteniendo plataformas: {e}")
            return []
    
    def publish_to_platforms(self, video_data, platforms):
        """Publicar video en múltiples plataformas"""
        results = []
        
        for platform_name in platforms:
            try:
                result = self._publish_to_platform(video_data, platform_name)
                results.append(result)
            except Exception as e:
                logger.error(f"Error publicando en {platform_name}: {e}")
                results.append({
                    'platform': platform_name,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _publish_to_platform(self, video_data, platform_name):
        """Publicar video en una plataforma específica"""
        try:
            # Crear registro de publicación
            publication = Publication(
                video_id=video_data['id'],
                platform=platform_name,
                status='pending'
            )
            db.session.add(publication)
            db.session.commit()
            
            # Obtener publisher para la plataforma
            publisher = self.platforms.get(platform_name)
            if not publisher:
                raise ValueError(f"Plataforma no soportada: {platform_name}")
            
            # Intentar publicar
            publish_result = publisher.publish_video(video_data)
            
            # Actualizar registro de publicación
            if publish_result['success']:
                publication.status = 'published'
                publication.platform_post_id = publish_result.get('post_id')
                publication.published_at = datetime.utcnow()
                publication.message = 'Publicado exitosamente'
            else:
                publication.status = 'failed'
                publication.message = publish_result.get('error', 'Error desconocido')
            
            db.session.commit()
            
            return {
                'platform': platform_name,
                'success': publish_result['success'],
                'publication_id': publication.id,
                'post_id': publish_result.get('post_id'),
                'message': publication.message
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error en _publish_to_platform para {platform_name}: {e}")
            raise e
    
    def get_publication_status(self, video_id):
        """Obtener estado de publicaciones de un video"""
        try:
            publications = Publication.query.filter_by(video_id=video_id).all()
            return [pub.to_dict() for pub in publications]
        except Exception as e:
            logger.error(f"Error obteniendo estado de publicaciones: {e}")
            return []
    
    def publish_video(self, video_id, platforms):
        """Publicar video en las plataformas especificadas"""
        try:
            # Obtener datos del video
            from models import Video
            video = Video.query.get(video_id)
            if not video:
                raise ValueError("Video no encontrado")
            
            video_data = video.to_dict()
            
            # Publicar en las plataformas especificadas
            results = self.publish_to_platforms(video_data, platforms)
            
            return {
                'video_id': video_id,
                'platforms': results,
                'success': any(result['success'] for result in results)
            }
            
        except Exception as e:
            logger.error(f"Error publicando video {video_id}: {e}")
            raise e

class BaseSocialPublisher:
    """Clase base para publicadores de redes sociales"""
    
    def __init__(self):
        self.platform_name = "base"
    
    def publish_video(self, video_data):
        """Método base para publicar video - debe ser implementado por cada plataforma"""
        raise NotImplementedError("Debe implementarse en la clase hija")
    
    def _get_video_url(self, video_data):
        """Construir URL completa del video"""
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        # Para pruebas, usar una URL pública de video
        # En producción, esto debería ser una URL pública accesible desde internet
        return f"{base_url}/uploads/{video_data['filename']}"

class InstagramPublisher(BaseSocialPublisher):
    """Publisher para Instagram"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "instagram"
    
    def publish_video(self, video_data):
        """Publicar video en Instagram"""
        try:
            # Simular publicación en Instagram
            # En un entorno real, aquí usarías la API de Instagram
            
            access_token = current_app.config.get('INSTAGRAM_ACCESS_TOKEN')
            business_account_id = current_app.config.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
            
            if not access_token or not business_account_id:
                return {
                    'success': False,
                    'error': 'Credenciales de Instagram no configuradas. Configura INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_BUSINESS_ACCOUNT_ID en las variables de entorno.'
                }
            
            # Simular delay de API
            time.sleep(1)
            
            # Para desarrollo local, simular éxito
            mock_post_id = f"instagram_{int(time.time())}"
            
            logger.info(f"Simulando publicación en Instagram: {video_data['title']}")
            
            return {
                'success': True,
                'post_id': mock_post_id,
                'message': 'Publicado en Instagram (simulado)'
            }
            
        except Exception as e:
            logger.error(f"Error publicando en Instagram: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class TikTokPublisher(BaseSocialPublisher):
    """Publisher para TikTok"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "tiktok"
    
    def publish_video(self, video_data):
        """Publicar video en TikTok"""
        try:
            access_token = current_app.config.get('TIKTOK_ACCESS_TOKEN')
            
            if not access_token:
                return {
                    'success': False,
                    'error': 'Credenciales de TikTok no configuradas. Configura TIKTOK_ACCESS_TOKEN en las variables de entorno.'
                }
            
            # Simular delay de API
            time.sleep(1.5)
            
            # Para desarrollo local, simular éxito
            mock_post_id = f"tiktok_{int(time.time())}"
            
            logger.info(f"Simulando publicación en TikTok: {video_data['title']}")
            
            return {
                'success': True,
                'post_id': mock_post_id,
                'message': 'Publicado en TikTok (simulado)'
            }
            
        except Exception as e:
            logger.error(f"Error publicando en TikTok: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class FacebookPublisher(BaseSocialPublisher):
    """Publisher para Facebook"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "facebook"
    
    def publish_video(self, video_data):
        """Publicar video en Facebook"""
        try:
            access_token = current_app.config.get('FACEBOOK_ACCESS_TOKEN')
            page_id = current_app.config.get('FACEBOOK_PAGE_ID')
            
            logger.info(f"Intentando publicar en Facebook - Token: {access_token[:20]}..., Page ID: {page_id}")
            
            if not access_token or not page_id:
                return {
                    'success': False,
                    'error': 'Credenciales de Facebook no configuradas. Configura FACEBOOK_ACCESS_TOKEN y FACEBOOK_PAGE_ID en las variables de entorno.'
                }
            
            # Primero verificar los permisos del token
            debug_url = f"https://graph.facebook.com/debug_token"
            debug_params = {
                'input_token': access_token,
                'access_token': access_token
            }
            
            debug_response = requests.get(debug_url, params=debug_params)
            logger.info(f"Debug token response: {debug_response.status_code} - {debug_response.text}")
            
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                scopes = debug_data.get('data', {}).get('scopes', [])
                logger.info(f"Permisos del token: {scopes}")
                
                # Verificar si tiene los permisos necesarios
                required_scopes = ['pages_manage_posts', 'publish_video']
                missing_scopes = [scope for scope in required_scopes if scope not in scopes]
                
                if missing_scopes:
                    return {
                        'success': False,
                        'error': f'Token de Facebook no tiene los permisos necesarios. Faltan: {missing_scopes}. Permisos actuales: {scopes}'
                    }
            
            # Simular publicación exitosa para pruebas
            # En producción, necesitas subir el video a un servidor público
            # y usar la URL pública del video
            logger.info(f"Simulando publicación exitosa en Facebook: {video_data['title']}")
            
            # Generar un ID simulado
            mock_post_id = f"facebook_{int(time.time())}"
            
            return {
                'success': True,
                'post_id': mock_post_id,
                'message': f'Publicado exitosamente en Facebook (ID: {mock_post_id}) - Simulado para pruebas'
            }
            
        except requests.RequestException as e:
            logger.error(f"Error de conexión con Facebook: {e}")
            return {
                'success': False,
                'error': f'Error de conexión con Facebook: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error inesperado publicando en Facebook: {e}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }

class TwitterPublisher(BaseSocialPublisher):
    """Publisher para Twitter/X"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "twitter"
    
    def publish_video(self, video_data):
        """Publicar video en Twitter/X"""
        try:
            bearer_token = current_app.config.get('TWITTER_BEARER_TOKEN')
            
            if not bearer_token:
                return {
                    'success': False,
                    'error': 'Credenciales de Twitter no configuradas. Configura TWITTER_BEARER_TOKEN en las variables de entorno.'
                }
            
            # Simular delay de API
            time.sleep(0.8)
            
            # Para desarrollo local, simular éxito
            mock_post_id = f"twitter_{int(time.time())}"
            
            logger.info(f"Simulando publicación en Twitter: {video_data['title']}")
            
            return {
                'success': True,
                'post_id': mock_post_id,
                'message': 'Publicado en Twitter/X (simulado)'
            }
            
        except Exception as e:
            logger.error(f"Error publicando en Twitter: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class RealInstagramPublisher(InstagramPublisher):
    """Publisher real para Instagram usando la API oficial"""
    
    def publish_video(self, video_data):
        """Implementación real de publicación en Instagram"""
        try:
            access_token = current_app.config.get('INSTAGRAM_ACCESS_TOKEN')
            business_account_id = current_app.config.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
            
            if not access_token or not business_account_id:
                raise ValueError("Credenciales de Instagram no configuradas")
            
            video_url = self._get_video_url(video_data)
            
            # Paso 1: Crear contenedor de media
            container_url = f"https://graph.facebook.com/v18.0/{business_account_id}/media"
            container_params = {
                'video_url': video_url,
                'caption': f"{video_data['title']}\n\n{video_data['description']}",
                'access_token': access_token
            }
            
            container_response = requests.post(container_url, data=container_params)
            container_response.raise_for_status()
            
            creation_id = container_response.json()['id']
            
            # Paso 2: Publicar el contenedor
            publish_url = f"https://graph.facebook.com/v18.0/{business_account_id}/media_publish"
            publish_params = {
                'creation_id': creation_id,
                'access_token': access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            publish_response.raise_for_status()
            
            post_id = publish_response.json()['id']
            
            return {
                'success': True,
                'post_id': post_id,
                'message': 'Publicado exitosamente en Instagram'
            }
            
        except requests.RequestException as e:
            logger.error(f"Error de API en Instagram: {e}")
            return {
                'success': False,
                'error': f'Error de API: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error general en Instagram: {e}")
            return {
                'success': False,
                'error': str(e)
            }