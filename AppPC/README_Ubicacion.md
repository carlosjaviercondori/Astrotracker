# 🌍 Sistema de Ubicación para Astrotracker con Geocoder

## 📋 Descripción

Este módulo proporciona funcionalidades avanzadas de geolocalización para sistemas astrotracker utilizando la librería `geocoder`. Permite obtener coordenadas geográficas precisas necesarias para cálculos astronómicos y seguimiento de objetos celestes.

## 🚀 Características

- ✅ **Detección automática de ubicación** usando múltiples proveedores
- ✅ **Integración con Astropy** para cálculos astronómicos precisos
- ✅ **Ubicación manual** para observatorios fijos
- ✅ **Guardado/carga de configuración** 
- ✅ **Múltiples proveedores** para mayor confiabilidad
- ✅ **Geocodificación** por dirección (cuando está disponible)

## 📦 Dependencias

```bash
pip install geocoder astropy
```

## 🔧 Uso Básico

### Obtener ubicación automáticamente

```python
from ubicacion import UbicacionManager

# Crear instancia
ubicacion_mgr = UbicacionManager()

# Obtener ubicación automática
ubicacion = ubicacion_mgr.obtener_ubicacion()

if ubicacion:
    print(f"Latitud: {ubicacion['latitud']}")
    print(f"Longitud: {ubicacion['longitud']}")
    print(f"Ciudad: {ubicacion['ciudad']}")
```

### Para uso astronómico

```python
# Obtener objeto EarthLocation para cálculos astronómicos
earth_location = ubicacion_mgr.get_earth_location()

if earth_location is not None:
    print(f"Latitud astronómica: {earth_location.lat}")
    print(f"Longitud astronómica: {earth_location.lon}")
    print(f"Altura: {earth_location.height}")
```

### Ubicación manual (recomendado para telescopios fijos)

```python
# Para un observatorio fijo
lat = -31.4065  # Córdoba, Argentina
lon = -64.1885
alt = 430       # metros sobre el nivel del mar

ubicacion_mgr.establecer_ubicacion_manual(
    lat, lon, alt, "Córdoba", "Argentina"
)
```

### Guardar y cargar configuración

```python
# Guardar ubicación actual
ubicacion_mgr.guardar_ubicacion("mi_observatorio.json")

# Cargar configuración guardada
ubicacion_mgr.cargar_ubicacion("mi_observatorio.json")
```

## 📊 Información proporcionada

El sistema devuelve un diccionario con:

```python
{
    'latitud': -31.4065,           # Grados decimales
    'longitud': -64.1885,          # Grados decimales
    'ciudad': 'Córdoba',           # Ciudad detectada
    'pais': 'AR',                  # Código de país
    'region': 'Cordoba',           # Región/estado
    'timezone': '',                # Zona horaria (cuando disponible)
    'direccion': 'Dirección completa',
    'altitud': 0,                  # Metros sobre nivel del mar
    'timestamp': '2025-10-03T...',  # Timestamp de obtención
    'proveedor': 'ip'              # Proveedor usado
}
```

## 🌌 Integración con Astrotracker

### Ejemplo de uso en sistema de seguimiento

```python
from ubicacion import UbicacionManager
from astropy.coordinates import EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u

def configurar_observatorio():
    """Configura la ubicación del observatorio."""
    ubicacion_mgr = UbicacionManager()
    
    # Opción 1: Automática
    ubicacion = ubicacion_mgr.obtener_ubicacion()
    
    # Opción 2: Manual (más precisa)
    # ubicacion = ubicacion_mgr.establecer_ubicacion_manual(
    #     lat=-31.4065, lon=-64.1885, altitud=430
    # )
    
    if ubicacion:
        # Obtener EarthLocation
        earth_location = ubicacion_mgr.get_earth_location()
        
        # Guardar configuración
        ubicacion_mgr.guardar_ubicacion("observatorio_config.json")
        
        return earth_location
    return None

def calcular_coordenadas_locales(earth_location, ra, dec):
    """
    Convierte coordenadas ecuatoriales a horizontales locales.
    Útil para posicionamiento del astrotracker.
    """
    # Tiempo actual
    tiempo = Time.now()
    
    # Crear marco de referencia Alt-Az para la ubicación
    altaz_frame = AltAz(obstime=tiempo, location=earth_location)
    
    # Coordenadas ecuatoriales del objeto
    from astropy.coordinates import SkyCoord
    objetivo = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
    
    # Convertir a coordenadas horizontales
    coords_horizontales = objetivo.transform_to(altaz_frame)
    
    return {
        'altitud': coords_horizontales.alt.deg,
        'azimut': coords_horizontales.az.deg
    }

# Ejemplo de uso
if __name__ == "__main__":
    earth_loc = configurar_observatorio()
    if earth_loc is not None:
        # Ejemplo: coordenadas de Sirius
        sirius_ra = 101.287  # Ascensión recta en grados
        sirius_dec = -16.716 # Declinación en grados
        
        coords = calcular_coordenadas_locales(earth_loc, sirius_ra, sirius_dec)
        print(f"Sirius - Altitud: {coords['altitud']:.2f}°")
        print(f"Sirius - Azimut: {coords['azimut']:.2f}°")
```

