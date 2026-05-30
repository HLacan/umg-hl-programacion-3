from estructuras.nodo import Nodo

class Lista:
    def __init__(self):
        self.cabeza = None
        self._tamano = 0

    def agregar(self, dato):
        nuevo = Nodo(dato)
        if self.cabeza is None:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self._tamano += 1

    def agregar_inicio(self, dato):
        nuevo = Nodo(dato)
        nuevo.siguiente = self.cabeza
        self.cabeza = nuevo
        self._tamano += 1

    def insertar_en(self, indice, dato):
        if indice <= 0:
            self.agregar_inicio(dato)
            return
        actual = self.cabeza
        for _ in range(indice - 1):
            if actual is None:
                return
            actual = actual.siguiente
        if actual is None:
            return
        nuevo = Nodo(dato)
        nuevo.siguiente = actual.siguiente
        actual.siguiente = nuevo
        self._tamano += 1

    def eliminar(self, dato):
        if self.cabeza is None:
            return
        if self.cabeza.dato == dato:
            self.cabeza = self.cabeza.siguiente
            self._tamano -= 1
            return
        actual = self.cabeza
        while actual.siguiente:
            if actual.siguiente.dato == dato:
                actual.siguiente = actual.siguiente.siguiente
                self._tamano -= 1
                return
            actual = actual.siguiente

    def eliminar_en(self, indice):
        if self.cabeza is None:
            return None
        if indice == 0:
            dato = self.cabeza.dato
            self.cabeza = self.cabeza.siguiente
            self._tamano -= 1
            return dato
        actual = self.cabeza
        for _ in range(indice - 1):
            if actual.siguiente is None:
                return None
            actual = actual.siguiente
        if actual.siguiente is None:
            return None
        dato = actual.siguiente.dato
        actual.siguiente = actual.siguiente.siguiente
        self._tamano -= 1
        return dato

    def obtener(self, indice):
        actual = self.cabeza
        for _ in range(indice):
            if actual is None:
                return None
            actual = actual.siguiente
        return actual.dato if actual else None

    def establecer(self, indice, dato):
        actual = self.cabeza
        for _ in range(indice):
            if actual is None:
                return
            actual = actual.siguiente
        if actual:
            actual.dato = dato

    def buscar(self, predicado):
        actual = self.cabeza
        while actual:
            if predicado(actual.dato):
                return actual.dato
            actual = actual.siguiente
        return None

    def vacia(self):
        return self._tamano == 0

    def limpiar(self):
        self.cabeza = None
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente

