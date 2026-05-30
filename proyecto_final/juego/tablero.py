from estructuras.lista import Lista

class Tablero:
    def __init__(self):
        self._celdas = Lista()
        for _ in range(9):
            self._celdas.agregar(' ')

    def colocar(self, fila, col, simbolo):
        idx = fila * 3 + col
        if self._celdas.obtener(idx) != ' ':
            return False
        self._celdas.establecer(idx, simbolo)
        return True

    def deshacer(self, fila, col):
        self._celdas.establecer(fila * 3 + col, ' ')

    def obtener(self, fila, col):
        return self._celdas.obtener(fila * 3 + col)

    def movimientos(self):
        resultado = Lista()
        for f in range(3):
            for c in range(3):
                if self._celdas.obtener(f * 3 + c) == ' ':
                    resultado.agregar((f, c))
        return resultado

    def lleno(self):
        for i in range(9):
            if self._celdas.obtener(i) == ' ':
                return False
        return True

    def clave(self):
        texto = ''
        for i in range(9):
            texto += self._celdas.obtener(i)
        return texto

    def copiar(self):
        nuevo = Tablero()
        for i in range(9):
            nuevo._celdas.establecer(i, self._celdas.obtener(i))
        return nuevo

    def reiniciar(self):
        for i in range(9):
            self._celdas.establecer(i, ' ')

