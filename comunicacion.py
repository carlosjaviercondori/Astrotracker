"""
App PC muy simple para controlar la CNC Shield V3 por USB/Serie.
- Lista puertos COM disponibles
- Conectar/Desconectar
- Botones de jog: X+/X-, Y+/Y-, Z+/Z-
- Ajuste de tamaño de paso, velocidad y aceleración
- Habilitar/Deshabilitar motores

Hecha con Tkinter (incluido en Python) y pyserial.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
from serial.tools import list_ports

# Velocidad de comunicación. Debe coincidir con el Serial.begin del Arduino
BAUD = 115200

class CNCApp:
    def __init__(self, root):
        self.root = root
        root.title("CNC Shield V3 - Control simple")
        root.geometry("430x360")
        root.resizable(False, False)

        self.ser = None  # acá guardamos el objeto serial cuando conectamos

        # --- Frame de conexión ---
        frm_conn = ttk.LabelFrame(root, text="Conexión")
        frm_conn.pack(fill="x", padx=10, pady=8)

        ttk.Label(frm_conn, text="Puerto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.cmb_port = ttk.Combobox(frm_conn, values=self.listar_puertos(), state="readonly", width=18)
        self.cmb_port.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(frm_conn, text="Actualizar", command=self.refrescar_puertos).grid(row=0, column=2, padx=5, pady=5)
        self.btn_con = ttk.Button(frm_conn, text="Conectar", command=self.conectar)
        self.btn_con.grid(row=0, column=3, padx=5, pady=5)
        self.btn_des = ttk.Button(frm_conn, text="Desconectar", state="disabled", command=self.desconectar)
        self.btn_des.grid(row=0, column=4, padx=5, pady=5)

        # --- Frame de parámetros ---
        frm_params = ttk.LabelFrame(root, text="Parámetros")
        frm_params.pack(fill="x", padx=10, pady=8)

        ttk.Label(frm_params, text="Paso (steps por clic):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.var_paso = tk.StringVar(value="200")  # 200 ~ 1 vuelta si tu motor es 200 pasos y microstepping 1:1
        ttk.Entry(frm_params, textvariable=self.var_paso, width=10).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frm_params, text="Vel máx (steps/s):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.var_vel = tk.StringVar(value="1000")
        ttk.Entry(frm_params, textvariable=self.var_vel, width=10).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frm_params, text="Aceleración (steps/s²):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.var_acel = tk.StringVar(value="400")
        ttk.Entry(frm_params, textvariable=self.var_acel, width=10).grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(frm_params, text="Aplicar vel/accel", command=self.enviar_parametros).grid(row=0, column=6, padx=8, pady=5)

        # --- Frame de jog ---
        frm_jog = ttk.LabelFrame(root, text="Jog (movimiento relativo)")
        frm_jog.pack(fill="both", expand=True, padx=10, pady=8)

        # Botones dispuestos en cruz para X/Y y a la derecha Z+/Z-
        self.btn_up    = ttk.Button(frm_jog, text="↑ Y+", command=lambda: self.mover(0, +1, 0))
        self.btn_left  = ttk.Button(frm_jog, text="← X-", command=lambda: self.mover(-1, 0, 0))
        self.btn_right = ttk.Button(frm_jog, text="→ X+", command=lambda: self.mover(+1, 0, 0))
        self.btn_down  = ttk.Button(frm_jog, text="↓ Y-", command=lambda: self.mover(0, -1, 0))

        self.btn_up.grid(   row=0, column=1, padx=5, pady=5)
        self.btn_left.grid( row=1, column=0, padx=5, pady=5)
        self.btn_right.grid(row=1, column=2, padx=5, pady=5)
        self.btn_down.grid( row=2, column=1, padx=5, pady=5)

        self.btn_zp = ttk.Button(frm_jog, text="Z+", command=lambda: self.mover(0, 0, +1))
        self.btn_zn = ttk.Button(frm_jog, text="Z-", command=lambda: self.mover(0, 0, -1))
        self.btn_zp.grid(row=0, column=4, padx=15, pady=5)
        self.btn_zn.grid(row=2, column=4, padx=15, pady=5)

        # --- Frame habilitar/deshabilitar ---
        frm_en = ttk.LabelFrame(root, text="Motores")
        frm_en.pack(fill="x", padx=10, pady=8)
        ttk.Button(frm_en, text="Habilitar (EN)", command=lambda: self.enviar_linea("EN")).pack(side="left", padx=6, pady=6)
        ttk.Button(frm_en, text="Deshabilitar (DI)", command=lambda: self.enviar_linea("DI")).pack(side="left", padx=6, pady=6)

        # Texto para mostrar respuestas del Arduino
        self.txt_log = tk.Text(root, height=6, state="disabled")
        self.txt_log.pack(fill="both", padx=10, pady=8)

        # Deshabilitar controles hasta conectar
        self.habilitar_controles(False)

    def listar_puertos(self):
        # Devuelve lista de nombres de puerto (COM3, /dev/ttyUSB0, etc.)
        return [p.device for p in list_ports.comports()]

    def refrescar_puertos(self):
        self.cmb_port["values"] = self.listar_puertos()

    def conectar(self):
        puerto = self.cmb_port.get()
        if not puerto:
            messagebox.showwarning("Atención", "Elegí un puerto primero.")
            return
        try:
            self.ser = serial.Serial(puerto, BAUD, timeout=1)
            self.habilitar_controles(True)
            self.btn_con.config(state="disabled")
            self.btn_des.config(state="normal")
            self.log(f"Conectado a {puerto} @ {BAUD} baud")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el puerto:\n{e}")

    def desconectar(self):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.habilitar_controles(False)
            self.btn_con.config(state="normal")
            self.btn_des.config(state="disabled")
            self.log("Desconectado")
        except Exception as e:
            messagebox.showerror("Error", f"Al cerrar el puerto:\n{e}")

    def habilitar_controles(self, estado):
        # Habilita botones y entradas que tienen sentido solo conectados
        for w in [self.btn_up, self.btn_left, self.btn_right, self.btn_down,
                  self.btn_zp, self.btn_zn]:
            w.config(state="normal" if estado else "disabled")

    def enviar_parametros(self):
        # Envía "S vel acel" al Arduino
        try:
            v = int(self.var_vel.get())
            a = int(self.var_acel.get())
            if v <= 0 or a <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Parámetros", "Velocidad y aceleración deben ser enteros positivos.")
            return
        self.enviar_linea(f"S {v} {a}")

    def mover(self, sx, sy, sz):
        # Toma el tamaño de paso (entero), arma comando M y lo envía
        try:
            paso = int(self.var_paso.get())
            if paso <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Parámetros", "El tamaño de paso debe ser un entero positivo.")
            return
        dx = sx * paso
        dy = sy * paso
        dz = sz * paso
        partes = []
        if dx != 0: partes.append(f"X{dx}")
        if dy != 0: partes.append(f"Y{dy}")
        if dz != 0: partes.append(f"Z{dz}")
        if not partes:
            return
        self.enviar_linea("M " + " ".join(partes))

    def enviar_linea(self, linea):
        # Manda una línea terminada en \n y lee respuesta
        if not self.ser or not self.ser.is_open:
            messagebox.showwarning("Conexión", "No hay puerto abierto.")
            return
        try:
            self.ser.write((linea + "\n").encode("ascii"))
            self.log(f">>> {linea}")
            resp = self.ser.readline().decode(errors="ignore").strip()
            if resp:
                self.log(f"<<< {resp}")
        except Exception as e:
            messagebox.showerror("Error", f"Envío/recepción falló:\n{e}")

    def log(self, texto):
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", texto + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = CNCApp(root)
    root.mainloop()
