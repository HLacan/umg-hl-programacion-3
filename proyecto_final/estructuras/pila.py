from estructuras.lista import Lista

class Pila:
    def __init__(self):
        self._lista = Lista()

    def apilar(self, dato):
        self._lista.agregar_inicio(dato)

    def desapilar(self):
        return self._lista.eliminar_en(0)

    def tope(self):
        return self._lista.obtener(0)

    def vacia(self):
        return self._lista.vacia()

    def limpiar(self):
        self._lista.limpiar()

    def __len__(self):
        return len(self._lista)