## 🔧 Métodos disponibles

### UbicacionManager

| Método | Descripción |
|--------|-------------|
| `obtener_ubicacion()` | Obtiene ubicación automáticamente |
| `obtener_ubicacion_alternativa()` | Prueba proveedores alternativos |
| `establecer_ubicacion_manual(lat, lon, alt)` | Define ubicación manualmente |
| `obtener_ubicacion_por_direccion(direccion)` | Geocodifica una dirección |
| `get_earth_location()` | Retorna objeto EarthLocation |
| `imprimir_ubicacion()` | Muestra información formateada |
| `guardar_ubicacion(archivo)` | Guarda en JSON |
| `cargar_ubicacion(archivo)` | Carga desde JSON |

## 🎯 Casos de uso para Astrotracker

### 1. **Astrotracker portátil**
```python
# Para un sistema móvil que se mueve entre ubicaciones
ubicacion = ubicacion_mgr.obtener_ubicacion()
ubicacion_mgr.guardar_ubicacion(f"session_{datetime.now().strftime('%Y%m%d')}.json")
```

### 2. **Observatorio fijo**
```python
# Para un telescopio permanente con coordenadas conocidas
ubicacion_mgr.establecer_ubicacion_manual(
    lat=-31.4065, lon=-64.1885, altitud=430,
    ciudad="Observatorio Casa", pais="Argentina"
)
```

### 3. **Sistema de respaldo**
```python
# Intentar cargar configuración guardada, si falla usar automática
if not ubicacion_mgr.cargar_ubicacion("observatorio.json"):
    print("Configuración no encontrada, detectando automáticamente...")
    ubicacion_mgr.obtener_ubicacion()
    ubicacion_mgr.guardar_ubicacion("observatorio.json")
```

## ❗ Notas importantes

1. **Precisión**: La detección automática por IP tiene precisión limitada (~ciudad). Para astronomía precisa, usa coordenadas manuales.

2. **Altitud**: Crítica para cálculos precisos. Si tu observatorio está en altura, especifica la altitud correcta.

3. **Conectividad**: Los métodos automáticos requieren conexión a internet.

4. **Proveedores**: Algunos servicios de geocodificación pueden tener limitaciones de uso.

## 🚀 Ejemplo completo

```python
from ubicacion import UbicacionManager

def setup_astrotracker():
    """Configuración completa para astrotracker."""
    ubicacion_mgr = UbicacionManager()
    
    print("🌍 Configurando ubicación para Astrotracker...")
    
    # Intentar cargar configuración existente
    if ubicacion_mgr.cargar_ubicacion("astrotracker_ubicacion.json"):
        print("✅ Configuración cargada desde archivo")
    else:
        print("🔍 Detectando ubicación automáticamente...")
        ubicacion = ubicacion_mgr.obtener_ubicacion()
        
        if ubicacion:
            ubicacion_mgr.guardar_ubicacion("astrotracker_ubicacion.json")
            print("✅ Ubicación detectada y guardada")
        else:
            print("❌ Error detectando ubicación")
            return None
    
    # Mostrar información
    ubicacion_mgr.imprimir_ubicacion()
    
    # Retornar EarthLocation para cálculos astronómicos
    return ubicacion_mgr.get_earth_location()

if __name__ == "__main__":
    earth_location = setup_astrotracker()
    if earth_location is not None:
        print("🎯 Sistema listo para tracking astronómico!")
```

---

**📝 Nota**: Este sistema está optimizado para uso con sistemas astrotracker y proporciona toda la información necesaria para cálculos de seguimiento preciso de objetos celestes.