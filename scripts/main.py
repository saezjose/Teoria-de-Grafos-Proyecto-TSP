from ui.ventana import AppTSP
from data.ciudades import CIUDADES
from core.logica import generar_matriz_distancias

def imprimir_matriz_para_informe():
    print("\n" + "="*60)
    print("--- DATOS PARA TU INFORME (COPIAR Y PEGAR) ---")
    print("="*60)
    
    nombres = list(CIUDADES.keys())
    coords = list(CIUDADES.values())
    matriz = generar_matriz_distancias(coords, metric='aereo')
    
    # 1. Imprimir Coordenadas
    print("\n[Tabla de Coordenadas]")
    print(f"{'Ciudad':<15} | {'Latitud':<10} | {'Longitud':<10}")
    print("-" * 45)
    for ciudad, coord in CIUDADES.items():
        print(f"{ciudad:<15} | {coord[0]:<10.4f} | {coord[1]:<10.4f}")

    # 2. Imprimir Matriz
    print("\n[Matriz de Distancias D (km) - Distancia Euclidiana/Aérea]")
    # Cabecera
    print(" " * 12, end="")
    for nombre in nombres:
        print(f"{nombre[:10]:<12}", end="")
    print()
    
    # Filas
    for i, fila in enumerate(nombres):
        print(f"{fila[:10]:<12}", end="")
        for val in matriz[i]:
            print(f"{val:<12.2f}", end="")
        print()
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    # 1. Imprimir datos útiles
    imprimir_matriz_para_informe()
    
    # 2. Iniciar App
    app = AppTSP()
    app.mainloop()