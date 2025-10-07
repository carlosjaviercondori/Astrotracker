"""
Ejemplo de integración del sistema de ubicación con el astrotracker.
Demuestra cómo usar la ubicación para cálculos astronómicos.
"""

from ubicacion import UbicacionManager
from astropy.coordinates import SkyCoord, AltAz, get_sun, get_moon
from astropy.time import Time
import astropy.units as u
from datetime import datetime

class AstroTrackerConUbicacion:
    def __init__(self):
        self.ubicacion_manager = UbicacionManager()
        self.earth_location = None
        self.inicializar_ubicacion()
    
    def inicializar_ubicacion(self):
        """
        Inicializa la ubicación del astrotracker.
        """
        print("Inicializando ubicación del astrotracker...")
        
        # Primero intenta cargar ubicación guardada
        ubicacion_guardada = self.ubicacion_manager.cargar_ubicacion()
        
        if not ubicacion_guardada:
            # Si no hay ubicación guardada, obtiene automáticamente
            print("No hay ubicación guardada, obteniendo automáticamente...")
            ubicacion = self.ubicacion_manager.obtener_ubicacion()
            
            if ubicacion:
                self.ubicacion_manager.guardar_ubicacion()
            else:
                print("Error: No se pudo obtener la ubicación.")
                return False
        
        self.earth_location = self.ubicacion_manager.get_earth_location()
        self.ubicacion_manager.imprimir_ubicacion()
        return True
    
    def calcular_posicion_sol(self, tiempo=None):
        """
        Calcula la posición del Sol para la ubicación actual.
        """
        if not self.earth_location:
            print("Error: Ubicación no inicializada.")
            return None
        
        if tiempo is None:
            tiempo = Time.now()
        
        # Obtener posición del Sol
        sun = get_sun(tiempo)
        
        # Convertir a coordenadas Alt-Az para la ubicación actual
        altaz_frame = AltAz(obstime=tiempo, location=self.earth_location)
        sun_altaz = sun.transform_to(altaz_frame)
        
        return {
            'elevacion': sun_altaz.alt.degree,
            'azimuth': sun_altaz.az.degree,
            'tiempo': tiempo.iso
        }
    
    def calcular_posicion_luna(self, tiempo=None):
        """
        Calcula la posición de la Luna para la ubicación actual.
        """
        if not self.earth_location:
            print("Error: Ubicación no inicializada.")
            return None
        
        if tiempo is None:
            tiempo = Time.now()
        
        # Obtener posición de la Luna
        moon = get_moon(tiempo)
        
        # Convertir a coordenadas Alt-Az
        altaz_frame = AltAz(obstime=tiempo, location=self.earth_location)
        moon_altaz = moon.transform_to(altaz_frame)
        
        return {
            'elevacion': moon_altaz.alt.degree,
            'azimuth': moon_altaz.az.degree,
            'tiempo': tiempo.iso
        }
    
    def calcular_posicion_estrella(self, ra, dec, tiempo=None):
        """
        Calcula la posición de una estrella dadas sus coordenadas RA/Dec.
        
        Args:
            ra: Ascensión recta en grados
            dec: Declinación en grados
            tiempo: Tiempo de observación (opcional)
        """
        if not self.earth_location:
            print("Error: Ubicación no inicializada.")
            return None
        
        if tiempo is None:
            tiempo = Time.now()
        
        # Crear coordenada de la estrella
        star = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
        
        # Convertir a coordenadas Alt-Az
        altaz_frame = AltAz(obstime=tiempo, location=self.earth_location)
        star_altaz = star.transform_to(altaz_frame)
        
        return {
            'elevacion': star_altaz.alt.degree,
            'azimuth': star_altaz.az.degree,
            'ra': ra,
            'dec': dec,
            'tiempo': tiempo.iso
        }
    
    def es_objeto_visible(self, elevacion, elevacion_minima=10):
        """
        Determina si un objeto es visible basado en su elevación.
        
        Args:
            elevacion: Elevación del objeto en grados
            elevacion_minima: Elevación mínima para considerar visible
        """
        return elevacion > elevacion_minima
    
    def obtener_info_observacion(self):
        """
        Obtiene información completa para la observación actual.
        """
        if not self.earth_location:
            print("Error: Ubicación no inicializada.")
            return None
        
        tiempo_actual = Time.now()
        
        # Calcular posiciones
        sol = self.calcular_posicion_sol(tiempo_actual)
        luna = self.calcular_posicion_luna(tiempo_actual)
        
        # Determinar si es de noche (Sol bajo el horizonte)
        es_noche = sol['elevacion'] < -6  # Crepúsculo astronómico
        
        info = {
            'tiempo': tiempo_actual.iso,
            'ubicacion': self.ubicacion_manager.ubicacion_actual,
            'sol': sol,
            'luna': luna,
            'es_noche': es_noche,
            'condiciones_observacion': 'Buenas' if es_noche and luna['elevacion'] < 30 else 'Regular'
        }
        
        return info
    
    def imprimir_info_observacion(self):
        """
        Imprime información detallada de las condiciones de observación.
        """
        info = self.obtener_info_observacion()
        if not info:
            return
        
        print("\n" + "="*60)
        print("INFORMACIÓN DE OBSERVACIÓN ASTRONÓMICA")
        print("="*60)
        print(f"Fecha y hora: {info['tiempo']}")
        print(f"Ubicación: {info['ubicacion']['ciudad']}, {info['ubicacion']['pais']}")
        print(f"Coordenadas: {info['ubicacion']['latitud']:.4f}°, {info['ubicacion']['longitud']:.4f}°")
        print()
        print("POSICIÓN DEL SOL:")
        print(f"  Elevación: {info['sol']['elevacion']:.2f}°")
        print(f"  Azimuth: {info['sol']['azimuth']:.2f}°")
        print(f"  Es de noche: {'Sí' if info['es_noche'] else 'No'}")
        print()
        print("POSICIÓN DE LA LUNA:")
        print(f"  Elevación: {info['luna']['elevacion']:.2f}°")
        print(f"  Azimuth: {info['luna']['azimuth']:.2f}°")
        print(f"  Visible: {'Sí' if self.es_objeto_visible(info['luna']['elevacion']) else 'No'}")
        print()
        print(f"Condiciones para observación: {info['condiciones_observacion']}")
        print("="*60)


# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del astrotracker
    astrotracker = AstroTrackerConUbicacion()
    
    if astrotracker.earth_location:
        # Mostrar información de observación
        astrotracker.imprimir_info_observacion()
        
        # Ejemplo: calcular posición de una estrella famosa (Vega)
        print("\nEjemplo - Posición de Vega:")
        vega = astrotracker.calcular_posicion_estrella(279.23, 38.78)  # RA y Dec de Vega
        if vega:
            print(f"Elevación: {vega['elevacion']:.2f}°")
            print(f"Azimuth: {vega['azimuth']:.2f}°")
            print(f"Visible: {'Sí' if astrotracker.es_objeto_visible(vega['elevacion']) else 'No'}")
    else:
        print("No se pudo inicializar el astrotracker.")