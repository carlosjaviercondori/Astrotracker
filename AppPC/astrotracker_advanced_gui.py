"""
Interfaz gráfica avanzada para Astrotracker con simulación astronómica.
Incluye seguimiento de objetos celestes, información astronómica y controles visuales.
"""

import pygame
import math
import sys
from datetime import datetime
from ubicacion import UbicacionManager
from astro_simulator import AstroTrackingSimulator, get_local_sidereal_time
import threading
import time

# Inicializar Pygame
pygame.init()

# Constantes de la interfaz
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 30

# Colores (tema espacial mejorado)
COLORS = {
    'background': (8, 12, 25),           # Azul muy oscuro
    'primary': (120, 200, 255),          # Azul claro
    'secondary': (255, 180, 80),         # Naranja dorado
    'accent': (255, 120, 180),           # Rosa brillante
    'success': (120, 255, 120),          # Verde brillante
    'warning': (255, 220, 80),           # Amarillo
    'error': (255, 120, 120),            # Rojo brillante
    'text': (230, 230, 230),             # Gris muy claro
    'panel': (20, 30, 50),               # Azul oscuro para paneles
    'border': (80, 120, 160),            # Azul medio para bordes
    'stars': (200, 220, 255),            # Blanco azulado para estrellas
    'telescope': (255, 200, 0),          # Dorado para telescopio
    'target': (255, 100, 100),           # Rojo para objetivo
}

