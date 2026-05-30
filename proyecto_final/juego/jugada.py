class Jugada:
    def __init__(self, fila, columna, peso=1.0):
        self.fila = fila
        self.columna = columna
        self.peso = peso

    def posicion(self):
        return (self.fila, self.columna)

