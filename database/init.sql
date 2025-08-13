-- Archivo de inicialización de la base de datos SocialMan

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Tabla de videos
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    duration REAL,
    tags VARCHAR(500),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de plataformas de redes sociales
CREATE TABLE IF NOT EXISTS platforms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    api_config TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de publicaciones
CREATE TABLE IF NOT EXISTS publications (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    message TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de tags de videos
CREATE TABLE IF NOT EXISTS video_tags (
    id SERIAL PRIMARY KEY,
    tag VARCHAR(100) UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Triggers para actualizar updated_at automáticamente
CREATE TRIGGER update_videos_updated_at 
    BEFORE UPDATE ON videos 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platforms_updated_at 
    BEFORE UPDATE ON platforms 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_publications_updated_at 
    BEFORE UPDATE ON publications 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_video_tags_updated_at 
    BEFORE UPDATE ON video_tags 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_videos_upload_date ON videos(upload_date);
CREATE INDEX IF NOT EXISTS idx_videos_title ON videos(title);
CREATE INDEX IF NOT EXISTS idx_videos_tags ON videos USING gin(to_tsvector('spanish', tags));
CREATE INDEX IF NOT EXISTS idx_publications_video_id ON publications(video_id);
CREATE INDEX IF NOT EXISTS idx_publications_platform ON publications(platform);
CREATE INDEX IF NOT EXISTS idx_publications_status ON publications(status);
CREATE INDEX IF NOT EXISTS idx_video_tags_tag ON video_tags(tag);
CREATE INDEX IF NOT EXISTS idx_video_tags_usage_count ON video_tags(usage_count DESC);

-- Insertar plataformas predeterminadas
INSERT INTO platforms (name, display_name, api_config) VALUES 
    ('instagram', 'Instagram', '{"endpoint": "https://graph.facebook.com/v18.0", "requires_auth": true}'),
    ('tiktok', 'TikTok', '{"endpoint": "https://open-api.tiktok.com", "requires_auth": true}'),
    ('facebook', 'Facebook', '{"endpoint": "https://graph.facebook.com/v18.0", "requires_auth": true}'),
    ('twitter', 'X (Twitter)', '{"endpoint": "https://api.twitter.com/2", "requires_auth": true}')
ON CONFLICT (name) DO NOTHING;

-- Insertar algunos tags comunes para comenzar
INSERT INTO video_tags (tag, usage_count) VALUES 
    ('música', 0),
    ('baile', 0),
    ('viral', 0),
    ('comedia', 0),
    ('tutorial', 0),
    ('deportes', 0),
    ('viajes', 0),
    ('cocina', 0),
    ('tecnología', 0),
    ('entretenimiento', 0)
ON CONFLICT (tag) DO NOTHING;

-- Vista para estadísticas rápidas
CREATE OR REPLACE VIEW video_stats AS
SELECT 
    COUNT(*) as total_videos,
    COALESCE(SUM(file_size), 0) as total_size_bytes,
    COALESCE(SUM(duration), 0) as total_duration_seconds,
    COUNT(DISTINCT CASE WHEN upload_date >= CURRENT_DATE - INTERVAL '7 days' THEN id END) as videos_last_week,
    COUNT(DISTINCT CASE WHEN upload_date >= CURRENT_DATE - INTERVAL '30 days' THEN id END) as videos_last_month
FROM videos;

-- Vista para publicaciones por plataforma
CREATE OR REPLACE VIEW publication_stats AS
SELECT 
    platform,
    COUNT(*) as total_publications,
    COUNT(CASE WHEN status = 'published' THEN 1 END) as successful_publications,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_publications,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_publications
FROM publications
GROUP BY platform;

-- Función para limpiar tags no utilizados
CREATE OR REPLACE FUNCTION cleanup_unused_tags()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM video_tags WHERE usage_count = 0;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Comentarios en las tablas
COMMENT ON TABLE videos IS 'Almacena información de los videos subidos';
COMMENT ON TABLE platforms IS 'Configuración de plataformas de redes sociales';
COMMENT ON TABLE publications IS 'Registro de publicaciones en redes sociales';
COMMENT ON TABLE video_tags IS 'Tags únicos y su frecuencia de uso';

-- Configurar permisos (opcional, depende del setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO socialman;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO socialman;