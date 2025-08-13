# Usar imagen base de Python
FROM python:3.11-slim

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivo de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorio para uploads
RUN mkdir -p static/uploads

# Crear directorio para templates
RUN mkdir -p templates

# Exponer puerto
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["sh", "-c", "echo 'Esperando a que PostgreSQL esté disponible...'; while ! nc -z db 5432; do sleep 2; done; echo 'PostgreSQL disponible - iniciando aplicación'; gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app"]