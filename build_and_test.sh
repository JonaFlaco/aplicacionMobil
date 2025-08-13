#!/bin/bash

echo "🚀 Construyendo y probando SocialMan con Docker..."
echo "================================================"

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down

# Limpiar imágenes anteriores (opcional)
echo "🧹 Limpiando imágenes anteriores..."
docker-compose build --no-cache

# Construir y levantar contenedores
echo "🔨 Construyendo contenedores..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar que los contenedores estén corriendo
echo "🔍 Verificando estado de contenedores..."
docker-compose ps

# Probar archivos estáticos
echo "🧪 Probando archivos estáticos..."
echo "Probando en puerto 5000 (Flask directo)..."
python backend/test_static.py

echo ""
echo "Probando en puerto 80 (Nginx)..."
# Modificar temporalmente el script para probar nginx
sed 's/base_url = "http:\/\/localhost:5000"/base_url = "http:\/\/localhost"/' backend/test_static.py > backend/test_nginx.py
python backend/test_nginx.py
rm backend/test_nginx.py

echo ""
echo "✅ Pruebas completadas!"
echo ""
echo "🌐 URLs disponibles:"
echo "   - Flask directo: http://localhost:5000"
echo "   - Nginx proxy:   http://localhost"
echo ""
echo "📝 Logs de contenedores:"
echo "   - Ver logs: docker-compose logs -f"
echo "   - Detener: docker-compose down"
