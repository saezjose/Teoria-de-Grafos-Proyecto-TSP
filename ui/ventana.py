import customtkinter as ctk
import time
import threading
from data.ciudades import CIUDADES
from core.logica import generar_matriz_distancias
import core.logica as logica
from core.algoritmos import generador_vecino_mas_cercano, generador_fuerza_bruta
from ui.grafico import MapaGrafico

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppTSP(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TSP Solver - Evaluación 2")
        self.geometry("1000x650")
        
        self.is_closing = False
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.nombres = list(CIUDADES.keys())
        self.coords = list(CIUDADES.values())
        self.matriz = generar_matriz_distancias(self.coords, metric='aereo')
        self.n = len(self.nombres)
        self.res_optimo = None
        self.res_heuristica = None
        self.animation_after_id = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        ctk.CTkLabel(self.sidebar, text="Viajante TSP", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(20, 15), padx=20, sticky='w')
        
        # Control Métrica
        self.var_metric = ctk.StringVar(value="Aéreo")
        ctk.CTkSwitch(self.sidebar, text="Modo Carretera", variable=self.var_metric, 
                      onvalue="Carretera", offvalue="Aéreo", command=self.cambiar_metrica).grid(row=1, column=0, padx=20, pady=10, sticky='w')
        
        # (Botón "Forzar Carretera" eliminado a petición del usuario)

        # Botones de ejecución
        btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=8, sticky='ew')
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(btn_frame, text="▶ NN", command=self.run_nn, height=40).grid(row=0, column=0, padx=(0, 5), sticky='ew')
        ctk.CTkButton(btn_frame, text="✕ Limpiar", fg_color="#FF6B6B", hover_color="#FF5252", command=self.limpiar_nn, height=40).grid(row=0, column=1, padx=(5, 0), sticky='ew')
        
        btn_frame2 = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_frame2.grid(row=3, column=0, padx=20, pady=8, sticky='ew')
        btn_frame2.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(btn_frame2, text="▶ BF", fg_color="#D35B58", hover_color="#C74542", command=self.run_ex, height=40).grid(row=0, column=0, padx=(0, 5), sticky='ew')
        ctk.CTkButton(btn_frame2, text="✕ Limpiar", fg_color="#FF6B6B", hover_color="#FF5252", command=self.limpiar_bf, height=40).grid(row=0, column=1, padx=(5, 0), sticky='ew')

        # Panel Resultados
        self.frame_res = ctk.CTkFrame(self.sidebar, fg_color="#242424", corner_radius=10)
        self.frame_res.grid(row=4, column=0, padx=15, pady=15, sticky='nsew')
        self.frame_res.grid_rowconfigure(2, weight=1)
        
        # Estado y GAP
        self.lbl_status = ctk.CTkLabel(self.frame_res, text="Esperando...", font=("Arial", 13), text_color="#AAB8C2")
        self.lbl_status.grid(row=0, column=0, pady=10, padx=10, sticky='w')
        
        self.lbl_gap = ctk.CTkLabel(self.frame_res, text="GAP: -", font=ctk.CTkFont(size=18, weight="bold"), text_color="#4ADE80")
        self.lbl_gap.grid(row=1, column=0, pady=8, padx=10, sticky='w')

        # Log de distancias con fuente monoespaciada
        self.txt_log = ctk.CTkTextbox(self.frame_res, height=280, fg_color="#1a1a1a", text_color="#00D084", font=("Courier New", 10))
        self.txt_log.grid(row=2, column=0, padx=10, pady=(5, 10), sticky='nsew')
        
        # --- MAPA (ahora ocupa más espacio) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        self.mapa = MapaGrafico(self.main_frame, self.coords, self.nombres)

    def on_closing(self):
        """Maneja el cierre de la ventana de forma segura."""
        if self.is_closing:
            return
        self.is_closing = True
        if self.animation_after_id:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None
        
        # Limpiar el mapa de matplotlib
        if self.mapa:
            self.mapa.destroy()
            
        self.destroy()

    def cambiar_metrica(self):
        # Ejecutar recalculo en background para no congelar la UI
        m = 'carretera' if self.var_metric.get() == "Carretera" else 'aereo'
        self.lbl_status.configure(text=f"Recalculando matriz ({m})...", text_color="#FFA500")
        self.var_metric_widget_state = getattr(self, 'var_metric_widget_state', None)
        # Lanzar hilo
        thread = threading.Thread(target=self._recalc_matriz, args=(m,), daemon=True)
        thread.start()

    def _recalc_matriz(self, m):
        try:
            matriz = generar_matriz_distancias(self.coords, metric=m)
        except Exception as e:
            # En caso de error, programar mensaje en hilo principal
            def update_status():
                if self.is_closing: return
                self.lbl_status.configure(text=f"Error al calcular matriz: {e}", text_color="#FF6B6B")
            self.after(0, update_status)
            return

        # Imprimir en consola el estado de la petición y la matriz en formato legible
        try:
            status = getattr(logica, 'LAST_ROAD_MATRIX_STATUS', None)
            print(f"[INFO] metric={m} LAST_ROAD_MATRIX_STATUS={status}")
            # Formatear tabla con nombres como en main.py
            names = self.nombres
            colw = 12
            header = "".ljust(colw) + "".join(name.ljust(colw) for name in names)
            title = "[Matriz de Distancias D (km) - " + ("Carretera" if m=="carretera" else "Aérea") + "]"
            print("\n" + title)
            print(header)
            for i, row in enumerate(matriz):
                line = names[i].ljust(colw) + "".join(f"{v:>{colw}.2f}" for v in row)
                print(line)
            if m == 'carretera' and status == 'unavailable':
                print("\n[WARN] OSRM table API no disponible: se usaron distancias aéreas en su lugar.")
                print("Si quieres forzar cálculo por carretera mediante múltiples peticiones, dime 'forzar carretera' y lo ejecuto (puede tardar).")
        except Exception:
            pass

        # Actualizar UI en hilo principal
        def _apply():
            if self.is_closing:
                return
            self.matriz = matriz
            # Mostrar si la matriz carretera fue realmente calculada o si hubo fallback
            status = getattr(logica, 'LAST_ROAD_MATRIX_STATUS', None)
            if m == 'carretera':
                if status == 'ok':
                    self.lbl_status.configure(text=f"Matriz carretera lista", text_color="#4ADE80")
                elif status == 'unavailable':
                    self.lbl_status.configure(text=f"OSRM no disponible — usando métrica aérea", text_color="#FFA500")
                else:
                    self.lbl_status.configure(text=f"Matriz recalculada (carretera/mixta)", text_color="#4ADE80")
            else:
                self.lbl_status.configure(text=f"Matriz recalculada (aérea)", text_color="#4ADE80")
            self.res_optimo = None
            self.res_heuristica = None
            self.lbl_gap.configure(text="GAP: -")
            # Redibujar mapa para reflejar cambios si es necesario
            try:
                self.mapa.reset_plot()
            except Exception:
                pass

        self.after(0, _apply)

    def forzar_carretera(self):
        """Lanza un cálculo forzado de la matriz por carretera (llamadas por par)."""
        self.lbl_status.configure(text="Forzando cálculo carretera...", text_color="#FFA500")
        thread = threading.Thread(target=self._force_carretera_thread, daemon=True)
        thread.start()

    def _force_carretera_thread(self):
        try:
            matriz = logica.generar_matriz_carretera_forzada(self.coords)
        except Exception as e:
            def update_status():
                if self.is_closing: return
                self.lbl_status.configure(text=f"Error forzando carretera: {e}", text_color="#FF6B6B")
            self.after(0, update_status)
            return

        # imprimir y aplicar en UI
        def _apply_force():
            if self.is_closing:
                return
            self.matriz = matriz
            self.lbl_status.configure(text="Matriz carretera (forzada) lista", text_color="#4ADE80")
            self.res_optimo = None
            self.res_heuristica = None
            self.lbl_gap.configure(text="GAP: -")
            try:
                self.mapa.reset_plot()
            except Exception:
                pass
            # Imprimir tabla en consola
            names = self.nombres
            colw = 12
            header = "".ljust(colw) + "".join(name.ljust(colw) for name in names)
            title = "[Matriz de Distancias D (km) - Carretera (forzada)]"
            print("\n" + title)
            print(header)
            for i, row in enumerate(matriz):
                line = names[i].ljust(colw) + "".join(f"{v:>{colw}.2f}" for v in row)
                print(line)

        self.after(0, _apply_force)

    def limpiar_nn(self):
        """Limpiar datos del algoritmo NN"""
        self.res_heuristica = None
        self.lbl_status.configure(text="NN Limpio", text_color="#FFA500")
        self.mapa.reset_plot()
        self.txt_log.configure(state="normal")
        self.txt_log.delete("0.0", "end")
        self.txt_log.insert("0.0", "Datos NN borrados")
        self.txt_log.configure(state="disabled")
        if not self.res_optimo:
            self.lbl_gap.configure(text="GAP: -")

    def limpiar_bf(self):
        """Limpiar datos del algoritmo BF"""
        self.res_optimo = None
        self.lbl_status.configure(text="BF Limpio", text_color="#FFA500")
        self.mapa.reset_plot()
        self.txt_log.configure(state="normal")
        self.txt_log.delete("0.0", "end")
        self.txt_log.insert("0.0", "Datos BF borrados")
        self.txt_log.configure(state="disabled")
        if not self.res_heuristica:
            self.lbl_gap.configure(text="GAP: -")

    def run_nn(self):
        self.start_algo(generador_vecino_mas_cercano(self.n, self.matriz), "NN", "#3B8ED0")

    def run_ex(self):
        self.start_algo(generador_fuerza_bruta(self.n, self.matriz), "EX", "#D35B58")

    def start_algo(self, generador, tipo, color):
        if self.animation_after_id:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None

        self.gen = generador
        self.tipo_actual = tipo
        self.color_actual = color
        self.start_time = time.time()
        self.lbl_status.configure(text=f"Ejecutando {tipo}...", text_color=color)
        self.txt_log.configure(state="normal")
        self.txt_log.delete("0.0", "end")
        self.txt_log.configure(state="disabled")
        self.animar()

    def animar(self):
        if self.is_closing:
            return
        try:
            ruta, costo = next(self.gen)
            self.mapa.dibujar_ruta(ruta, self.color_actual)
            
            # Log bonito con detalles por tramo
            log_lines = [f"Costo total: {costo:>8.2f} km", "─" * 30]
            for i in range(len(ruta) - 1):
                u, v = ruta[i], ruta[i+1]
                dist = self.matriz[u][v]
                log_lines.append(f"{self.nombres[u]:11} → {self.nombres[v]:11} : {dist:7.2f} km")
            
            self.txt_log.configure(state="normal")
            self.txt_log.delete("0.0", "end")
            self.txt_log.insert("0.0", "\n".join(log_lines))
            self.txt_log.configure(state="disabled")
            self.lbl_status.configure(text=f"Iterando: {costo:.2f} km")

            self.animation_after_id = self.after(50, self.animar) 
        except StopIteration:
            self.animation_after_id = None
            dt = time.time() - self.start_time
            # Obtener costo final desde el log (primera línea)
            log_text = self.txt_log.get("0.0", "end")
            try:
                costo_final = float(log_text.split(":")[1].split("km")[0].strip())
            except Exception:
                costo_final = 0
            
            if self.tipo_actual == "NN": self.res_heuristica = costo_final
            else: self.res_optimo = costo_final
            
            self.lbl_status.configure(text=f"✓ {self.tipo_actual} Fin: {dt:.3f}s", text_color="#4ADE80")
            
            if self.res_optimo and self.res_heuristica:
                gap = ((self.res_heuristica - self.res_optimo) / self.res_optimo) * 100
                self.lbl_gap.configure(text=f"GAP: {gap:.2f}%", text_color="#FFD700" if gap > 10 else "#4ADE80")