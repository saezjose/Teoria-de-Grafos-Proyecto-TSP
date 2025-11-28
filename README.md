# 🚚 TSP Solver: Problema del Viajante en Chile

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Finalizado-success)

Aplicación gráfica interactiva para visualizar y resolver el **Problema del Viajante (TSP)** utilizando algoritmos exactos y heurísticos sobre un mapa real del sur de Chile. Proyecto desarrollado para la asignatura de **Teoría de Grafos**.

---

## 📋 Descripción

Este software permite comparar el desempeño de dos estrategias algorítmicas clásicas para encontrar la ruta más corta que visita un conjunto de 8 ciudades ($K_8$):

1.  **Fuerza Bruta (Búsqueda Exhaustiva):** Garantiza el óptimo global ($L^*$) evaluando todas las permutaciones posibles ($O(n!)$).
2.  **Vecino Más Cercano (Heurística Greedy):** Construye una solución rápida ($L^{NN}$) seleccionando siempre la ciudad más cercana ($O(n^2)$).

### Características Principales
* 🗺️ **Mapas Reales:** Visualización sobre OpenStreetMap usando `contextily`.
* 🚗 **Modo Carretera:** Cálculo de distancias reales mediante la API de OSRM (o fallback a distancia aérea Haversine).
* 🎬 **Animación en Tiempo Real:** Visualización paso a paso del proceso de búsqueda sin congelar la interfaz.
* 📊 **Comparativa:** Cálculo automático del *Gap de Optimalidad* y tiempos de ejecución.

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Interfaz Gráfica:** `customtkinter` (GUI moderna)
* **Visualización:** `matplotlib`, `contextily`
* **Cálculo:** `numpy`, `requests` (API), `itertools`

---