class AdvancedAstrotrackerGUI:
    def __init__(self):
        """Inicializa la interfaz gráfica avanzada del astrotracker."""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🌌 Advanced Astrotracker Control System")
        self.clock = pygame.time.Clock()
        
        # Fuentes
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        self.font_tiny = pygame.font.Font(None, 14)
        
        # Sistema de ubicación y simulador
        self.ubicacion_mgr = UbicacionManager()
        self.simulator = None
        self.ubicacion_data = None
        self.earth_location = None
        
        # Estado del sistema
        self.system_status = "Inicializando sistema..."
        self.tracking_status = "Inactivo"
        self.last_update = None
        self.current_target = None
        self.target_coords = None
        self.telescope_pos = None
        
        # Estado de la interfaz
        self.running = True
        self.stars = self.generate_stars(150)
        self.animation_time = 0
        self.selected_target_index = 0
        self.available_targets = []
        
        # Información astronómica
        self.sun_moon_info = None
        self.sidereal_time = "00:00:00"
        
        # Inicializar sistema
        self.initialize_system()
    
    def generate_stars(self, count):
        """Genera estrellas para el fondo animado."""
        import random
        stars = []
        for _ in range(count):
            pos = pygame.math.Vector2(
                random.randint(0, WINDOW_WIDTH),
                random.randint(0, WINDOW_HEIGHT)
            )
            size = random.uniform(0.5, 2.5)
            alpha = random.randint(80, 255)
            twinkle_speed = random.uniform(0.01, 0.05)
            stars.append({
                'pos': pos, 
                'size': size, 
                'alpha': alpha,
                'twinkle_speed': twinkle_speed
            })
        return stars
    
    def initialize_system(self):
        """Inicializa el sistema de ubicación y simulador."""
        try:
            # Cargar ubicación
            if self.ubicacion_mgr.cargar_ubicacion("astrotracker_ubicacion.json"):
                self.system_status = "Ubicación cargada desde archivo"
                self.setup_simulator()
            else:
                self.system_status = "Detectando ubicación..."
                thread = threading.Thread(target=self.detect_location_async)
                thread.daemon = True
                thread.start()
        except Exception as e:
            self.system_status = f"Error inicializando sistema: {e}"
    
    def setup_simulator(self):
        """Configura el simulador astronómico."""
        try:
            self.ubicacion_data = self.ubicacion_mgr.ubicacion_actual
            self.earth_location = self.ubicacion_mgr.get_earth_location()
            
            if self.earth_location is not None:
                self.simulator = AstroTrackingSimulator(self.earth_location)
                self.available_targets = self.simulator.get_catalog_objects()
                self.system_status = "Sistema astronómico listo"
                
                # Iniciar actualizaciones periódicas
                self.start_updates()
            else:
                self.system_status = "Error: No se pudo crear EarthLocation"
                
        except Exception as e:
            self.system_status = f"Error configurando simulador: {e}"
    
    def detect_location_async(self):
        """Detecta la ubicación de forma asíncrona."""
        try:
            ubicacion = self.ubicacion_mgr.obtener_ubicacion()
            if ubicacion:
                self.ubicacion_mgr.guardar_ubicacion("astrotracker_ubicacion.json")
                self.setup_simulator()
            else:
                self.system_status = "Error: No se pudo detectar ubicación"
        except Exception as e:
            self.system_status = f"Error detectando ubicación: {e}"
        
        self.last_update = datetime.now()
    
    def start_updates(self):
        """Inicia las actualizaciones periódicas del sistema."""
        def update_loop():
            while self.running:
                self.update_astronomical_data()
                time.sleep(1)  # Actualizar cada segundo
        
        thread = threading.Thread(target=update_loop)
        thread.daemon = True
        thread.start()
    
    def update_astronomical_data(self):
        """Actualiza los datos astronómicos."""
        if not self.simulator:
            return
        
        try:
            # Actualizar tiempo sidéreo
            if self.earth_location is not None:
                self.sidereal_time = get_local_sidereal_time(self.earth_location)
            
            # Actualizar información Sol/Luna
            self.sun_moon_info = self.simulator.get_sun_moon_info()
            
            # Actualizar coordenadas del objetivo si hay uno seleccionado
            if self.current_target:
                self.target_coords = self.simulator.get_target_coordinates()
                self.telescope_pos = self.simulator.simulate_telescope_position(self.target_coords)
                
                # Actualizar estado de seguimiento
                if self.target_coords and self.target_coords.get('is_visible'):
                    self.tracking_status = f"Siguiendo {self.current_target}"
                else:
                    self.tracking_status = f"{self.current_target} no visible"
            
            self.last_update = datetime.now()
            
        except Exception as e:
            self.system_status = f"Error actualizando datos: {e}"
    
    def draw_background(self):
        """Dibuja el fondo animado con estrellas parpadeantes."""
        self.screen.fill(COLORS['background'])
        
        # Dibujar estrellas con efecto de parpadeo
        for star in self.stars:
            # Efecto de parpadeo único para cada estrella
            twinkle = math.sin(self.animation_time * star['twinkle_speed']) * 0.3
            current_alpha = max(30, min(255, star['alpha'] + twinkle * 100))
            
            # Crear superficie para la estrella
            star_surface = pygame.Surface((star['size'] * 2, star['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surface, (*COLORS['stars'], int(current_alpha)), 
                             (star['size'], star['size']), star['size'])
            
            self.screen.blit(star_surface, (star['pos'].x - star['size'], star['pos'].y - star['size']))
    
    def draw_panel(self, x, y, width, height, title="", title_color=None):
        """Dibuja un panel mejorado con efectos visuales."""
        if title_color is None:
            title_color = COLORS['primary']
        
        # Panel principal con gradiente simulado
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLORS['panel'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['border'], panel_rect, 2)
        
        # Efecto de brillo en el borde superior
        highlight_rect = pygame.Rect(x, y, width, 2)
        pygame.draw.rect(self.screen, (100, 120, 200), highlight_rect)
        
        # Título del panel
        if title:
            title_surface = self.font_medium.render(title, True, title_color)
            title_rect = title_surface.get_rect()
            title_rect.centerx = x + width // 2
            title_rect.y = y + 8
            self.screen.blit(title_surface, title_rect)
        
        return y + (35 if title else 10)
    
    def draw_location_panel(self):
        """Panel de información de ubicación."""
        panel_x, panel_y = 20, 20
        panel_width, panel_height = 320, 180
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "📍 UBICACIÓN")
        
        if self.ubicacion_data:
            info_items = [
                ("Ciudad:", self.ubicacion_data.get('ciudad', 'N/A')),
                ("País:", self.ubicacion_data.get('pais', 'N/A')),
                ("Lat:", f"{self.ubicacion_data['latitud']:.4f}°"),
                ("Lon:", f"{self.ubicacion_data['longitud']:.4f}°"),
                ("Alt:", f"{self.ubicacion_data['altitud']} m"),
            ]
            
            for i, (label, value) in enumerate(info_items):
                y_pos = content_y + 10 + i * 20
                
                label_surface = self.font_small.render(label, True, COLORS['text'])
                self.screen.blit(label_surface, (panel_x + 10, y_pos))
                
                value_surface = self.font_small.render(str(value), True, COLORS['secondary'])
                self.screen.blit(value_surface, (panel_x + 80, y_pos))
            
            # Estado EarthLocation
            earth_status = "✅ Activo" if self.earth_location is not None else "❌ Error"
            earth_color = COLORS['success'] if self.earth_location is not None else COLORS['error']
            earth_surface = self.font_tiny.render(f"Sistema: {earth_status}", True, earth_color)
            self.screen.blit(earth_surface, (panel_x + 10, content_y + 120))
        else:
            loading_surface = self.font_medium.render("Cargando ubicación...", True, COLORS['warning'])
            loading_rect = loading_surface.get_rect(center=(panel_x + panel_width//2, content_y + 60))
            self.screen.blit(loading_surface, loading_rect)
    
    def draw_telescope_status(self):
        """Panel de estado del telescopio."""
        panel_x, panel_y = 360, 20
        panel_width, panel_height = 300, 180
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, 
                                  "🔭 ESTADO TELESCOPIO", COLORS['telescope'])
        
        status_items = [
            ("Estado:", self.tracking_status),
            ("Objetivo:", self.current_target or "Ninguno"),
            ("Última act.:", self.last_update.strftime("%H:%M:%S") if self.last_update else "N/A"),
        ]
        
        for i, (label, value) in enumerate(status_items):
            y_pos = content_y + 10 + i * 20
            
            label_surface = self.font_small.render(label, True, COLORS['text'])
            self.screen.blit(label_surface, (panel_x + 10, y_pos))
            
            # Color del valor según el estado
            if "Siguiendo" in str(value):
                value_color = COLORS['success']
            elif "no visible" in str(value):
                value_color = COLORS['warning']
            else:
                value_color = COLORS['secondary']
            
            value_surface = self.font_small.render(str(value), True, value_color)
            self.screen.blit(value_surface, (panel_x + 80, y_pos))
        
        # Coordenadas del telescopio
        if self.telescope_pos:
            coord_y = content_y + 80
            coord_items = [
                f"Alt: {self.telescope_pos['telescope_alt']:.2f}°",
                f"Az: {self.telescope_pos['telescope_az']:.2f}°",
                f"Error Alt: {self.telescope_pos['tracking_error_alt']:.3f}°",
                f"Error Az: {self.telescope_pos['tracking_error_az']:.3f}°"
            ]
            
            for i, coord in enumerate(coord_items):
                coord_surface = self.font_tiny.render(coord, True, COLORS['primary'])
                self.screen.blit(coord_surface, (panel_x + 10, coord_y + i * 15))
    
    def draw_sky_map(self):
        """Dibuja un mapa del cielo simplificado."""
        center_x, center_y = 850, 350
        radius = 120
        
        # Panel contenedor
        panel_x, panel_y = center_x - 150, center_y - 150
        panel_width, panel_height = 300, 300
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "🌌 MAPA CELESTE")
        
        # Círculo del horizonte
        pygame.draw.circle(self.screen, COLORS['border'], (center_x, center_y), radius, 2)
        pygame.draw.circle(self.screen, (0, 0, 0, 50), (center_x, center_y), radius - 2)
        
        # Marcas direccionales
        directions = [
            (0, "N", COLORS['primary']),
            (90, "E", COLORS['text']),
            (180, "S", COLORS['text']),
            (270, "W", COLORS['text'])
        ]
        
        for angle, text, color in directions:
            rad = math.radians(angle - 90)
            text_x = center_x + math.cos(rad) * (radius + 20)
            text_y = center_y + math.sin(rad) * (radius + 20)
            
            text_surface = self.font_small.render(text, True, color)
            text_rect = text_surface.get_rect(center=(text_x, text_y))
            self.screen.blit(text_surface, text_rect)
        
        # Líneas de elevación (30°, 60°)
        for elev_radius in [radius * 0.33, radius * 0.66]:
            pygame.draw.circle(self.screen, (100, 100, 100), (center_x, center_y), int(elev_radius), 1)
        
        # Dibujar objetivo si existe
        if self.target_coords and self.target_coords.get('is_visible'):
            alt = self.target_coords['altitud']
            az = self.target_coords['azimut']
            
            # Convertir alt/az a coordenadas de pantalla
            # En el mapa: radio = función de altitud, ángulo = azimut
            map_radius = radius * (1 - alt / 90)  # Altitud 90° = centro, 0° = borde
            map_angle = math.radians(az - 90)  # Ajustar para que N esté arriba
            
            target_x = center_x + math.cos(map_angle) * map_radius
            target_y = center_y + math.sin(map_angle) * map_radius
            
            # Dibujar objetivo
            pygame.draw.circle(self.screen, COLORS['target'], (int(target_x), int(target_y)), 8)
            pygame.draw.circle(self.screen, COLORS['text'], (int(target_x), int(target_y)), 8, 2)
            
            # Nombre del objetivo
            name_surface = self.font_tiny.render(self.current_target, True, COLORS['target'])
            self.screen.blit(name_surface, (int(target_x) + 12, int(target_y) - 8))
        
        # Dibujar posición del telescopio
        if self.telescope_pos:
            tel_alt = self.telescope_pos['telescope_alt']
            tel_az = self.telescope_pos['telescope_az']
            
            if tel_alt > 0:  # Solo si está sobre el horizonte
                tel_map_radius = radius * (1 - tel_alt / 90)
                tel_map_angle = math.radians(tel_az - 90)
                
                tel_x = center_x + math.cos(tel_map_angle) * tel_map_radius
                tel_y = center_y + math.sin(tel_map_angle) * tel_map_radius
                
                # Dibujar telescopio
                pygame.draw.circle(self.screen, COLORS['telescope'], (int(tel_x), int(tel_y)), 6)
                pygame.draw.circle(self.screen, COLORS['text'], (int(tel_x), int(tel_y)), 6, 1)
    
    def draw_target_selector(self):
        """Dibuja el selector de objetivos."""
        panel_x, panel_y = 680, 20
        panel_width, panel_height = 320, 180
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "🎯 SELECCIONAR OBJETIVO")
        
        if self.available_targets:
            # Mostrar lista de objetivos
            visible_targets = 8
            start_index = max(0, min(self.selected_target_index - visible_targets//2, 
                                   len(self.available_targets) - visible_targets))
            
            for i in range(visible_targets):
                target_index = start_index + i
                if target_index >= len(self.available_targets):
                    break
                
                target_name = self.available_targets[target_index]
                y_pos = content_y + 10 + i * 18
                
                # Highlight del objetivo seleccionado
                if target_index == self.selected_target_index:
                    highlight_rect = pygame.Rect(panel_x + 5, y_pos - 2, panel_width - 10, 16)
                    pygame.draw.rect(self.screen, COLORS['border'], highlight_rect)
                
                # Color según si es el objetivo actual
                if target_name == self.current_target:
                    color = COLORS['success']
                    prefix = "► "
                elif target_index == self.selected_target_index:
                    color = COLORS['primary']
                    prefix = "• "
                else:
                    color = COLORS['text']
                    prefix = "  "
                
                target_surface = self.font_small.render(f"{prefix}{target_name}", True, color)
                self.screen.blit(target_surface, (panel_x + 10, y_pos))
        else:
            no_targets_surface = self.font_medium.render("No hay objetivos disponibles", True, COLORS['warning'])
            no_targets_rect = no_targets_surface.get_rect(center=(panel_x + panel_width//2, content_y + 60))
            self.screen.blit(no_targets_surface, no_targets_rect)
    
    def draw_astronomical_info(self):
        """Dibuja información astronómica adicional."""
        panel_x, panel_y = 1020, 20
        panel_width, panel_height = 360, 300
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "⭐ INFO ASTRONÓMICA")
        
        # Tiempo sidéreo
        sidereal_surface = self.font_small.render(f"Tiempo Sidéreo: {self.sidereal_time}", True, COLORS['primary'])
        self.screen.blit(sidereal_surface, (panel_x + 10, content_y + 10))
        
        # Información Sol/Luna
        if self.sun_moon_info:
            sun_info = self.sun_moon_info.get('sun', {})
            moon_info = self.sun_moon_info.get('moon', {})
            
            info_y = content_y + 35
            
            # Sol
            sun_alt = sun_info.get('altitud', 0)
            sun_status = "☀️ Visible" if sun_alt > 0 else "🌙 Oculto"
            sun_color = COLORS['warning'] if sun_alt > 0 else COLORS['success']
            
            sun_surface = self.font_small.render(f"Sol: {sun_status} ({sun_alt:.1f}°)", True, sun_color)
            self.screen.blit(sun_surface, (panel_x + 10, info_y))
            
            # Luna
            moon_alt = moon_info.get('altitud', 0)
            moon_status = "🌙 Visible" if moon_alt > 0 else "🌑 Oculta"
            moon_color = COLORS['secondary'] if moon_alt > 0 else COLORS['text']
            
            moon_surface = self.font_small.render(f"Luna: {moon_status} ({moon_alt:.1f}°)", True, moon_color)
            self.screen.blit(moon_surface, (panel_x + 10, info_y + 20))
            
            # Fase del día
            day_phase = self.sun_moon_info.get('day_phase', 'Desconocido')
            phase_colors = {
                'Noche': COLORS['success'],
                'Crepúsculo astronómico': COLORS['primary'],
                'Día': COLORS['warning']
            }
            phase_color = phase_colors.get(day_phase, COLORS['text'])
            
            phase_surface = self.font_small.render(f"Fase: {day_phase}", True, phase_color)
            self.screen.blit(phase_surface, (panel_x + 10, info_y + 45))
            
            # Condiciones de observación
            conditions = self.sun_moon_info.get('observing_conditions', 'Unknown')
            cond_color = COLORS['success'] if conditions == 'Good' else COLORS['warning']
            
            cond_surface = self.font_small.render(f"Condiciones: {conditions}", True, cond_color)
            self.screen.blit(cond_surface, (panel_x + 10, info_y + 70))
        
        # Información del objetivo actual
        if self.target_coords:
            target_y = content_y + 130
            
            target_title = self.font_small.render(f"Objetivo: {self.current_target}", True, COLORS['accent'])
            self.screen.blit(target_title, (panel_x + 10, target_y))
            
            if 'error' not in self.target_coords:
                coord_info = [
                    f"Altitud: {self.target_coords['altitud']:.2f}°",
                    f"Azimut: {self.target_coords['azimut']:.2f}°",
                    f"Magnitud: {self.target_coords['magnitude']:.2f}",
                    f"Estado: {self.target_coords['status']}"
                ]
                
                for i, info in enumerate(coord_info):
                    info_surface = self.font_tiny.render(info, True, COLORS['text'])
                    self.screen.blit(info_surface, (panel_x + 10, target_y + 20 + i * 15))
    
    def draw_controls_info(self):
        """Dibuja información de controles."""
        panel_x, panel_y = 20, 220
        panel_width, panel_height = 320, 250
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "🎮 CONTROLES")
        
        controls = [
            "NAVEGACIÓN:",
            "  ↑↓ - Seleccionar objetivo",
            "  ENTER - Seguir objetivo",
            "  SPACE - Parar seguimiento",
            "",
            "SISTEMA:",
            "  R - Recargar ubicación",
            "  M - Ubicación manual",
            "  S - Guardar configuración",
            "",
            "  ESC - Salir"
        ]
        
        for i, control in enumerate(controls):
            y_pos = content_y + 10 + i * 18
            
            if control.startswith("  "):
                color = COLORS['text']
                font = self.font_tiny
            elif control == "":
                continue
            elif control.endswith(":"):
                color = COLORS['primary']
                font = self.font_small
            else:
                color = COLORS['secondary']
                font = self.font_tiny
            
            control_surface = font.render(control, True, color)
            self.screen.blit(control_surface, (panel_x + 10, y_pos))
    
    def draw_system_status(self):
        """Dibuja el estado general del sistema."""
        panel_x, panel_y = 360, 220
        panel_width, panel_height = 640, 100
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "💫 ESTADO GENERAL")
        
        # Estado principal
        status_color = COLORS['success'] if "listo" in self.system_status else COLORS['warning']
        if "Error" in self.system_status:
            status_color = COLORS['error']
        
        status_surface = self.font_medium.render(self.system_status, True, status_color)
        self.screen.blit(status_surface, (panel_x + 10, content_y + 10))
        
        # Timestamp actual
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_surface = self.font_small.render(f"Hora local: {current_time}", True, COLORS['text'])
        self.screen.blit(time_surface, (panel_x + 10, content_y + 35))
        
        # FPS y rendimiento
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.font_tiny.render(fps_text, True, COLORS['text'])
        self.screen.blit(fps_surface, (panel_x + panel_width - 80, content_y + 60))
    
    def handle_events(self):
        """Maneja los eventos de pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_UP:
                    # Navegar objetivos hacia arriba
                    if self.available_targets:
                        self.selected_target_index = (self.selected_target_index - 1) % len(self.available_targets)
                
                elif event.key == pygame.K_DOWN:
                    # Navegar objetivos hacia abajo
                    if self.available_targets:
                        self.selected_target_index = (self.selected_target_index + 1) % len(self.available_targets)
                
                elif event.key == pygame.K_RETURN:
                    # Seleccionar objetivo para seguimiento
                    if self.available_targets and self.simulator:
                        target_name = self.available_targets[self.selected_target_index]
                        if self.simulator.set_target(target_name):
                            self.current_target = target_name
                            self.tracking_status = f"Iniciando seguimiento de {target_name}"
                
                elif event.key == pygame.K_SPACE:
                    # Parar seguimiento
                    if self.simulator:
                        self.simulator.tracking_active = False
                        self.current_target = None
                        self.target_coords = None
                        self.telescope_pos = None
                        self.tracking_status = "Seguimiento detenido"
                
                elif event.key == pygame.K_r:
                    # Recargar ubicación
                    self.system_status = "Recargando ubicación..."
                    thread = threading.Thread(target=self.detect_location_async)
                    thread.daemon = True
                    thread.start()
                
                elif event.key == pygame.K_s:
                    # Guardar configuración
                    if self.ubicacion_data:
                        self.ubicacion_mgr.guardar_ubicacion("astrotracker_ubicacion.json")
                        self.system_status = "Configuración guardada"
                
                elif event.key == pygame.K_m:
                    # Ubicación manual
                    self.ubicacion_mgr.establecer_ubicacion_manual(
                        -31.4065, -64.1885, 430, "Córdoba", "Argentina"
                    )
                    self.setup_simulator()
                    self.system_status = "Ubicación manual establecida"
    
    def run(self):
        """Bucle principal de la interfaz."""
        print("🚀 Iniciando Advanced Astrotracker GUI...")
        print("Controles:")
        print("  ↑↓ - Navegar objetivos")
        print("  ENTER - Seguir objetivo seleccionado")
        print("  SPACE - Detener seguimiento")
        print("  R - Recargar ubicación")
        print("  S - Guardar configuración")
        print("  M - Ubicación manual")
        print("  ESC - Salir")
        
        while self.running:
            self.animation_time += 1
            
            self.handle_events()
            
            # Dibujar interfaz
            self.draw_background()
            self.draw_location_panel()
            self.draw_telescope_status()
            self.draw_target_selector()
            self.draw_sky_map()
            self.draw_astronomical_info()
            self.draw_controls_info()
            self.draw_system_status()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        print("👋 Advanced Astrotracker GUI cerrado")

def main():
    """Función principal."""
    try:
        app = AdvancedAstrotrackerGUI()
        app.run()
    except Exception as e:
        print(f"Error ejecutando la interfaz: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()