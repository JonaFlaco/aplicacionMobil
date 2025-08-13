import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from sqlalchemy import or_, and_
from models import db, Video, VideoTag
import subprocess
import json

class VideoService:
    """Servicio para gestión de videos"""
    
    def __init__(self):
        self.allowed_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
    
    def upload_video(self, file, title, description, tags):
        """
        Subir un video al sistema
        """
        try:
            # Validar archivo
            if not self._is_allowed_file(file.filename):
                raise ValueError("Formato de archivo no permitido")
            
            # Generar nombre único para el archivo
            filename = self._generate_unique_filename(file.filename)
            
            # Ruta donde se guardará el archivo
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, filename)
            
            # Crear directorio si no existe
            os.makedirs(upload_folder, exist_ok=True)
            
            # Guardar archivo
            file.save(file_path)
            
            # Obtener información del video
            file_size = os.path.getsize(file_path)
            duration = self._get_video_duration(file_path)
            
            # Crear registro en la base de datos
            video = Video(
                title=title.strip(),
                description=description.strip() if description else '',
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                duration=duration,
                tags=tags.strip() if tags else ''
            )
            
            db.session.add(video)
            db.session.commit()
            
            # Actualizar estadísticas de tags
            self._update_tags_statistics(video.get_tags_list())
            
            return video.to_dict()
            
        except Exception as e:
            db.session.rollback()
            # Eliminar archivo si fue creado
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            raise e
    
    def get_videos(self, search='', tag='', sort_by='date', order='desc'):
        """
        Obtener lista de videos con filtros y ordenamiento
        """
        try:
            query = Video.query
            
            # Aplicar filtros de búsqueda
            if search:
                search_filter = or_(
                    Video.title.contains(search),
                    Video.description.contains(search),
                    Video.tags.contains(search)
                )
                query = query.filter(search_filter)
            
            # Filtrar por tag específico
            if tag:
                query = query.filter(Video.tags.contains(tag))
            
            # Aplicar ordenamiento
            if sort_by == 'title':
                if order == 'asc':
                    query = query.order_by(Video.title.asc())
                else:
                    query = query.order_by(Video.title.desc())
            else:  # sort_by == 'date'
                if order == 'asc':
                    query = query.order_by(Video.upload_date.asc())
                else:
                    query = query.order_by(Video.upload_date.desc())
            
            videos = query.all()
            return [video.to_dict() for video in videos]
            
        except Exception as e:
            raise e
    
    def get_video_by_id(self, video_id):
        """
        Obtener un video específico por ID
        """
        try:
            video = Video.query.get(video_id)
            if video:
                return video.to_dict()
            return None
        except Exception as e:
            raise e
    
    def delete_video(self, video_id):
        """
        Eliminar un video
        """
        try:
            video = Video.query.get(video_id)
            if not video:
                return False
            
            # Eliminar archivo físico
            if os.path.exists(video.file_path):
                os.remove(video.file_path)
            
            # Actualizar estadísticas de tags (decrementar)
            self._update_tags_statistics(video.get_tags_list(), increment=False)
            
            # Eliminar registro de la base de datos
            db.session.delete(video)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update_video(self, video_id, title=None, description=None, tags=None):
        """
        Actualizar información de un video
        """
        try:
            video = Video.query.get(video_id)
            if not video:
                return None
            
            # Actualizar campos si se proporcionan
            if title is not None:
                video.title = title.strip()
            
            if description is not None:
                video.description = description.strip()
            
            if tags is not None:
                # Actualizar estadísticas de tags
                old_tags = video.get_tags_list()
                new_tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                
                # Decrementar tags antiguos
                self._update_tags_statistics(old_tags, increment=False)
                # Incrementar tags nuevos
                self._update_tags_statistics(new_tags, increment=True)
                
                video.tags = tags.strip()
            
            video.updated_at = datetime.utcnow()
            db.session.commit()
            
            return video.to_dict()
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_popular_tags(self, limit=20):
        """
        Obtener tags más populares
        """
        try:
            tags = VideoTag.query.order_by(
                VideoTag.usage_count.desc()
            ).limit(limit).all()
            
            return [tag.to_dict() for tag in tags]
            
        except Exception as e:
            raise e
    
    def search_videos_by_date_range(self, start_date, end_date):
        """
        Buscar videos por rango de fechas
        """
        try:
            videos = Video.query.filter(
                and_(
                    Video.upload_date >= start_date,
                    Video.upload_date <= end_date
                )
            ).order_by(Video.upload_date.desc()).all()
            
            return [video.to_dict() for video in videos]
            
        except Exception as e:
            raise e
    
    def _is_allowed_file(self, filename):
        """
        Verificar si el archivo tiene una extensión permitida
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def _generate_unique_filename(self, original_filename):
        """
        Generar nombre único para el archivo
        """
        # Obtener extensión del archivo
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        
        # Generar UUID único
        unique_id = str(uuid.uuid4())
        
        # Crear nombre seguro
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{unique_id}.{file_extension}"
        
        return secure_filename(filename)
    
    def _get_video_duration(self, file_path):
        """
        Obtener duración del video usando ffprobe
        """
        try:
            # Comando ffprobe para obtener duración
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data['format']['duration'])
                return duration
            else:
                # Si ffprobe no está disponible, retornar None
                return None
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
                json.JSONDecodeError, KeyError, FileNotFoundError):
            # Si hay algún error, retornar None
            return None
    
    def _update_tags_statistics(self, tags_list, increment=True):
        """
        Actualizar estadísticas de uso de tags
        """
        try:
            for tag_name in tags_list:
                if not tag_name:
                    continue
                
                tag = VideoTag.query.filter_by(tag=tag_name).first()
                
                if not tag:
                    # Crear nuevo tag si no existe
                    tag = VideoTag(tag=tag_name, usage_count=1 if increment else 0)
                    db.session.add(tag)
                else:
                    # Actualizar contador
                    if increment:
                        tag.usage_count += 1
                    else:
                        tag.usage_count = max(0, tag.usage_count - 1)
                    
                    tag.updated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            # No relanzar la excepción para no afectar la operación principal
            print(f"Error actualizando estadísticas de tags: {e}")
    
    def get_video_stats(self):
        """
        Obtener estadísticas generales de videos
        """
        try:
            total_videos = Video.query.count()
            total_size = db.session.query(db.func.sum(Video.file_size)).scalar() or 0
            total_duration = db.session.query(db.func.sum(Video.duration)).scalar() or 0
            
            # Obtener video más reciente
            latest_video = Video.query.order_by(Video.upload_date.desc()).first()
            
            return {
                'total_videos': total_videos,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_duration_seconds': total_duration,
                'total_duration_minutes': round(total_duration / 60, 2) if total_duration else 0,
                'latest_upload': latest_video.upload_date.isoformat() if latest_video else None
            }
            
        except Exception as e:
            raise e