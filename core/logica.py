import math
import numpy as np
try:
    import requests
except ImportError:
    requests = None

_ROAD_CACHE = {}

# Estado de la última petición de matriz por carretera: 'ok', 'unavailable', 'partial' o None
LAST_ROAD_MATRIX_STATUS = None
def haversine_km(c1, c2):
    """Distancia euclidiana sobre esfera (Aérea)."""
    lat1, lon1 = c1
    lat2, lon2 = c2
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def _road_distance_osrm(c1, c2):
    """Intenta obtener distancia por carretera, si falla usa aérea."""
    if requests is None: return haversine_km(c1, c2)
    key = (c1, c2)
    if key in _ROAD_CACHE: return _ROAD_CACHE[key]

    try:
        # OSRM usa lon,lat
        url = f"http://router.project-osrm.org/route/v1/driving/{c1[1]},{c1[0]};{c2[1]},{c2[0]}?overview=false"
        resp = requests.get(url, timeout=1)
        if resp.status_code == 200:
            dist = resp.json()['routes'][0]['distance'] / 1000.0
            _ROAD_CACHE[key] = dist
            return dist
    except Exception:
        pass
    return haversine_km(c1, c2)


def _road_matrix_osrm(coords):
    """Intenta obtener la matriz de distancias por carretera usando el servicio 'table' de OSRM.
    Si falla, devuelve None para indicar que se debe usar fallback (haversine o N^2 requests).
    """
    global LAST_ROAD_MATRIX_STATUS
    if requests is None:
        LAST_ROAD_MATRIX_STATUS = 'unavailable'
        return None

    # Construir la cadena de coordenadas lon,lat;lon,lat;...
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'distances' in data and data['distances']:
                # distances are in meters; convert to km
                arr = data['distances']
                n = len(arr)
                mat = [[0.0]*n for _ in range(n)]
                for i in range(n):
                    for j in range(n):
                        d = arr[i][j]
                        mat[i][j] = 0.0 if d is None else (d / 1000.0)
                LAST_ROAD_MATRIX_STATUS = 'ok'
                return mat
    except Exception:
        pass
    LAST_ROAD_MATRIX_STATUS = 'unavailable'
    return None

def generar_matriz_distancias(coords, metric='aereo'):
    n = len(coords)
    matriz = np.zeros((n, n))
    if metric == 'carretera':
        # Intentar obtener toda la matriz de una sola vez (más eficiente)
        road_mat = _road_matrix_osrm(coords)
        if road_mat is not None:
            for i in range(n):
                for j in range(n):
                    matriz[i][j] = road_mat[i][j]
            return matriz

        # Si la petición de tabla no estuvo disponible, preferimos usar haversine
        # para evitar múltiples llamadas lentas a OSRM desde la red pública.
        if metric == 'carretera' and LAST_ROAD_MATRIX_STATUS == 'unavailable':
            metric = 'aereo'

        # Fallback: calcular por pares (aérea o carretera con llamada por par)
    for i in range(n):
        for j in range(n):
            if i == j:
                matriz[i][j] = 0
            else:
                if metric == 'carretera':
                    matriz[i][j] = _road_distance_osrm(coords[i], coords[j])
                else:
                    matriz[i][j] = haversine_km(coords[i], coords[j])
    return matriz


def generar_matriz_carretera_forzada(coords):
    """Fuerza el cálculo de la matriz usando llamadas por par a OSRM (más lento).
    Útil cuando la API de 'table' no está disponible pero quieres distancias por carretera.
    """
    n = len(coords)
    matriz = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                matriz[i][j] = 0
            else:
                matriz[i][j] = _road_distance_osrm(coords[i], coords[j])
    return matriz

def calcular_costo_ruta(ruta, matriz):
    costo = 0
    for i in range(len(ruta) - 1):
        costo += matriz[ruta[i]][ruta[i+1]]
    return costo