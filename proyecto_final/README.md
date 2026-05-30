# Totito

## Integrantes

Luis Emilio Sipac Maldonado 9490-24-5565 100%
Herbert Rafael Lacan Hernandez 9490-24-21332 100% 

## Descripción

Juego de Totito con inteligencia artificial que aprende a jugar mejor con cada partida

## Requisitos

- Python 3.8 o superior
- Graphviz instalado en el sistema (para las visualizaciones)
- Librería `graphviz` de Python

### Instalar dependencias

pip install graphviz
Instalar Graphviz en Windows: https://graphviz.org/download/

## Cómo ejecutar

Desde la carpeta `proyecto_final/`:
python main.py

## Funcionalidades

- **Jugar vs IA**: el humano juega con X contra la IA con O
- **IA vs IA**: dos cerebros juegan entre sí automáticamente
- **Historial**: muestra todas las partidas jugadas con su ID y tablero final
- **Entrenar**: simula N partidas para que la IA aprenda rápido
- **Limpiar**: reinicia el aprendizaje y el historial desde cero
- **Visualización**: cada partida genera un grafo con Graphviz mostrando los pesos de las jugadas
