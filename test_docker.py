#!/usr/bin/env python3
"""
Script para probar la aplicación SocialMan en Docker
"""

import requests
import os
import tempfile
import json
import time

def test_docker_app():
    """Probar la aplicación corriendo en Docker"""
    
    base_url = "http://localhost"  # Docker usa puerto 80
    
    print("🐳 Probando SocialMan en Docker...")
    print(f"URL base: {base_url}")
    print("=" * 60)
    
    # Esperar a que los servicios estén listos
    print("⏳ Esperando a que los servicios estén listos...")
    time.sleep(5)
    
    # Probar endpoints básicos
    endpoints_to_test = [
        ("/", "Página principal"),
        ("/api/videos", "API Videos"),
        ("/static/style.css", "CSS"),
        ("/static/script.js", "JavaScript")
    ]
    
    print("\n🔍 Probando endpoints básicos...")
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {description}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description}: Error - {e}")
    
    # Probar subida de video
    print("\n📤 Probando subida de video...")
    test_file_path = create_test_video()
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'video': ('test_video.mp4', f, 'video/mp4')}
            data = {
                'title': 'Video de prueba Docker',
                'description': 'Video de prueba para verificar Docker',
                'tags': 'docker, test, prueba'
            }
            
            response = requests.post(
                f"{base_url}/api/videos",
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 201:
                print("   ✅ ¡Subida exitosa!")
                try:
                    video_data = response.json()
                    print(f"   Video ID: {video_data.get('id')}")
                    print(f"   Título: {video_data.get('title')}")
                except:
                    pass
            else:
                print("   ❌ Error en la subida")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    print("\n" + "=" * 60)
    print("🎉 Pruebas completadas!")

def create_test_video():
    """Crear un archivo de video de prueba"""
    test_content = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08mdat'
    
    fd, path = tempfile.mkstemp(suffix='.mp4')
    with os.fdopen(fd, 'wb') as f:
        f.write(test_content)
    
    return path

def check_docker_status():
    """Verificar el estado de los contenedores Docker"""
    print("🔍 Verificando estado de contenedores Docker...")
    
    try:
        import subprocess
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True, timeout=10)
        print(result.stdout)
        return True
    except Exception as e:
        print(f"   ❌ Error verificando Docker: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de Docker para SocialMan...")
    
    # Verificar estado de Docker
    check_docker_status()
    
    print("\n" + "=" * 60)
    
    # Probar aplicación
    test_docker_app()
    
    print("\n💡 URLs disponibles:")
    print("   - Aplicación: http://localhost")
    print("   - API: http://localhost/api/videos")
    print("   - Archivos estáticos: http://localhost/static/")
    
    print("\n📝 Comandos útiles:")
    print("   - Ver logs: docker-compose logs -f")
    print("   - Reiniciar: docker-compose restart")
    print("   - Detener: docker-compose down")
