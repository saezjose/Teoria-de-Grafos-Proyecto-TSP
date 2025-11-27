import itertools
from .logica import calcular_costo_ruta

def generador_vecino_mas_cercano(n_ciudades, matriz):
    visitados = [False] * n_ciudades
    ruta = [0]
    visitados[0] = True
    nodo_actual = 0
    
    yield ruta, 0 

    for _ in range(n_ciudades - 1):
        mas_cercano = -1
        min_dist = float('inf')
        
        for v in range(n_ciudades):
            if not visitados[v] and matriz[nodo_actual][v] < min_dist:
                min_dist = matriz[nodo_actual][v]
                mas_cercano = v
        
        if mas_cercano != -1:
            nodo_actual = mas_cercano
            visitados[nodo_actual] = True
            ruta.append(nodo_actual)
            costo = calcular_costo_ruta(ruta, matriz)
            yield ruta, costo

    # Cerrar ciclo
    ruta.append(0)
    costo_final = calcular_costo_ruta(ruta, matriz)
    yield ruta, costo_final

def generador_fuerza_bruta(n_ciudades, matriz):
    indices = range(1, n_ciudades)
    mejor_ruta = None
    min_costo = float('inf')
    
    for perm in itertools.permutations(indices):
        ruta_actual = [0] + list(perm) + [0]
        costo_actual = calcular_costo_ruta(ruta_actual, matriz)
        
        yield ruta_actual, costo_actual
        # Solo enviamos actualización a la pantalla si encontramos un mejor camino
        # Esto hace que la animación se vea "inteligente" y no muestre millones de intentos malos
        if costo_actual < min_costo:
            min_costo = costo_actual
            mejor_ruta = list(ruta_actual)

    # Entrega final garantizada
    yield mejor_ruta, min_costo