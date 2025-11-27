import math
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

try:
    import contextily as ctx
    _HAS_CTX = True
except Exception:
    ctx = None
    _HAS_CTX = False

def ll2mercator(lat, lon):
    """Convierte Lat/Lon (WGS84) a Web Mercator (metros)."""
    x = lon * 20037508.34 / 180.0
    y = math.log(math.tan((90.0 + lat) * math.pi / 360.0))
    y = y * 20037508.34 / math.pi
    return x, y

class MapaGrafico:
    def __init__(self, parent, coords, nombres):
        self.parent = parent
        self.coords = coords
        self.nombres = nombres
        
        # Conversión de coordenadas
        self.mercator_coords = [ll2mercator(lat, lon) for lat, lon in self.coords]
        self.xs = [c[0] for c in self.mercator_coords]
        self.ys = [c[1] for c in self.mercator_coords]

        # Configuración de la Figura
        # dpi=100 asegura textos nítidos
        self.fig, self.ax = plt.subplots(figsize=(6.5, 5.0), dpi=100)
        
        # Quitamos márgenes blancos de la figura
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        # Fondo gris oscuro para que se funda con la ventana de la App
        self.fig.patch.set_facecolor('#2b2b2b')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Dibujar estado inicial
        self.reset_plot()

    def reset_plot(self):
        self.ax.clear()
        
        # 1. CALCULO DE ZOOM "ARMONIOSO" (Más alejado)
        if len(self.xs) > 0:
            xmin, xmax = min(self.xs), max(self.xs)
            ymin, ymax = min(self.ys), max(self.ys)
            
            dx = xmax - xmin if xmax > xmin else 5000.0
            dy = ymax - ymin if ymax > ymin else 5000.0
            
            # Usamos la dimensión mayor para mantener la proporción cuadrada
            max_dim = max(dx, dy)
            
            # PADDING 60%: Esto aleja el mapa para que se vea "armónico" y no apretado
            pad = max_dim * 0.60 
            
            self.ax.set_xlim(xmin - pad, xmax + pad)
            self.ax.set_ylim(ymin - pad, ymax + pad)
        
        # 2. MAPA BASE VIBRANTE (Estilo Clásico Claro)
        # Usamos OpenStreetMap.Mapnik para colores vivos (azul agua, verde bosque)
        # Sin filtros de tinte encima para máxima claridad.
        if _HAS_CTX:
            try:
                ctx.add_basemap(self.ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom_adjust=0)
            except Exception:
                # Fallback si falla la descarga
                self.ax.set_facecolor('#f2f2f2')
                self.ax.grid(True, color='#e0e0e0', linestyle='--')
        else:
            self.ax.set_facecolor('#f2f2f2')

        # 3. MARCADORES ESTILO "PIN" (Naranja/Rojo Vibrante)
        self.ax.scatter(self.xs, self.ys, 
                        c='#FF5722',    # Naranja rojizo intenso
                        s=180,          # Tamaño grande
                        zorder=20, 
                        edgecolors='white', # Borde blanco limpio
                        linewidth=2.5,      # Borde grueso
                        marker='o')

        # 4. ETIQUETAS ELEGANTES (Encima del punto)
        for i, name in enumerate(self.nombres):
            x, y = self.xs[i], self.ys[i]
            
            # Etiqueta flotando arriba del punto
            ann = self.ax.annotate(name, (x, y), 
                                   xytext=(0, 12), textcoords='offset points', 
                                   color='white', fontsize=9, fontweight='bold', fontfamily='sans-serif',
                                   # Caja gris oscura redondeada
                                   bbox=dict(boxstyle='round,pad=0.4', fc='#263238', ec='none', alpha=0.85),
                                   ha='center', va='bottom', zorder=21)

        self.ax.axis('off')
        self.canvas.draw()

    def dibujar_ruta(self, ruta_indices, color_linea='#E91E63'):
        """Dibuja la ruta. Color Rosa Fuerte (#E91E63) para contraste alto."""
        if not ruta_indices:
            return

        # Redibujamos base limpia
        self.reset_plot()
        
        rx = [self.mercator_coords[i][0] for i in ruta_indices]
        ry = [self.mercator_coords[i][1] for i in ruta_indices]
        
        # Sombra suave debajo de la ruta (Efecto profundidad)
        self.ax.plot(rx, ry, '-', color='black', linewidth=4.0, alpha=0.2, zorder=14)
        
        # Línea principal
        self.ax.plot(rx, ry, '-', color=color_linea, linewidth=2.5, alpha=0.9, zorder=15)
        
        self.canvas.draw()