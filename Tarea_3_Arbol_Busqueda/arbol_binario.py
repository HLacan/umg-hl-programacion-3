from graphviz import Digraph
import csv

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None

class ArbolBinario:
    def __init__(self):
       self.raiz = None

    def insertar(self, valor):
        nuevo_nodo = Nodo(valor)

        if(self.raiz == None):
            self.raiz = nuevo_nodo
        else:
            self._insertar(self.raiz, nuevo_nodo)
            
    def _insertar(self, actual, nodo):
        if(nodo.valor < actual.valor):
            if(actual.izquierda is None):
                actual.izquierda = nodo
                return
            else:
                return self._insertar(actual.izquierda, nodo)
        elif(nodo.valor > actual.valor):
            if(actual.derecha is None):
                actual.derecha = nodo
                return
            else:
                return self._insertar(actual.derecha, nodo)

    def buscarValor(self, valor):
        return self._buscarValor(self.raiz, valor)
    
    def _buscarValor(self, actual, valor):
        if actual is None:
            return False
        
        if (valor == actual.valor):
            return True
        
        if(valor < actual.valor):
            return self._buscarValor(actual.izquierda, valor)
        else:
            return self._buscarValor(actual.derecha, valor)
        
    def eliminar(self, valor):
        self.raiz = self._eliminar(self.raiz, valor)

    def _eliminar(self, actual, valor):
        if actual is None:
            return None

        if valor < actual.valor:
            actual.izquierda = self._eliminar(actual.izquierda, valor)
        elif valor > actual.valor:
            actual.derecha = self._eliminar(actual.derecha, valor)
        else:
            if actual.izquierda is None and actual.derecha is None:
                return None
            if actual.izquierda is None:
                return actual.derecha
            if actual.derecha is None:
                return actual.izquierda
            menor_mayor = self.buscarMenor(actual.derecha)
            actual.valor = menor_mayor.valor
            actual.derecha = self._eliminar(actual.derecha, menor_mayor.valor)
        return actual

    def buscarMenor(self, actual):
        while actual.izquierda is not None:
            actual = actual.izquierda
        return actual

    def generar_grafico(self, nombre_archivo="arbol_binario"):
        dot = Digraph(format="png")
        dot.attr(rankdir="TB")

        def agregar_nodos_aristas(nodo):
            if nodo is None:
                return
            # Nodo con etiqueta igual al valor
            dot.node(str(id(nodo)), label=str(nodo.valor), shape="circle", style="filled", fillcolor="#AED6F1")
            # Hijo izquierdo
            if nodo.izquierda:
                dot.edge(str(id(nodo)), str(id(nodo.izquierda)), label="Izq", color="#58D68D")
                agregar_nodos_aristas(nodo.izquierda)
            # Hijo derecho
            if nodo.derecha:
                dot.edge(str(id(nodo)), str(id(nodo.derecha)), label="Der", color="#F5B041")
                agregar_nodos_aristas(nodo.derecha)

        agregar_nodos_aristas(self.raiz)
        dot.render(nombre_archivo, view=False)
        print(f"Imagen generada: {nombre_archivo}.png")

def cargar_desde_csv(arbol, nombre_archivo):
    with open(nombre_archivo, newline='', encoding='utf-8') as csvfile:
        lector = csv.reader(csvfile)
        for fila in lector:
            for celda in fila:
                if celda.strip():
                    try:
                        valor = int(celda.strip())
                        arbol.insertar(valor)
                    except ValueError:
                        print(f"Valor no válido en el CSV: {celda}")
    print("Valores del CSV insertados en el árbol.")
    arbol.generar_grafico()

def menu():
    arbol = ArbolBinario()
    while True:
        print("\nMenú:")
        print("1. Insertar valor")
        print("2. Buscar valor")
        print("3. Eliminar valor")
        print("4. Cargar valores desde CSV")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            valor = int(input("Ingrese el valor a insertar: "))
            arbol.insertar(valor)
            print(f"Valor {valor} insertado.")
            arbol.generar_grafico()
        elif opcion == "2":
            valor = int(input("Ingrese el valor a buscar: "))
            encontrado = arbol.buscarValor(valor)
            if encontrado:
                print(f"Valor {valor} encontrado en el árbol.")
            else:
                print(f"Valor {valor} no encontrado en el árbol.")
            arbol.generar_grafico()
        elif opcion == "3":
            valor = int(input("Ingrese el valor a eliminar: "))
            arbol.eliminar(valor)
            print(f"Valor {valor} eliminado (si existía).")
            arbol.generar_grafico()
        elif opcion == "4":
            cargar_desde_csv(arbol, "lista.csv")
        elif opcion == "5":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción del menú.")
   
menu()


