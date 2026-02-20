from graphviz import Digraph

class Nodo:
    def __init__(self, nombre, apellido, carnet):
        self.nombre = nombre
        self.apellido = apellido
        self.carnet = carnet
        self.siguiente = None
        self.anterior = None


class ListaDoble:
    def __init__(self):
        self.inicio = None
        self.fin = None

    def agregar_inicio(self, nombre, apellido, carnet):
        nuevo_nodo = Nodo(nombre, apellido, carnet)
        if self.inicio is None:
            self.inicio = nuevo_nodo
            self.fin = nuevo_nodo
        else:
            nuevo_nodo.siguiente = self.inicio
            self.inicio.anterior = nuevo_nodo
            self.inicio = nuevo_nodo
        
        print("Nodo agregado al inicio.")
        self.generar_grafico()
    
    def agregar_final(self, nombre, apellido, carnet):
        nuevo_nodo = Nodo(nombre, apellido, carnet)
        if self.fin is None:
            self.inicio = nuevo_nodo
            self.fin = nuevo_nodo
        else:
            self.fin.siguiente = nuevo_nodo
            nuevo_nodo.anterior = self.fin
            self.fin = nuevo_nodo
        
        print("Nodo agregado al final.")
        self.generar_grafico()

    def eliminar(self, carnet):
        actual = self.inicio
        while actual:
            if actual.carnet == carnet:
                if actual.anterior:
                    actual.anterior.siguiente = actual.siguiente
                else:
                    self.inicio = actual.siguiente
                
                if actual.siguiente:
                    actual.siguiente.anterior = actual.anterior
                else:
                    self.fin = actual.anterior
                
                print("Nodo eliminado.")
                self.generar_grafico()
                return
            
            actual = actual.siguiente
        
        print("Nodo no encontrado.")

    def imprimir(self):
        actual = self.inicio
        while actual:
            print(f"Nombre: {actual.nombre}, Apellido: {actual.apellido}, Carnet: {actual.carnet}")
            actual = actual.siguiente
   
    def generar_grafico(self):
        dot = Digraph(format="png")
        dot.attr(rankdir="LR")

        actual = self.inicio
        anterior_id = None
        contador = 0

        while actual:
            nodo_id = f"N{contador}"
            etiqueta = f"{actual.nombre}\n{actual.apellido}\n{actual.carnet}"
            dot.node(nodo_id, etiqueta)

            if anterior_id is not None:
                dot.edge(anterior_id, nodo_id)
                dot.edge(nodo_id, anterior_id)

            anterior_id = nodo_id
            actual = actual.siguiente
            contador += 1

        dot.render("lista_doblemente_enlazada", view=False)
        print("Imagen generada: lista_doblemente_enlazada.png")


def menu():
    lista = ListaDoble()

    while True:
        print("\n===== MENU =====")
        print("1. Insertar al principio")
        print("2. Insertar al final")
        print("3. Eliminar por carnet")
        print("4. Mostrar lista")
        print("5. Salir")

        opcion = input("Seleccione una opcion: ")

        if opcion == "1":
            nombre = input("Nombre: ")
            apellido = input("Apellido: ")
            carnet = input("Carnet: ")
            lista.agregar_inicio(nombre, apellido, carnet)

        elif opcion == "2":
            nombre = input("Nombre: ")
            apellido = input("Apellido: ")
            carnet = input("Carnet: ")
            lista.agregar_final(nombre, apellido, carnet)

        elif opcion == "3":
            carnet = input("Carnet a eliminar: ")
            lista.eliminar(carnet)

        elif opcion == "4":
            lista.imprimir()

        elif opcion == "5":
            print("Saliendo...")
            break

        else:
            print("Opcion incorrecta")


menu()
