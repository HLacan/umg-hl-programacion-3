from estructuras.arbol_b import ArbolB
from historial.registro import Registro

class Historial:
    def __init__(self, orden=4):
        self._arbol = ArbolB(orden=orden)
        self._total = 0

    def agregar(self, ganador, jugadas):
        reg = Registro(ganador, jugadas)
        self._arbol.insertar(reg.id, reg)
        self._total += 1
        return reg

    def obtener(self, id_partida):
        return self._arbol.buscar(id_partida)

    def todos(self):
        return self._arbol.todos()

    def total(self):
        return self._total

    def vacio(self):
        return self._total == 0

    def estadisticas(self):
        x = 0
        o = 0
        empates = 0
        total_jugadas = 0
        for reg in self.todos():
            if reg.ganador == 'X':
                x += 1
            elif reg.ganador == 'O':
                o += 1
            else:
                empates += 1
            total_jugadas += reg.total_jugadas()
        total = x + o + empates
        promedio = round(total_jugadas / total, 1) if total > 0 else 0
        return {'X': x, 'O': o, 'empate': empates, 'total': total, 'promedio': promedio}

    def iteraciones_para_ganar(self, simbolo='O'):
        contador = 0
        for reg in self.todos():
            contador += 1
            if reg.ganador == simbolo:
                return contador
        return None

    def limpiar(self):
        self._arbol.limpiar()
        self._total = 0
        Registro._siguiente_id = 1

