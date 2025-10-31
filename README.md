# Astrotracker

Resumen breve de los componentes principales del proyecto:

## AppPC — Interfaz gráfica
- Archivo: [AppPC/astrotracker_programa.py](AppPC/astrotracker_programa.py)  
- Qué hace: Proporciona una interfaz visual en Pygame para mostrar la ubicación, estado del sistema y coordenadas astronómicas en tiempo real.  
- Punto principal: clase `AstrotrackerGUI` (ver [`AstrotrackerGUI`](AppPC/astrotracker_programa.py)).  
- Cómo ejecutar: desde la carpeta raíz:
  ```sh
  python AppPC/astrotracker_programa.py
  ```

## AppMovil — Firmware Arduino
- Archivo: [AppMovil/Astrotracker 2.0.ino](AppMovil/Astrotracker 2.0.ino)  
- Qué hace: Controla los motores paso a paso mediante AccelStepper y recibe comandos por Bluetooth para mover, ajustar velocidad y reportar posición.  
- Funciones principales: [`setup`](AppMovil/Astrotracker 2.0.ino) y [`loop`](AppMovil/Astrotracker 2.0.ino).  
- Cómo usar: abrir en el IDE de Arduino, seleccionar placa y puerto, y subir al microcontrolador. El control se realiza vía comandos por Bluetooth.

---

Ubicación de los archivos:
- [AppPC/astrotracker_programa.py](AppPC/astrotracker_programa.py)  
- [AppMovil/Astrotracker 2.0.ino](AppMovil/Astrotracker 2.0.ino)