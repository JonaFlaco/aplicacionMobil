#!/usr/bin/env python3
"""
Script de debug para probar la subida de videos
"""

import requests
import os
import tempfile
import json

def test_upload_endpoint():
    """Probar el endpoint de subida de videos"""
    
    base_url = "http://localhost:5000"
    
    print("🔍 Probando endpoint de subida de videos...")
    print(f"URL base: {base_url}")
    print("-" * 50)
    
    # Crear un archivo de prueba
    test_file_path = create_test_video()
    
    try:
        # Preparar datos de prueba
        with open(test_file_path, 'rb') as f:
            files = {'video': ('test_video.mp4', f, 'video/mp4')}
            data = {
                'title': 'Video de prueba',
                'description': 'Este es un video de prueba para diagnosticar el problema',
                'tags': 'test, debug, prueba'
            }
            
            print("📤 Enviando solicitud POST a /api/videos...")
            print(f"   Archivo: {test_file_path}")
            print(f"   Título: {data['title']}")
            print(f"   Descripción: {data['description']}")
            print(f"   Tags: {data['tags']}")
            
            # Hacer la solicitud
            response = requests.post(
                f"{base_url}/api/videos",
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"\n📥 Respuesta del servidor:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"   Response JSON: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Response Text: {response.text}")
            
            if response.status_code == 201:
                print("✅ ¡Subida exitosa!")
                return True
            else:
                print("❌ Error en la subida")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        # Limpiar archivo de prueba
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def create_test_video():
    """Crear un archivo de video de prueba"""
    # Crear un archivo MP4 simple (solo headers)
    test_content = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08mdat'
    
    # Crear archivo temporal
    fd, path = tempfile.mkstemp(suffix='.mp4')
    with os.fdopen(fd, 'wb') as f:
        f.write(test_content)
    
    return path

def test_server_status():
    """Probar el estado del servidor"""
    base_url = "http://localhost:5000"
    
    print("🔍 Probando estado del servidor...")
    
    try:
        # Probar endpoint principal
        response = requests.get(base_url, timeout=5)
        print(f"   Página principal: {response.status_code}")
        
        # Probar endpoint de videos
        response = requests.get(f"{base_url}/api/videos", timeout=5)
        print(f"   GET /api/videos: {response.status_code}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de subida de videos...")
    print("=" * 60)
    
    # Probar estado del servidor
    if not test_server_status():
        print("\n❌ El servidor no está respondiendo. Asegúrate de que esté ejecutándose.")
        exit(1)
    
    print("\n" + "=" * 60)
    
    # Probar subida
    success = test_upload_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ¡Diagnóstico completado exitosamente!")
    else:
        print("💥 Hay problemas con la subida de videos")
        print("\n💡 Posibles soluciones:")
        print("   1. Verificar que la base de datos esté configurada correctamente")
        print("   2. Verificar que el directorio de uploads exista")
        print("   3. Verificar los logs del servidor")
        print("   4. Verificar que ffmpeg esté instalado")
