"""
Test del sistema de ubicación usando geocoder para astrotracker.
"""

from ubicacion import UbicacionManager

def test_ubicacion_basica():
    """Test básico de obtención de ubicación."""
    print("🌍 TEST 1: Obtención básica de ubicación")
    print("-" * 50)
    
    ubicacion_mgr = UbicacionManager()
    ubicacion = ubicacion_mgr.obtener_ubicacion()
    
    if ubicacion:
        print("✅ Ubicación obtenida exitosamente")
        ubicacion_mgr.imprimir_ubicacion()
        return True
    else:
        print("❌ No se pudo obtener la ubicación")
        return False

def test_ubicacion_por_direccion():
    """Test de geocodificación por dirección."""
    print("\n🏠 TEST 2: Geocodificación por dirección")
    print("-" * 50)
    
    ubicacion_mgr = UbicacionManager()
    
    # Prueba con diferentes direcciones
    direcciones = [
        "Madrid, España",
        "Barcelona, Spain",
        "Mexico City, Mexico"
    ]
    
    for direccion in direcciones:
        print(f"\n🔍 Probando: {direccion}")
        resultado = ubicacion_mgr.obtener_ubicacion_por_direccion(direccion)
        
        if resultado:
            print(f"✅ Encontrado: {resultado['direccion']}")
            print(f"   Coordenadas: {resultado['latitud']:.4f}, {resultado['longitud']:.4f}")
        else:
            print(f"❌ No se encontró: {direccion}")

def test_informacion_detallada():
    """Test de información detallada."""
    print("\n📍 TEST 3: Información detallada")
    print("-" * 50)
    
    ubicacion_mgr = UbicacionManager()
    ubicacion = ubicacion_mgr.obtener_ubicacion()
    
    if ubicacion:
        print("Obteniendo información detallada...")
        detallada = ubicacion_mgr.obtener_informacion_detallada()
        
        if detallada:
            print("✅ Información detallada obtenida")
            ubicacion_mgr.imprimir_ubicacion()
        else:
            print("❌ No se pudo obtener información detallada")

def test_metodos_alternativos():
    """Test de métodos alternativos."""
    print("\n🔄 TEST 4: Métodos alternativos")
    print("-" * 50)
    
    ubicacion_mgr = UbicacionManager()
    ubicacion = ubicacion_mgr.obtener_ubicacion_alternativa()
    
    if ubicacion:
        print("✅ Ubicación obtenida con método alternativo")
        print(f"Proveedor usado: {ubicacion.get('proveedor', 'N/A')}")
    else:
        print("❌ Métodos alternativos fallaron")

def test_earth_location():
    """Test del objeto EarthLocation para astronomía."""
    print("\n🌌 TEST 5: Objeto EarthLocation")
    print("-" * 50)
    
    ubicacion_mgr = UbicacionManager()
    ubicacion = ubicacion_mgr.obtener_ubicacion()
    
    if ubicacion:
        earth_loc = ubicacion_mgr.get_earth_location()
        
        if earth_loc:
            print("✅ Objeto EarthLocation creado exitosamente")
            print(f"   Latitud: {earth_loc.lat}")
            print(f"   Longitud: {earth_loc.lon}")
            print(f"   Altura: {earth_loc.height}")
            print("\n🔬 Esto es útil para cálculos astronómicos precisos")
        else:
            print("❌ No se pudo crear EarthLocation")

def test_guardado_y_carga():
    """Test de guardado y carga de configuración."""
    print("\n💾 TEST 6: Guardado y carga")
    print("-" * 50)
    
    ubicacion_mgr = UbicacionManager()
    ubicacion = ubicacion_mgr.obtener_ubicacion()
    
    if ubicacion:
        # Guardar
        if ubicacion_mgr.guardar_ubicacion("test_ubicacion.json"):
            print("✅ Ubicación guardada exitosamente")
            
            # Crear nueva instancia y cargar
            nueva_instancia = UbicacionManager()
            if nueva_instancia.cargar_ubicacion("test_ubicacion.json"):
                print("✅ Ubicación cargada exitosamente")
                print("Datos cargados:")
                nueva_instancia.imprimir_ubicacion()
            else:
                print("❌ Error cargando ubicación")
        else:
            print("❌ Error guardando ubicación")

def main():
    """Ejecutar todos los tests."""
    print("🚀 INICIANDO TESTS DEL SISTEMA DE UBICACIÓN GEOCODER")
    print("=" * 70)
    
    try:
        # Test básico
        if test_ubicacion_basica():
            # Tests adicionales solo si el básico funciona
            test_ubicacion_por_direccion()
            test_informacion_detallada()
            test_metodos_alternativos()
            test_earth_location()
            test_guardado_y_carga()
        
        print("\n🎯 TESTS COMPLETADOS")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante los tests: {e}")

if __name__ == "__main__":
    main()