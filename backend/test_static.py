#!/usr/bin/env python3
"""
Script de prueba para verificar que los archivos estáticos se sirvan correctamente
"""

import os
import requests
import sys

def test_static_files():
    """Probar que los archivos estáticos estén disponibles"""
    
    # URL base (cambiar según tu configuración)
    base_url = "http://localhost:5000"  # Para desarrollo local
    # base_url = "http://localhost"      # Para Docker
    
    # Archivos estáticos a probar
    static_files = [
        "/static/style.css",
        "/static/script.js"
    ]
    
    print("🔍 Probando archivos estáticos...")
    print(f"URL base: {base_url}")
    print("-" * 50)
    
    all_good = True
    
    for file_path in static_files:
        url = base_url + file_path
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {file_path} - OK (Status: {response.status_code})")
                print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
                print(f"   Tamaño: {len(response.content)} bytes")
            else:
                print(f"❌ {file_path} - Error (Status: {response.status_code})")
                all_good = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {file_path} - Error de conexión: {e}")
            all_good = False
        print()
    
    # Probar la página principal
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Página principal - OK (Status: {response.status_code})")
            if "SocialMan" in response.text:
                print("   ✅ Contenido HTML encontrado")
            else:
                print("   ⚠️  Contenido HTML no encontrado")
        else:
            print(f"❌ Página principal - Error (Status: {response.status_code})")
            all_good = False
    except requests.exceptions.RequestException as e:
        print(f"❌ Página principal - Error de conexión: {e}")
        all_good = False
    
    print("-" * 50)
    if all_good:
        print("🎉 ¡Todos los archivos estáticos funcionan correctamente!")
    else:
        print("💥 Hay problemas con algunos archivos estáticos")
    
    return all_good

if __name__ == "__main__":
    success = test_static_files()
    sys.exit(0 if success else 1)
