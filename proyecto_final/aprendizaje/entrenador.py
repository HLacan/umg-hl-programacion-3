from juego.tablero import Tablero
from juego.logica import ganador, empate, terminada
from estructuras.lista import Lista

class Entrenador:

    def entrenar(self, cerebro_x, cerebro_o, n, historial=None):
        victorias_x = 0
        victorias_o = 0
        empates = 0
        partidas_registradas = Lista()

        for _ in range(n):
            tablero = Tablero()
            turno = 'X'
            jugadas = Lista()

            while not terminada(tablero):
                cerebro = cerebro_x if turno == 'X' else cerebro_o

                jugada = cerebro.elegir(tablero, exploracion=0.3)

                if jugada:
                    tablero.colocar(jugada.fila, jugada.columna, turno)
                    jugadas.agregar((jugada.fila, jugada.columna, turno))

                turno = 'O' if turno == 'X' else 'X'

            resultado = ganador(tablero)

            if resultado == 'X':
                cerebro_x.reforzar('gano')
                cerebro_o.reforzar('perdio')
                victorias_x += 1
            elif resultado == 'O':
                cerebro_x.reforzar('perdio')
                cerebro_o.reforzar('gano')
                victorias_o += 1
            else:
                cerebro_x.reforzar('empato')
                cerebro_o.reforzar('empato')
                empates += 1

            if historial is not None:
                registro = historial.agregar(resultado, jugadas)
                partidas_registradas.agregar(registro)

        return {
            'X':       victorias_x,
            'O':       victorias_o,
            'empate':  empates,
            'total':   n,
            'partidas': partidas_registradas,
        }

