"""
Script de prueba simple para verificar la obtención de ubicación.
Este ejemplo no requiere astropy, solo requests.
"""

import sys
import os

# Agregar el directorio actual al path para importar ubicacion.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ubicacion import UbicacionManager, obtener_ubicacion_rapida
    print("✓ Módulo de ubicación importado correctamente")
except ImportError as e:
    print(f"✗ Error importando módulo de ubicación: {e}")
    sys.exit(1)

def test_ubicacion_simple():
    """
    Prueba simple de obtención de ubicación.
    """
    print("\n" + "="*50)
    print("PRUEBA DE OBTENCIÓN DE UBICACIÓN")
    print("="*50)
    
    try:
        # Método 1: Función rápida
        print("\n1. Probando función rápida...")
        ubicacion = obtener_ubicacion_rapida()
        
        if ubicacion:
            print("✓ Ubicación obtenida exitosamente:")
            print(f"   Ciudad: {ubicacion.get('ciudad', 'N/A')}")
            print(f"   País: {ubicacion.get('pais', 'N/A')}")
            print(f"   Latitud: {ubicacion['latitud']:.6f}°")
            print(f"   Longitud: {ubicacion['longitud']:.6f}°")
            print(f"   Zona horaria: {ubicacion.get('timezone', 'N/A')}")
        else:
            print("✗ No se pudo obtener la ubicación")
            return False
        
        # Método 2: Usando el manager completo
        print("\n2. Probando UbicacionManager...")
        manager = UbicacionManager()
        ubicacion2 = manager.obtener_ubicacion()
        
        if ubicacion2:
            print("✓ UbicacionManager funcionando correctamente")
            manager.imprimir_ubicacion()
            
            # Probar guardado/carga
            print("\n3. Probando guardado y carga...")
            if manager.guardar_ubicacion("test_ubicacion.json"):
                print("✓ Ubicación guardada correctamente")
                
                # Probar carga
                manager_nuevo = UbicacionManager()
                ubicacion_cargada = manager_nuevo.cargar_ubicacion("test_ubicacion.json")
                
                if ubicacion_cargada:
                    print("✓ Ubicación cargada correctamente")
                    return True
                else:
                    print("✗ Error cargando ubicación")
                    return False
            else:
                print("✗ Error guardando ubicación")
                return False
        else:
            print("✗ Error con UbicacionManager")
            return False
            
    except Exception as e:
        print(f"✗ Error durante la prueba: {e}")
        return False

def test_ubicacion_manual():
    """
    Prueba establecimiento manual de ubicación.
    """
    print("\n" + "="*50)
    print("PRUEBA DE UBICACIÓN MANUAL")
    print("="*50)
    
    try:
        manager = UbicacionManager()
        
        # Ejemplo: Coordenadas de Madrid, España
        madrid_lat = 40.4168
        madrid_lon = -3.7038
        madrid_alt = 650  # metros sobre el nivel del mar
        
        ubicacion = manager.establecer_ubicacion_manual(
            madrid_lat, madrid_lon, madrid_alt, "Madrid", "España"
        )
        
        if ubicacion:
            print("✓ Ubicación manual establecida:")
            manager.imprimir_ubicacion()
            return True
        else:
            print("✗ Error estableciendo ubicación manual")
            return False
            
    except Exception as e:
        print(f"✗ Error en prueba manual: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando pruebas del sistema de ubicación...")
    
    # Verificar si hay conexión a internet
    try:
        import requests
        response = requests.get("https://httpbin.org/ip", timeout=5)
        if response.status_code == 200:
            print("✓ Conexión a internet disponible")
            
            # Ejecutar prueba automática
            if test_ubicacion_simple():
                print("\n✓ Todas las pruebas automáticas pasaron")
            else:
                print("\n✗ Algunas pruebas automáticas fallaron")
        else:
            print("✗ Problema con la conexión a internet")
    
    except Exception as e:
        print(f"✗ Sin conexión a internet: {e}")
        print("Probando ubicación manual...")
    
    # Siempre probar ubicación manual (no requiere internet)
    if test_ubicacion_manual():
        print("\n✓ Prueba manual exitosa")
    else:
        print("\n✗ Prueba manual falló")
    
    print("\n" + "="*50)
    print("PRUEBAS COMPLETADAS")
    print("="*50)
    
    # Limpiar archivo de prueba
    try:
        os.remove("test_ubicacion.json")
        print("Archivo de prueba eliminado.")
    except:
        pass