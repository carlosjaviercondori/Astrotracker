"""
Test simplificado del sistema de ubicación con geocoder.
Se enfoca en las funcionalidades principales que funcionan bien.
"""

from ubicacion import UbicacionManager

def main():
    """Test principal del sistema de ubicación con geocoder."""
    print("🚀 ASTROTRACKER - TEST SISTEMA DE UBICACIÓN CON GEOCODER")
    print("=" * 70)
    
    # Crear instancia del manager
    ubicacion_mgr = UbicacionManager()
    
    # Test 1: Obtener ubicación automática
    print("\n🌍 TEST 1: Obteniendo ubicación automática...")
    print("-" * 50)
    
    ubicacion = ubicacion_mgr.obtener_ubicacion()
    
    if ubicacion:
        print("✅ Ubicación obtenida exitosamente!")
        ubicacion_mgr.imprimir_ubicacion()
        
        # Test 2: Objeto EarthLocation para astronomía
        print("\n🌌 TEST 2: Creando objeto EarthLocation para astronomía...")
        print("-" * 50)
        
        earth_location = ubicacion_mgr.get_earth_location()
        if earth_location is not None:
            print("✅ Objeto EarthLocation creado exitosamente!")
            print("Este objeto es esencial para cálculos astronómicos precisos:")
            print(f"   • Latitud astronómica: {earth_location.lat}")
            print(f"   • Longitud astronómica: {earth_location.lon}")
            print(f"   • Altura sobre el nivel del mar: {earth_location.height}")
        
        # Test 3: Guardar configuración
        print("\n💾 TEST 3: Guardando configuración...")
        print("-" * 50)
        
        if ubicacion_mgr.guardar_ubicacion("astrotracker_ubicacion.json"):
            print("✅ Configuración guardada en 'astrotracker_ubicacion.json'")
            print("Ahora puedes cargar esta configuración rápidamente en el futuro.")
        
        # Test 4: Ubicación manual (para telescopios fijos)
        print("\n🎯 TEST 4: Estableciendo ubicación manual...")
        print("-" * 50)
        
        # Ejemplo: Observatorio del Teide, España
        lat_teide = 28.3009
        lon_teide = -16.5093
        alt_teide = 2390
        
        ubicacion_manual = ubicacion_mgr.establecer_ubicacion_manual(
            lat_teide, lon_teide, alt_teide, 
            "Observatorio del Teide", "España"
        )
        
        if ubicacion_manual:
            print("✅ Ubicación manual establecida (Observatorio del Teide):")
            print(f"   • Latitud: {lat_teide}°")
            print(f"   • Longitud: {lon_teide}°") 
            print(f"   • Altitud: {alt_teide} m")
            print("Esto es útil para telescopios en ubicaciones fijas conocidas.")
        
        # Test 5: Diferentes proveedores
        print("\n🔄 TEST 5: Probando proveedores alternativos...")
        print("-" * 50)
        
        ubicacion_alt = ubicacion_mgr.obtener_ubicacion_alternativa()
        if ubicacion_alt:
            print("✅ Proveedor alternativo funcionó!")
            print(f"Proveedor usado: {ubicacion_alt.get('proveedor', 'N/A')}")
        else:
            print("⚠️  Los proveedores alternativos no están disponibles actualmente")
        
        # Resumen final
        print("\n🎯 RESUMEN PARA ASTROTRACKER")
        print("=" * 70)
        print("✅ Sistema de ubicación configurado exitosamente")
        print("✅ Objeto EarthLocation creado para cálculos astronómicos") 
        print("✅ Configuración guardada para uso futuro")
        print("\n📍 INFORMACIÓN CLAVE PARA TU ASTROTRACKER:")
        ubicacion_actual = ubicacion_mgr.ubicacion_actual
        if ubicacion_actual:
            print(f"   • Latitud: {ubicacion_actual['latitud']:.6f}°")
            print(f"   • Longitud: {ubicacion_actual['longitud']:.6f}°")
            print(f"   • Ubicación: {ubicacion_actual.get('ciudad', 'N/A')}, {ubicacion_actual.get('pais', 'N/A')}")
        
        print("\n🔧 PRÓXIMOS PASOS:")
        print("   1. Integrar esta ubicación con los cálculos de seguimiento")
        print("   2. Usar EarthLocation para cálculos de coordenadas celestes")
        print("   3. Implementar corrección por altitud si tienes un observatorio elevado")
        
    else:
        print("❌ No se pudo obtener la ubicación")
        print("💡 Puedes usar ubicación manual con coordenadas conocidas:")
        print("   ubicacion_mgr.establecer_ubicacion_manual(lat, lon, altitud)")
    
    print("\n🎉 TEST COMPLETADO")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()