import random

from estructuras.arbol_b import ArbolB
from estructuras.lista import Lista
from estructuras.pila import Pila
from juego.jugada import Jugada
from juego.tablero import Tablero
from juego.logica import ganador, empate

class Cerebro:

    AJUSTE_GANAR  =  1.0
    AJUSTE_EMPATE =  0.3
    AJUSTE_PERDER = -0.8

    PESO_MINIMO = 0.05

    GAMMA = 0.9

    def __init__(self, simbolo, orden=4):
        self.simbolo = simbolo
        self._memoria = ArbolB(orden=orden)
        self._jugadas_partida = Pila()

    def elegir(self, tablero, exploracion=0.0):
        clave = tablero.clave()
        jugadas = self._memoria.buscar(clave)

        if jugadas is None:
            jugadas = Lista()
            for (fila, col) in tablero.movimientos():
                jugadas.agregar(Jugada(fila, col, peso=1.0))
            self._memoria.insertar(clave, jugadas)

        if len(jugadas) == 0:
            return None

        if exploracion > 0 and random.random() < exploracion:
            indice_aleatorio = random.randint(0, len(jugadas) - 1)
            jugada_elegida = jugadas.obtener(indice_aleatorio)

        else:
            mejor_peso = -1
            mejores_jugadas = Lista()

            for jugada in jugadas:
                if jugada.peso > mejor_peso:
                    mejor_peso = jugada.peso
                    mejores_jugadas.limpiar()
                    mejores_jugadas.agregar(jugada)
                elif jugada.peso == mejor_peso:
                    mejores_jugadas.agregar(jugada)

            indice = random.randint(0, len(mejores_jugadas) - 1)
            jugada_elegida = mejores_jugadas.obtener(indice)

        self._jugadas_partida.apilar((clave, jugada_elegida))
        return jugada_elegida

    def reforzar(self, resultado):
        if resultado == 'gano':
            ajuste_base = self.AJUSTE_GANAR
        elif resultado == 'empato':
            ajuste_base = self.AJUSTE_EMPATE
        else:
            ajuste_base = self.AJUSTE_PERDER

        descuento = 1.0
        while not self._jugadas_partida.vacia():
            clave, jugada_hecha = self._jugadas_partida.desapilar()
            jugadas = self._memoria.buscar(clave)

            if jugadas is not None:
                for jugada in jugadas:
                    if jugada.fila == jugada_hecha.fila and jugada.columna == jugada_hecha.columna:
                        ajuste = ajuste_base * descuento
                        jugada.peso = max(self.PESO_MINIMO, jugada.peso + ajuste)
                        break

            descuento *= self.GAMMA

    def estados(self):
        return self._memoria.tamano()

def poblar_todos_estados(cerebro_x, cerebro_o):
    def explorar(tablero, turno):
        if ganador(tablero) or empate(tablero):
            return

        cerebro = cerebro_x if turno == 'X' else cerebro_o
        clave = tablero.clave()

        if cerebro._memoria.buscar(clave) is not None:
            return

        jugadas = Lista()
        for (fila, col) in tablero.movimientos():
            jugadas.agregar(Jugada(fila, col, peso=1.0))
        cerebro._memoria.insertar(clave, jugadas)

        for (fila, col) in tablero.movimientos():
            tablero.colocar(fila, col, turno)
            siguiente_turno = 'O' if turno == 'X' else 'X'
            explorar(tablero, siguiente_turno)
            tablero.deshacer(fila, col)

    tablero_inicial = Tablero()
    explorar(tablero_inicial, 'X')

