#!/usr/bin/env python3
"""
Script para construir y ejecutar SocialMan en Docker
"""

import subprocess
import time
import sys
import os

def run_command(command, description):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n🔧 {description}...")
    print(f"Comando: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print("✅ Comando ejecutado exitosamente")
        if result.stdout:
            print("Salida:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {e}")
        if e.stdout:
            print("Salida:", e.stdout)
        if e.stderr:
            print("Error:", e.stderr)
        return False

def build_and_run_docker():
    """Construir y ejecutar la aplicación en Docker"""
    
    print("🐳 Construyendo y ejecutando SocialMan en Docker...")
    print("=" * 60)
    
    # Detener contenedores existentes
    if not run_command("docker-compose down", "Deteniendo contenedores existentes"):
        return False
    
    # Limpiar imágenes anteriores
    if not run_command("docker-compose build --no-cache", "Construyendo imágenes Docker"):
        return False
    
    # Levantar contenedores
    if not run_command("docker-compose up -d", "Levantando contenedores"):
        return False
    
    # Esperar a que los servicios estén listos
    print("\n⏳ Esperando a que los servicios estén listos...")
    time.sleep(15)
    
    # Verificar estado de contenedores
    if not run_command("docker-compose ps", "Verificando estado de contenedores"):
        return False
    
    # Verificar logs
    print("\n📋 Verificando logs de los contenedores...")
    print("-" * 50)
    
    services = ['app', 'db', 'nginx']
    for service in services:
        print(f"\n📝 Logs de {service}:")
        try:
            result = subprocess.run(f"docker-compose logs --tail=10 {service}", 
                                  shell=True, capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Error obteniendo logs de {service}: {e}")
    
    return True

def test_application():
    """Probar la aplicación"""
    print("\n🧪 Probando la aplicación...")
    print("-" * 50)
    
    try:
        # Importar y ejecutar el script de prueba
        from test_docker import test_docker_app
        test_docker_app()
        return True
    except Exception as e:
        print(f"❌ Error probando la aplicación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando SocialMan en Docker...")
    
    # Construir y ejecutar
    if not build_and_run_docker():
        print("\n💥 Error construyendo/ejecutando Docker")
        return False
    
    # Probar aplicación
    if not test_application():
        print("\n💥 Error probando la aplicación")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ¡SocialMan está ejecutándose en Docker!")
    print("\n🌐 URLs disponibles:")
    print("   - Aplicación: http://localhost")
    print("   - API: http://localhost/api/videos")
    print("   - Backend directo: http://localhost:5000")
    
    print("\n📝 Comandos útiles:")
    print("   - Ver logs: docker-compose logs -f")
    print("   - Reiniciar: docker-compose restart")
    print("   - Detener: docker-compose down")
    print("   - Probar: python test_docker.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
