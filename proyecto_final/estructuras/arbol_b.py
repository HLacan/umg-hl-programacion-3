from estructuras.lista import Lista

class NodoB:

    def __init__(self, es_hoja=True):
        self.claves  = Lista()
        self.valores = Lista()
        self.hijos   = Lista()
        self.es_hoja = es_hoja

    def num_claves(self):
        return len(self.claves)

    def pos_insercion(self, clave):
        idx = 0
        for c in self.claves:
            if clave < c:
                return idx
            idx += 1
        return idx

class ArbolB:

    def __init__(self, orden=4):
        self.orden = orden
        self.raiz  = NodoB(es_hoja=True)
        self._tamano = 0

    def buscar(self, clave):
        return self._buscar_rec(self.raiz, clave)

    def _buscar_rec(self, nodo, clave):
        for i in range(nodo.num_claves()):
            c = nodo.claves.obtener(i)
            if clave == c:
                return nodo.valores.obtener(i)
            if clave < c:
                if nodo.es_hoja:
                    return None
                return self._buscar_rec(nodo.hijos.obtener(i), clave)
        if nodo.es_hoja:
            return None
        return self._buscar_rec(nodo.hijos.obtener(nodo.num_claves()), clave)

    def _buscar_nodo(self, nodo, clave):
        for i in range(nodo.num_claves()):
            c = nodo.claves.obtener(i)
            if clave == c:
                return (nodo, i)
            if clave < c:
                if nodo.es_hoja:
                    return None
                return self._buscar_nodo(nodo.hijos.obtener(i), clave)
        if nodo.es_hoja:
            return None
        return self._buscar_nodo(nodo.hijos.obtener(nodo.num_claves()), clave)

    def insertar(self, clave, valor):
        encontrado = self._buscar_nodo(self.raiz, clave)
        if encontrado is not None:
            nodo, idx = encontrado
            nodo.valores.establecer(idx, valor)
            return

        resultado = self._insertar_rec(self.raiz, clave, valor)
        self._tamano += 1

        if resultado is not None:
            clave_media, valor_medio, hijo_der = resultado
            nueva_raiz = NodoB(es_hoja=False)
            nueva_raiz.claves.agregar(clave_media)
            nueva_raiz.valores.agregar(valor_medio)
            nueva_raiz.hijos.agregar(self.raiz)
            nueva_raiz.hijos.agregar(hijo_der)
            self.raiz = nueva_raiz

    def _insertar_rec(self, nodo, clave, valor):
        if nodo.es_hoja:
            pos = nodo.pos_insercion(clave)
            nodo.claves.insertar_en(pos, clave)
            nodo.valores.insertar_en(pos, valor)
        else:
            pos    = nodo.pos_insercion(clave)
            hijo   = nodo.hijos.obtener(pos)
            resultado = self._insertar_rec(hijo, clave, valor)

            if resultado is not None:
                clave_media, valor_medio, hijo_nuevo = resultado
                ins_pos = nodo.pos_insercion(clave_media)
                nodo.claves.insertar_en(ins_pos,     clave_media)
                nodo.valores.insertar_en(ins_pos,    valor_medio)
                nodo.hijos.insertar_en(ins_pos + 1,  hijo_nuevo)

        if nodo.num_claves() >= self.orden:
            return self._dividir(nodo)
        return None

    def _dividir(self, nodo):
        mitad = nodo.num_claves() // 2

        clave_media = nodo.claves.obtener(mitad)
        valor_medio = nodo.valores.obtener(mitad)

        nuevo = NodoB(es_hoja=nodo.es_hoja)
        num_total = nodo.num_claves()
        for _ in range(num_total - mitad - 1):
            nuevo.claves.agregar(nodo.claves.obtener(mitad + 1))
            nuevo.valores.agregar(nodo.valores.obtener(mitad + 1))
            nodo.claves.eliminar_en(mitad + 1)
            nodo.valores.eliminar_en(mitad + 1)

        nodo.claves.eliminar_en(mitad)
        nodo.valores.eliminar_en(mitad)

        if not nodo.es_hoja:
            num_hijos = len(nodo.hijos)
            for _ in range(num_hijos - mitad - 1):
                nuevo.hijos.agregar(nodo.hijos.obtener(mitad + 1))
                nodo.hijos.eliminar_en(mitad + 1)

        return (clave_media, valor_medio, nuevo)

    def recorrer(self):
        resultado = Lista()
        self._inorden(self.raiz, resultado)
        return resultado

    def todos(self):
        resultado = Lista()
        self._inorden_valores(self.raiz, resultado)
        return resultado

    def _inorden(self, nodo, resultado):
        if nodo.es_hoja:
            for i in range(nodo.num_claves()):
                resultado.agregar((nodo.claves.obtener(i), nodo.valores.obtener(i)))
        else:
            for i in range(nodo.num_claves()):
                self._inorden(nodo.hijos.obtener(i), resultado)
                resultado.agregar((nodo.claves.obtener(i), nodo.valores.obtener(i)))
            self._inorden(nodo.hijos.obtener(nodo.num_claves()), resultado)

    def _inorden_valores(self, nodo, resultado):
        if nodo.es_hoja:
            for i in range(nodo.num_claves()):
                resultado.agregar(nodo.valores.obtener(i))
        else:
            for i in range(nodo.num_claves()):
                self._inorden_valores(nodo.hijos.obtener(i), resultado)
                resultado.agregar(nodo.valores.obtener(i))
            self._inorden_valores(nodo.hijos.obtener(nodo.num_claves()), resultado)

    def tamano(self):
        return self._tamano

    def vacio(self):
        return self._tamano == 0

    def limpiar(self):
        self.raiz    = NodoB(es_hoja=True)
        self._tamano = 0

    def estructura(self):
        nodos = []
        cola  = Lista()
        cola.agregar(self.raiz)
        while not cola.vacia():
            nodo   = cola.eliminar_en(0)
            claves = [c for c in nodo.claves]
            if nodo.es_hoja:
                nodos.append({
                    'id':      id(nodo),
                    'es_hoja': True,
                    'claves':  claves,
                    'hijos':   [],
                })
            else:
                hijos_ids = []
                for hijo in nodo.hijos:
                    hijos_ids.append(id(hijo))
                    cola.agregar(hijo)
                nodos.append({
                    'id':      id(nodo),
                    'es_hoja': False,
                    'claves':  claves,
                    'hijos':   hijos_ids,
                })
        return nodos

