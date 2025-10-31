"""
Interfaz gráfica visual para Astrotracker usando Pygame.
Proporciona una visualización en tiempo real del estado del sistema.
"""

import pygame
import math
import sys
from datetime import datetime
from ubicacion import UbicacionManager
import threading
import time

# Inicializar Pygame
pygame.init()

# Constantes de la interfaz
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Colores (tema espacial)
COLORS = {
    'background': (10, 15, 35),           # Azul oscuro espacial
    'primary': (100, 200, 255),          # Azul claro
    'secondary': (255, 200, 100),        # Amarillo/naranja
    'accent': (255, 100, 150),           # Rosa/magenta
    'success': (100, 255, 150),          # Verde claro
    'warning': (255, 255, 100),          # Amarillo
    'error': (255, 100, 100),            # Rojo claro
    'text': (220, 220, 220),             # Gris claro
    'panel': (25, 35, 60),               # Azul oscuro para paneles
    'border': (60, 80, 120),             # Azul medio para bordes
    'stars': (200, 200, 255),            # Blanco azulado para estrellas
}

class AstrotrackerGUI:
    def __init__(self):
        """Inicializa la interfaz gráfica del astrotracker."""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🌌 Astrotracker Control Panel")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Estado del sistema
        self.ubicacion_mgr = UbicacionManager()
        self.ubicacion_data = None
        self.earth_location = None
        self.system_status = "Inicializando..."
        self.last_update = None
        
        # Estado de la interfaz
        self.running = True
        self.stars = self.generate_stars(100)
        self.animation_time = 0
        
        # Cargar ubicación
        self.load_location()
    
    def generate_stars(self, count):
        """Genera estrellas para el fondo animado."""
        import random
        stars = []
        for _ in range(count):
            pos = pygame.math.Vector2(
                random.randint(0, WINDOW_WIDTH),
                random.randint(0, WINDOW_HEIGHT)
            )
            size = random.uniform(1, 3)
            alpha = random.randint(100, 255)
            stars.append({'pos': pos, 'size': size, 'alpha': alpha})
        return stars
    
    def load_location(self):
        """Carga la ubicación del sistema."""
        try:
            # Intentar cargar configuración guardada
            if self.ubicacion_mgr.cargar_ubicacion("astrotracker_ubicacion.json"):
                self.system_status = "Ubicación cargada desde archivo"
                self.ubicacion_data = self.ubicacion_mgr.ubicacion_actual
                self.earth_location = self.ubicacion_mgr.get_earth_location()
            else:
                self.system_status = "Detectando ubicación..."
                # Detectar ubicación en hilo separado para no bloquear la interfaz
                thread = threading.Thread(target=self.detect_location_async)
                thread.daemon = True
                thread.start()
        except Exception as e:
            self.system_status = f"Error cargando ubicación: {e}"
    
    def detect_location_async(self):
        """Detecta la ubicación de forma asíncrona."""
        try:
            ubicacion = self.ubicacion_mgr.obtener_ubicacion()
            if ubicacion:
                self.ubicacion_data = ubicacion
                self.earth_location = self.ubicacion_mgr.get_earth_location()
                self.system_status = "Ubicación detectada exitosamente"
                # Guardar para uso futuro
                self.ubicacion_mgr.guardar_ubicacion("astrotracker_ubicacion.json")
            else:
                self.system_status = "Error: No se pudo detectar ubicación"
        except Exception as e:
            self.system_status = f"Error detectando ubicación: {e}"
        
        self.last_update = datetime.now()
    
    def draw_background(self):
        """Dibuja el fondo animado con estrellas."""
        self.screen.fill(COLORS['background'])
        
        # Dibujar estrellas parpadeantes
        for star in self.stars:
            # Efecto de parpadeo
            alpha_variation = math.sin(self.animation_time * 0.02 + star['pos'].x * 0.01) * 30
            current_alpha = max(50, min(255, star['alpha'] + alpha_variation))
            
            # Crear superficie temporal para alpha
            star_surface = pygame.Surface((star['size'] * 2, star['size'] * 2))
            star_surface.set_alpha(current_alpha)
            star_surface.fill(COLORS['stars'])
            
            self.screen.blit(star_surface, (star['pos'].x - star['size'], star['pos'].y - star['size']))
    
    def draw_panel(self, x, y, width, height, title=""):
        """Dibuja un panel con borde y título."""
        # Panel principal
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLORS['panel'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['border'], panel_rect, 2)
        
        # Título del panel
        if title:
            title_surface = self.font_medium.render(title, True, COLORS['primary'])
            title_rect = title_surface.get_rect()
            title_rect.centerx = x + width // 2
            title_rect.y = y + 10
            self.screen.blit(title_surface, title_rect)
        
        return y + (40 if title else 10)  # Retorna la posición Y para contenido
    
    def draw_location_panel(self):
        """Dibuja el panel de información de ubicación."""
        panel_x, panel_y = 20, 20
        panel_width, panel_height = 380, 300
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "📍 UBICACIÓN")
        
        if self.ubicacion_data:
            # Información de ubicación
            info_items = [
                ("Ciudad:", self.ubicacion_data.get('ciudad', 'N/A')),
                ("País:", self.ubicacion_data.get('pais', 'N/A')),
                ("Región:", self.ubicacion_data.get('region', 'N/A')),
                ("Latitud:", f"{self.ubicacion_data['latitud']:.6f}°"),
                ("Longitud:", f"{self.ubicacion_data['longitud']:.6f}°"),
                ("Altitud:", f"{self.ubicacion_data['altitud']} m"),
                ("Proveedor:", self.ubicacion_data.get('proveedor', 'N/A')),
            ]
            
            for i, (label, value) in enumerate(info_items):
                y_pos = content_y + 25 + i * 25
                
                # Etiqueta
                label_surface = self.font_small.render(label, True, COLORS['text'])
                self.screen.blit(label_surface, (panel_x + 15, y_pos))
                
                # Valor
                value_surface = self.font_small.render(str(value), True, COLORS['secondary'])
                self.screen.blit(value_surface, (panel_x + 120, y_pos))
            
            # Indicador de EarthLocation
            earth_status = "✅ Activo" if self.earth_location is not None else "❌ No disponible"
            earth_color = COLORS['success'] if self.earth_location is not None else COLORS['error']
            
            earth_surface = self.font_small.render(f"EarthLocation: {earth_status}", True, earth_color)
            self.screen.blit(earth_surface, (panel_x + 15, content_y + 200))
            
        else:
            # Mensaje de carga
            loading_surface = self.font_medium.render("Cargando ubicación...", True, COLORS['warning'])
            loading_rect = loading_surface.get_rect()
            loading_rect.centerx = panel_x + panel_width // 2
            loading_rect.y = content_y + 100
            self.screen.blit(loading_surface, loading_rect)
    
    def draw_status_panel(self):
        """Dibuja el panel de estado del sistema."""
        panel_x, panel_y = 420, 20
        panel_width, panel_height = 360, 150
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "⚡ ESTADO DEL SISTEMA")
        
        # Estado actual
        status_color = COLORS['success'] if "exitosamente" in self.system_status else COLORS['warning']
        if "Error" in self.system_status:
            status_color = COLORS['error']
        
        status_surface = self.font_small.render(self.system_status, True, status_color)
        self.screen.blit(status_surface, (panel_x + 15, content_y + 20))
        
        # Timestamp
        if self.last_update:
            time_str = self.last_update.strftime("%H:%M:%S")
            time_surface = self.font_small.render(f"Última actualización: {time_str}", True, COLORS['text'])
            self.screen.blit(time_surface, (panel_x + 15, content_y + 45))
        
        # Estado de conexión
        connection_status = "🌐 Conectado" if self.ubicacion_data else "🔌 Desconectado"
        connection_color = COLORS['success'] if self.ubicacion_data else COLORS['error']
        connection_surface = self.font_small.render(connection_status, True, connection_color)
        self.screen.blit(connection_surface, (panel_x + 15, content_y + 70))
    
    def draw_compass(self):
        """Dibuja una brújula visual con la orientación."""
        center_x, center_y = 900, 200
        radius = 80
        
        # Círculo exterior
        pygame.draw.circle(self.screen, COLORS['border'], (center_x, center_y), radius + 5, 3)
        pygame.draw.circle(self.screen, COLORS['panel'], (center_x, center_y), radius)
        
        # Marcas cardinales
        directions = [
            (0, "N", COLORS['primary']),
            (90, "E", COLORS['text']),
            (180, "S", COLORS['text']),
            (270, "W", COLORS['text'])
        ]
        
        for angle, text, color in directions:
            rad = math.radians(angle - 90)
            text_x = center_x + math.cos(rad) * (radius - 20)
            text_y = center_y + math.sin(rad) * (radius - 20)
            
            text_surface = self.font_medium.render(text, True, color)
            text_rect = text_surface.get_rect(center=(text_x, text_y))
            self.screen.blit(text_surface, text_rect)
        
        # Aguja (apuntando al norte por ahora)
        needle_angle = self.animation_time * 0.5  # Rotación lenta para demo
        needle_rad = math.radians(needle_angle - 90)
        needle_end_x = center_x + math.cos(needle_rad) * (radius - 30)
        needle_end_y = center_y + math.sin(needle_rad) * (radius - 30)
        
        pygame.draw.line(self.screen, COLORS['accent'], (center_x, center_y), 
                        (needle_end_x, needle_end_y), 3)
        pygame.draw.circle(self.screen, COLORS['accent'], (center_x, center_y), 5)
    
    def draw_coordinates_display(self):
        """Dibuja un display de coordenadas astronómicas."""
        panel_x, panel_y = 800, 300
        panel_width, panel_height = 380, 200
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "🌌 COORDENADAS")
        
        if self.earth_location is not None:
            # Información astronómica
            astro_info = [
                ("Latitud astronómica:", f"{self.earth_location.lat}"),
                ("Longitud astronómica:", f"{self.earth_location.lon}"),
                ("Altura:", f"{self.earth_location.height}"),
                ("Tiempo sidéreo:", f"{datetime.now().strftime('%H:%M:%S')} LST"),
            ]
            
            for i, (label, value) in enumerate(astro_info):
                y_pos = content_y + 20 + i * 25
                
                label_surface = self.font_small.render(label, True, COLORS['text'])
                self.screen.blit(label_surface, (panel_x + 15, y_pos))
                
                value_surface = self.font_small.render(str(value), True, COLORS['primary'])
                self.screen.blit(value_surface, (panel_x + 15, y_pos + 15))
        else:
            no_data_surface = self.font_medium.render("Coordenadas no disponibles", True, COLORS['warning'])
            no_data_rect = no_data_surface.get_rect()
            no_data_rect.centerx = panel_x + panel_width // 2
            no_data_rect.y = content_y + 80
            self.screen.blit(no_data_surface, no_data_rect)
    
    def draw_controls(self):
        """Dibuja los controles de la interfaz."""
        panel_x, panel_y = 20, 340
        panel_width, panel_height = 380, 200
        
        content_y = self.draw_panel(panel_x, panel_y, panel_width, panel_height, "🎮 CONTROLES")
        
        controls = [
            "R - Recargar ubicación",
            "M - Ubicación manual",
            "S - Guardar configuración",
            "ESC - Salir",
            "",
            "Estado: Sistema activo"
        ]
        
        for i, control in enumerate(controls):
            y_pos = content_y + 20 + i * 20
            color = COLORS['success'] if "Estado:" in control else COLORS['text']
            control_surface = self.font_small.render(control, True, color)
            self.screen.blit(control_surface, (panel_x + 15, y_pos))
    
    def draw_title(self):
        """Dibuja el título principal."""
        title = "🌌 ASTROTRACKER CONTROL PANEL"
        title_surface = self.font_large.render(title, True, COLORS['primary'])
        title_rect = title_surface.get_rect()
        title_rect.centerx = WINDOW_WIDTH // 2
        title_rect.y = 550
        self.screen.blit(title_surface, title_rect)
        
        # Subtítulo
        subtitle = f"Sistema de seguimiento astronómico - {datetime.now().strftime('%d/%m/%Y')}"
        subtitle_surface = self.font_small.render(subtitle, True, COLORS['text'])
        subtitle_rect = subtitle_surface.get_rect()
        subtitle_rect.centerx = WINDOW_WIDTH // 2
        subtitle_rect.y = 580
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    def handle_events(self):
        """Maneja los eventos de pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
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
                    # Ubicación manual (ejemplo: Córdoba)
                    self.ubicacion_mgr.establecer_ubicacion_manual(
                        -31.4065, -64.1885, 430, "Córdoba", "Argentina"
                    )
                    self.ubicacion_data = self.ubicacion_mgr.ubicacion_actual
                    self.earth_location = self.ubicacion_mgr.get_earth_location()
                    self.system_status = "Ubicación manual establecida"
    
    def run(self):
        """Bucle principal de la interfaz."""
        print("🚀 Iniciando Astrotracker GUI...")
        print("Controles:")
        print("  R - Recargar ubicación")
        print("  M - Ubicación manual")
        print("  S - Guardar configuración")
        print("  ESC - Salir")
        
        while self.running:
            self.animation_time += 1
            
            self.handle_events()
            
            # Dibujar interfaz
            self.draw_background()
            self.draw_location_panel()
            self.draw_status_panel()
            self.draw_compass()
            self.draw_coordinates_display()
            self.draw_controls()
            self.draw_title()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        print("👋 Astrotracker GUI cerrado")

def main():
    """Función principal."""
    try:
        app = AstrotrackerGUI()
        app.run()
    except Exception as e:
        print(f"Error ejecutando la interfaz: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()