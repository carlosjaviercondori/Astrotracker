"""
Módulo de simulación y cálculos astronómicos para el astrotracker.
Proporciona funciones para simular el seguimiento de objetos celestes.
"""

import math
from datetime import datetime, timezone
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.time import Time
import astropy.units as u

class AstroTrackingSimulator:
    def __init__(self, earth_location=None):
        """
        Inicializa el simulador de seguimiento astronómico.
        
        Args:
            earth_location: Objeto EarthLocation con la ubicación del observatorio
        """
        self.earth_location = earth_location
        self.target_object = None
        self.tracking_active = False
        
        # Objetos celestes populares (RA, Dec en grados)
        self.catalog = {
            'Sirius': {'ra': 101.287, 'dec': -16.716, 'magnitude': -1.46},
            'Vega': {'ra': 279.234, 'dec': 38.784, 'magnitude': 0.03},
            'Polaris': {'ra': 37.946, 'dec': 89.264, 'magnitude': 1.97},
            'Betelgeuse': {'ra': 88.793, 'dec': 7.407, 'magnitude': 0.50},
            'Rigel': {'ra': 78.634, 'dec': -8.202, 'magnitude': 0.13},
            'Aldebaran': {'ra': 68.980, 'dec': 16.509, 'magnitude': 0.85},
            'Capella': {'ra': 79.172, 'dec': 45.998, 'magnitude': 0.08},
            'Arcturus': {'ra': 213.915, 'dec': 19.182, 'magnitude': -0.05},
            'Antares': {'ra': 247.352, 'dec': -26.432, 'magnitude': 1.09},
        }
    
    def set_target(self, target_name):
        """
        Establece un objeto celeste como objetivo.
        
        Args:
            target_name: Nombre del objeto en el catálogo
        """
        if target_name in self.catalog:
            self.target_object = target_name
            self.tracking_active = True
            return True
        return False
    
    def get_target_coordinates(self, timestamp=None):
        """
        Calcula las coordenadas horizontales del objetivo.
        
        Args:
            timestamp: Tiempo específico (por defecto: ahora)
            
        Returns:
            dict: Coordenadas altitud/azimut y estado
        """
        if not self.target_object or not self.earth_location:
            return None
        
        try:
            # Tiempo de observación
            if timestamp is None:
                observing_time = Time.now()
            else:
                observing_time = Time(timestamp)
            
            # Obtener coordenadas del catálogo
            target_data = self.catalog[self.target_object]
            
            # Crear coordenadas ecuatoriales
            target_coord = SkyCoord(
                ra=target_data['ra'] * u.deg,
                dec=target_data['dec'] * u.deg,
                frame='icrs'
            )
            
            # Marco de referencia horizontal
            altaz_frame = AltAz(obstime=observing_time, location=self.earth_location)
            
            # Transformar a coordenadas horizontales
            target_altaz = target_coord.transform_to(altaz_frame)
            
            # Estado de visibilidad
            is_visible = target_altaz.alt.deg > 0
            visibility_status = "Visible" if is_visible else "Bajo el horizonte"
            
            return {
                'name': self.target_object,
                'altitud': target_altaz.alt.deg,
                'azimut': target_altaz.az.deg,
                'magnitude': target_data['magnitude'],
                'is_visible': is_visible,
                'status': visibility_status,
                'timestamp': observing_time.iso
            }
            
        except Exception as e:
            return {
                'name': self.target_object,
                'error': str(e),
                'status': 'Error en cálculo'
            }
    
    def get_catalog_objects(self):
        """Retorna la lista de objetos disponibles en el catálogo."""
        return list(self.catalog.keys())
    
    def calculate_tracking_rates(self):
        """
        Calcula las velocidades de seguimiento necesarias.
        
        Returns:
            dict: Velocidades en grados/hora para RA y Dec
        """
        if not self.tracking_active:
            return None
        
        # Velocidad sidérea básica
        sidereal_rate = 15.0  # grados/hora
        
        # Para objetos estelares, la velocidad de seguimiento es principalmente sidérea
        # En un sistema real, esto sería más complejo incluyendo refracción, etc.
        
        return {
            'ra_rate': sidereal_rate,  # Ascensión recta
            'dec_rate': 0.0,          # Declinación (constante para estrellas)
            'units': 'grados/hora'
        }
    
    def simulate_telescope_position(self, target_coords):
        """
        Simula la posición actual del telescopio siguiendo el objetivo.
        
        Args:
            target_coords: Coordenadas del objetivo
            
        Returns:
            dict: Posición simulada del telescopio
        """
        if not target_coords or 'error' in target_coords:
            return {
                'telescope_alt': 0.0,
                'telescope_az': 0.0,
                'tracking_error_alt': 0.0,
                'tracking_error_az': 0.0,
                'status': 'No tracking'
            }
        
        # Simular pequeños errores de seguimiento (realista)
        import random
        error_range = 0.1  # grados
        
        tracking_error_alt = random.uniform(-error_range, error_range)
        tracking_error_az = random.uniform(-error_range, error_range)
        
        telescope_alt = target_coords['altitud'] + tracking_error_alt
        telescope_az = target_coords['azimut'] + tracking_error_az
        
        return {
            'telescope_alt': telescope_alt,
            'telescope_az': telescope_az,
            'tracking_error_alt': tracking_error_alt,
            'tracking_error_az': tracking_error_az,
            'status': 'Tracking active'
        }
    
    def get_sun_moon_info(self):
        """
        Obtiene información básica del Sol y la Luna.
        
        Returns:
            dict: Información solar y lunar
        """
        if not self.earth_location:
            return None
        
        try:
            from astropy.coordinates import get_sun, get_moon
            
            observing_time = Time.now()
            altaz_frame = AltAz(obstime=observing_time, location=self.earth_location)
            
            # Posición del Sol
            sun_coord = get_sun(observing_time)
            sun_altaz = sun_coord.transform_to(altaz_frame)
            
            # Posición de la Luna
            moon_coord = get_moon(observing_time)
            moon_altaz = moon_coord.transform_to(altaz_frame)
            
            # Determinar fase del día
            sun_alt = sun_altaz.alt.deg
            if sun_alt > 6:
                day_phase = "Día"
            elif sun_alt > -6:
                day_phase = "Crepúsculo"
            elif sun_alt > -12:
                day_phase = "Crepúsculo náutico"
            elif sun_alt > -18:
                day_phase = "Crepúsculo astronómico"
            else:
                day_phase = "Noche"
            
            return {
                'sun': {
                    'altitud': sun_alt,
                    'azimut': sun_altaz.az.deg,
                    'visible': sun_alt > 0
                },
                'moon': {
                    'altitud': moon_altaz.alt.deg,
                    'azimut': moon_altaz.az.deg,
                    'visible': moon_altaz.alt.deg > 0
                },
                'day_phase': day_phase,
                'observing_conditions': 'Good' if day_phase == "Noche" else 'Poor'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'Error calculando Sol/Luna'
            }

def get_local_sidereal_time(earth_location):
    """
    Calcula el tiempo sidéreo local.
    
    Args:
        earth_location: Ubicación del observatorio
        
    Returns:
        str: Tiempo sidéreo local en formato HH:MM:SS
    """
    try:
        from astropy.time import Time
        from astropy.coordinates import EarthLocation
        
        now = Time.now()
        lst = now.sidereal_time('mean', longitude=earth_location.lon)
        
        # Convertir a horas, minutos, segundos
        hours = int(lst.hour)
        minutes = int((lst.hour - hours) * 60)
        seconds = int(((lst.hour - hours) * 60 - minutes) * 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
    except Exception as e:
        return f"Error: {e}"

# Función de conveniencia
def create_simulator(ubicacion_mgr):
    """
    Crea un simulador usando un UbicacionManager.
    
    Args:
        ubicacion_mgr: Instancia de UbicacionManager
        
    Returns:
        AstroTrackingSimulator: Simulador configurado
    """
    earth_location = ubicacion_mgr.get_earth_location()
    return AstroTrackingSimulator(earth_location)