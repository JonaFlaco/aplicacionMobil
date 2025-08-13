# Configuración de Credenciales de APIs de Redes Sociales

## Resumen

El error "Error desconocido" que ves en los resultados de publicación se debe a que no tienes configuradas las credenciales de las APIs de redes sociales. El sistema está funcionando correctamente, pero necesita las credenciales para poder publicar.

## Configuración de Variables de Entorno

Crea un archivo `.env` en la carpeta `backend/` con las siguientes variables:

```bash
# =============================================================================
# CONFIGURACIÓN BÁSICA DE LA APLICACIÓN
# =============================================================================
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ENVIRONMENT=development

# Base de datos (para desarrollo local con Docker)
DATABASE_URL=postgresql://socialman:password123@localhost:5432/socialman_db

# Archivos
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=104857600

# URL base de la aplicación
BASE_URL=http://localhost:5000

# =============================================================================
# CREDENCIALES DE REDES SOCIALES
# =============================================================================

# =============================================================================
# FACEBOOK API
# =============================================================================
# Para obtener estas credenciales:
# 1. Ve a https://developers.facebook.com/
# 2. Crea una nueva aplicación
# 3. Configura los permisos necesarios (pages_manage_posts, pages_read_engagement)
# 4. Genera un token de acceso de página
FACEBOOK_ACCESS_TOKEN=EAFXcCI5WKqABPHxvoZBYUPVTw22UAmybkePmTZCx1x0e0pj5tjN5bXsQaMp2dHPIEoFYFAM1EEt874YxlPt8K2KCtlSpTDxZAv4JHZB3TClQE9zSV43mfPexVH4EIy3C6QOEEFZBmZC7VJcgCDcAsc8hMZCZBIGSpz7JYaEb6Hp96LaT5iOZBuZAOzEHkia4AmDmenyiZAHJZAoNqEDZACgFTbXZBcENaZCTH1QqZCTqVIQ3zdZA1
FACEBOOK_PAGE_ID=675370979002447

# =============================================================================
# INSTAGRAM API
# =============================================================================
# Para obtener estas credenciales:
# 1. Necesitas una cuenta de Instagram Business
# 2. Conecta tu cuenta de Instagram a tu página de Facebook
# 3. Usa la misma aplicación de Facebook creada anteriormente
# 4. El Business Account ID se obtiene de la API de Facebook
INSTAGRAM_ACCESS_TOKEN=your-instagram-access-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-business-account-id

# =============================================================================
# TIKTOK API
# =============================================================================
# Para obtener estas credenciales:
# 1. Ve a https://developers.tiktok.com/
# 2. Crea una nueva aplicación
# 3. Configura los permisos necesarios (video.upload)
# 4. Genera un token de acceso
TIKTOK_ACCESS_TOKEN=your-tiktok-access-token
TIKTOK_CLIENT_KEY=your-tiktok-client-key
TIKTOK_CLIENT_SECRET=your-tiktok-client-secret

# =============================================================================
# TWITTER/X API
# =============================================================================
# Para obtener estas credenciales:
# 1. Ve a https://developer.twitter.com/
# 2. Crea una nueva aplicación
# 3. Configura los permisos necesarios (Read and Write)
# 4. Genera las claves de API y tokens de acceso
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_ACCESS_TOKEN=your-twitter-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-twitter-access-token-secret
TWITTER_BEARER_TOKEN=your-twitter-bearer-token

# =============================================================================
# AWS (para futuro uso en producción)
# =============================================================================
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=socialman-videos
AWS_REGION=us-east-1

# =============================================================================
# CONFIGURACIÓN ADICIONAL
# =============================================================================
# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5000

# Logging
LOG_LEVEL=INFO
```

## Instrucciones Paso a Paso

### 1. Facebook/Instagram

1. **Crear aplicación en Facebook Developers**:
   - Ve a https://developers.facebook.com/
   - Crea una nueva aplicación
   - Selecciona "Business" como tipo

2. **Configurar permisos**:
   - Ve a "App Review" > "Permissions and Features"
   - Solicita los permisos: `pages_manage_posts`, `pages_read_engagement`

3. **Generar token de página**:
   - Ve a "Tools" > "Graph API Explorer"
   - Selecciona tu aplicación y página
   - Genera un token de acceso

4. **Para Instagram**:
   - Conecta tu cuenta de Instagram Business a tu página de Facebook
   - Usa el mismo token de Facebook
   - Obtén el Business Account ID de la API de Facebook

### 2. TikTok

1. **Crear aplicación en TikTok Developers**:
   - Ve a https://developers.tiktok.com/
   - Crea una nueva aplicación
   - Configura los permisos necesarios

2. **Generar credenciales**:
   - Obtén el Client Key y Client Secret
   - Genera un Access Token

### 3. Twitter/X

1. **Crear aplicación en Twitter Developers**:
   - Ve a https://developer.twitter.com/
   - Crea una nueva aplicación
   - Configura los permisos como "Read and Write"

2. **Generar credenciales**:
   - Obtén las API Keys y Secrets
   - Genera los Access Tokens

## Uso en Desarrollo

Si no configuras las credenciales, el sistema seguirá funcionando pero mostrará mensajes informativos como:

- "Credenciales de Facebook no configuradas. Configura FACEBOOK_ACCESS_TOKEN y FACEBOOK_PAGE_ID en las variables de entorno."
- "Credenciales de Instagram no configuradas. Configura INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_BUSINESS_ACCOUNT_ID en las variables de entorno."

## Reiniciar la Aplicación

Después de configurar las credenciales, reinicia los contenedores:

```bash
docker-compose down
docker-compose up --build -d
```

## Notas Importantes

- **Desarrollo**: Puedes dejar las credenciales vacías para desarrollo
- **Producción**: Siempre configura credenciales reales en producción
- **Seguridad**: Nunca subas el archivo `.env` al repositorio
- **Permisos**: Asegúrate de que las aplicaciones tengan los permisos correctos
