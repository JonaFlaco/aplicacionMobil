# SocialMan App - Gestión de Videos para Redes Sociales

Una aplicación web para gestionar y publicar videos en múltiples plataformas de redes sociales.

## 🚀 Características

- **Subida de Videos**: Carga videos mediante drag & drop o selección de archivos
- **Gestión de Contenido**: Organiza videos con títulos, descripciones y tags
- **Búsqueda y Filtros**: Encuentra videos rápidamente por título, fecha o tags
- **Publicación Multi-plataforma**: Publica en Instagram, TikTok, Facebook y Twitter/X
- **Estadísticas**: Visualiza métricas de tus videos y publicaciones
- **Responsive Design**: Funciona perfectamente en desktop y móvil

## 🛠️ Tecnologías

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Base de Datos**: PostgreSQL
- **Containerización**: Docker, Docker Compose
- **APIs**: Integración con redes sociales

## 📋 Prerrequisitos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)
- FFmpeg (para procesamiento de video)

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/socialman-app.git
cd socialman-app
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Ejecutar con Docker Compose

```bash
# Desarrollo
docker-compose up -d

# Incluir Adminer para gestión de DB
docker-compose --profile development up -d

# Producción con Nginx
docker-compose --profile production up -d
```

### 4. Acceder a la Aplicación

- **Aplicación**: http://localhost:5000
- **Adminer** (desarrollo): http://localhost:8080
- **Nginx** (producción): http://localhost

## 🔧 Desarrollo Local (Sin Docker)

### 1. Configurar Entorno Virtual

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

```bash
# Instalar PostgreSQL localmente o usar Docker
docker run --name socialman-db -e POSTGRES_PASSWORD=password123 -e POSTGRES_USER=socialman -e POSTGRES_DB=socialman_db