"""
Módulo para obtener y manejar datos de ubicación geográfica
para el sistema astrotracker usando geocoder.
"""

import geocoder
import json
from astropy.coordinates import EarthLocation
import astropy.units as u
from datetime import datetime

class UbicacionManager:
    def __init__(self):
        self.ubicacion_actual = None
        self.earth_location = None
        
    def obtener_ubicacion_automatica(self):
        """
        Obtiene la ubicación automáticamente usando geocoder con IP.
        """
        try:
            # Usando geocoder para obtener ubicación por IP
            g = geocoder.ip('me')
            
            if g.ok:
                self.ubicacion_actual = {
                    'latitud': g.latlng[0] if g.latlng else None,
                    'longitud': g.latlng[1] if g.latlng else None,
                    'ciudad': g.city,
                    'pais': g.country,
                    'region': g.state,
                    'timezone': getattr(g, 'timezone', ''),
                    'direccion': g.address,
                    'altitud': 0,  # Por defecto, se puede ajustar manualmente
                    'timestamp': datetime.now().isoformat(),
                    'proveedor': g.provider
                }
                
                # Crear objeto EarthLocation para cálculos astronómicos
                if self.ubicacion_actual['latitud'] and self.ubicacion_actual['longitud']:
                    self.earth_location = EarthLocation(
                        lat=self.ubicacion_actual['latitud'] * u.deg,
                        lon=self.ubicacion_actual['longitud'] * u.deg,
                        height=self.ubicacion_actual['altitud'] * u.m
                    )
                
                return self.ubicacion_actual
            else:
                print(f"Error con geocoder: {g.error}")
                return None
            
        except Exception as e:
            print(f"Error obteniendo ubicación con geocoder: {e}")
            return None
    
    def obtener_ubicacion_alternativa(self):
        """
        Método alternativo usando diferentes proveedores de geocoder.
        """
        proveedores = ['ipapi', 'freegeoip', 'maxmind']
        
        for proveedor in proveedores:
            try:
                print(f"Intentando con proveedor: {proveedor}")
                
                if proveedor == 'ipapi':
                    g = geocoder.ipapi('me')
                elif proveedor == 'freegeoip':
                    g = geocoder.freegeoip('me')
                elif proveedor == 'maxmind':
                    g = geocoder.maxmind('me')
                
                if g.ok:
                    self.ubicacion_actual = {
                        'latitud': g.latlng[0] if g.latlng else None,
                        'longitud': g.latlng[1] if g.latlng else None,
                        'ciudad': g.city,
                        'pais': g.country,
                        'region': g.state,
                        'timezone': getattr(g, 'timezone', ''),
                        'direccion': g.address,
                        'altitud': 0,
                        'timestamp': datetime.now().isoformat(),
                        'proveedor': proveedor
                    }
                    
                    # Crear objeto EarthLocation
                    if self.ubicacion_actual['latitud'] and self.ubicacion_actual['longitud']:
                        self.earth_location = EarthLocation(
                            lat=self.ubicacion_actual['latitud'] * u.deg,
                            lon=self.ubicacion_actual['longitud'] * u.deg,
                            height=self.ubicacion_actual['altitud'] * u.m
                        )
                    
                    print(f"✓ Ubicación obtenida con {proveedor}")
                    return self.ubicacion_actual
                else:
                    print(f"✗ Fallo con {proveedor}: {g.error}")
                    
            except Exception as e:
                print(f"✗ Error con {proveedor}: {e}")
                continue
        
        print("No se pudo obtener ubicación con ningún proveedor")
        return None
    
    def establecer_ubicacion_manual(self, latitud, longitud, altitud=0, ciudad="", pais=""):
        """
        Permite establecer la ubicación manualmente para mayor precisión.
        
        Args:
            latitud (float): Latitud en grados decimales
            longitud (float): Longitud en grados decimales
            altitud (float): Altitud en metros sobre el nivel del mar
            ciudad (str): Nombre de la ciudad (opcional)
            pais (str): Nombre del país (opcional)
        """
        self.ubicacion_actual = {
            'latitud': latitud,
            'longitud': longitud,
            'ciudad': ciudad,
            'pais': pais,
            'region': "",
            'timezone': "",
            'altitud': altitud,
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear objeto EarthLocation
        self.earth_location = EarthLocation(
            lat=latitud * u.deg,
            lon=longitud * u.deg,
            height=altitud * u.m
        )
        
        return self.ubicacion_actual
    
    def obtener_ubicacion(self, intentar_automatico=True):
        """
        Método principal para obtener ubicación.
        Intenta automático primero, luego alternativo.
        """
        if intentar_automatico:
            ubicacion = self.obtener_ubicacion_automatica()
            if ubicacion is None:
                print("Intentando API alternativa...")
                ubicacion = self.obtener_ubicacion_alternativa()
            return ubicacion
        else:
            return self.ubicacion_actual
    
    def obtener_ubicacion_por_direccion(self, direccion):
        """
        Obtiene coordenadas a partir de una dirección usando geocoder.
        Prueba múltiples proveedores para mayor confiabilidad.
        
        Args:
            direccion (str): Dirección a geocodificar (ej: "Madrid, España")
        """
        proveedores_geocoding = [
            ('arcgis', lambda d: geocoder.arcgis(d)),
            ('here', lambda d: geocoder.here(d)),
            ('bing', lambda d: geocoder.bing(d)),
        ]
        
        for proveedor_nombre, proveedor_func in proveedores_geocoding:
            try:
                print(f"Intentando geocodificar con {proveedor_nombre}...")
                g = proveedor_func(direccion)
                
                if g.ok and g.latlng:
                    self.ubicacion_actual = {
                        'latitud': g.latlng[0],
                        'longitud': g.latlng[1],
                        'ciudad': g.city,
                        'pais': g.country,
                        'region': g.state,
                        'timezone': '',
                        'direccion': g.address,
                        'altitud': 0,
                        'timestamp': datetime.now().isoformat(),
                        'proveedor': proveedor_nombre
                    }
                    
                    # Crear objeto EarthLocation
                    self.earth_location = EarthLocation(
                        lat=self.ubicacion_actual['latitud'] * u.deg,
                        lon=self.ubicacion_actual['longitud'] * u.deg,
                        height=self.ubicacion_actual['altitud'] * u.m
                    )
                    
                    print(f"✅ Geocodificación exitosa con {proveedor_nombre}")
                    return self.ubicacion_actual
                else:
                    print(f"❌ {proveedor_nombre} no pudo geocodificar")
                    
            except Exception as e:
                print(f"❌ Error con {proveedor_nombre}: {e}")
                continue
        
        print(f"❌ No se pudo geocodificar la dirección: {direccion}")
        return None
    
    def obtener_informacion_detallada(self):
        """
        Obtiene información más detallada usando geocodificación inversa.
        """
        if not self.ubicacion_actual:
            self.obtener_ubicacion()
        
        if self.ubicacion_actual and self.ubicacion_actual['latitud']:
            try:
                # Usar las coordenadas para obtener más información con geocodificación inversa
                lat, lon = self.ubicacion_actual['latitud'], self.ubicacion_actual['longitud']
                
                # Intentar con diferentes proveedores
                proveedores_reverse = [
                    ('arcgis', lambda: geocoder.arcgis([lat, lon], method='reverse')),
                    ('here', lambda: geocoder.here([lat, lon], method='reverse')),
                ]
                
                for proveedor, func in proveedores_reverse:
                    try:
                        g = func()
                        if g.ok:
                            self.ubicacion_actual.update({
                                'direccion_completa': g.address,
                                'codigo_postal': getattr(g, 'postal', ''),
                                'barrio': getattr(g, 'neighborhood', ''),
                                'proveedor_detalle': proveedor
                            })
                            print(f"✅ Información detallada obtenida con {proveedor}")
                            break
                    except Exception as e:
                        print(f"Error con {proveedor}: {e}")
                        continue
                
                return self.ubicacion_actual
                
            except Exception as e:
                print(f"Error obteniendo información detallada: {e}")
        
        return self.ubicacion_actual
    
    def get_earth_location(self):
        """
        Retorna el objeto EarthLocation para cálculos astronómicos.
        """
        return self.earth_location
    
    def imprimir_ubicacion(self):
        """
        Imprime la información de ubicación de forma legible.
        """
        if self.ubicacion_actual:
            print("=" * 50)
            print("INFORMACIÓN DE UBICACIÓN")
            print("=" * 50)
            print(f"Ciudad: {self.ubicacion_actual.get('ciudad', 'N/A')}")
            print(f"País: {self.ubicacion_actual.get('pais', 'N/A')}")
            print(f"Región: {self.ubicacion_actual.get('region', 'N/A')}")
            print(f"Latitud: {self.ubicacion_actual['latitud']:.6f}°")
            print(f"Longitud: {self.ubicacion_actual['longitud']:.6f}°")
            print(f"Altitud: {self.ubicacion_actual['altitud']} m")
            print(f"Zona horaria: {self.ubicacion_actual.get('timezone', 'N/A')}")
            print(f"Actualizado: {self.ubicacion_actual['timestamp']}")
            print("=" * 50)
        else:
            print("No hay información de ubicación disponible.")
    
    def guardar_ubicacion(self, archivo="ubicacion_config.json"):
        """
        Guarda la ubicación actual en un archivo JSON.
        """
        if self.ubicacion_actual:
            try:
                with open(archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.ubicacion_actual, f, indent=4, ensure_ascii=False)
                print(f"Ubicación guardada en {archivo}")
                return True
            except Exception as e:
                print(f"Error guardando ubicación: {e}")
                return False
        return False
    
    def cargar_ubicacion(self, archivo="ubicacion_config.json"):
        """
        Carga la ubicación desde un archivo JSON.
        """
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                self.ubicacion_actual = json.load(f)
                
            # Recrear EarthLocation
            if self.ubicacion_actual.get('latitud') and self.ubicacion_actual.get('longitud'):
                self.earth_location = EarthLocation(
                    lat=self.ubicacion_actual['latitud'] * u.deg,
                    lon=self.ubicacion_actual['longitud'] * u.deg,
                    height=self.ubicacion_actual.get('altitud', 0) * u.m
                )
            
            print(f"Ubicación cargada desde {archivo}")
            return self.ubicacion_actual
        except FileNotFoundError:
            print(f"Archivo {archivo} no encontrado.")
            return None
        except Exception as e:
            print(f"Error cargando ubicación: {e}")
            return None


# Función de conveniencia para uso rápido
def obtener_ubicacion_rapida():
    """
    Función rápida para obtener ubicación sin crear una instancia de clase.
    """
    manager = UbicacionManager()
    return manager.obtener_ubicacion()


# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del manager
    ubicacion_mgr = UbicacionManager()
    
    # Intentar obtener ubicación automáticamente
    print("Obteniendo ubicación...")
    ubicacion = ubicacion_mgr.obtener_ubicacion()
    
    if ubicacion:
        ubicacion_mgr.imprimir_ubicacion()
        
        # Guardar para uso posterior
        ubicacion_mgr.guardar_ubicacion()
        
        # Obtener objeto EarthLocation para cálculos astronómicos
        earth_loc = ubicacion_mgr.get_earth_location()
        if earth_loc:
            print(f"\nObjeto EarthLocation creado:")
            print(f"Latitud: {earth_loc.lat}")
            print(f"Longitud: {earth_loc.lon}")
            print(f"Altura: {earth_loc.height}")
    else:
        print("No se pudo obtener la ubicación automáticamente.")
        print("Puedes establecer la ubicación manualmente:")
        print("ubicacion_mgr.establecer_ubicacion_manual(lat, lon, altitud)")
        
        
