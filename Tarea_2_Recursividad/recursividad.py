def convertir_a_binario(numero):
    if numero == 0:
        return "0"
    elif numero == 1:
        return "1"
    else:
        return convertir_a_binario(numero // 2) + str(numero % 2)
    
def contar_digitos(numero):
    if numero < 10:
        return 1
    else:
        return 1 + contar_digitos(numero // 10)

def calcular_raiz_cuadrada(numero, valor):
    if valor * valor > numero:
        return valor - 1
    else:
        return calcular_raiz_cuadrada(numero, valor + 1)


def raiz_cuadrada_entera(numero):

    if numero < 0:
        raise ValueError("No existe raiz cuadrada")
    return calcular_raiz_cuadrada(numero, 0)

def convertir_a_decimal(numero):
    valores = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000
    }
    
    if len(numero) == 0:
        return 0
    
    if len(numero) == 1:
        return valores[numero]
    
    if valores[numero[0]] < valores[numero[1]]:
        return valores[numero[1]] - valores[numero[0]] + convertir_a_decimal(numero[2:])
    else:
        return valores[numero[0]] + convertir_a_decimal(numero[1:])

def suma_numeros_enteros(numero):
    if numero <= 1:
        return numero
    else:
        return numero + suma_numeros_enteros(numero - 1)
    
def menu():
    while True:
        print("\n===== MENU =====")
        print("1. Decimal a binario")
        print("2. Contar digitos")
        print("3. Calcular raiz cuadrada")
        print("4. Romanos a decimal")
        print("5. Sumar numeros enteros")
        print("6. Salir")

        opcion = input("Seleccione una opcion: ")

        if opcion == "1":
            numero = int(input("Ingrese un numero: "))
            print(f"Valor de {numero} en binario: {convertir_a_binario(numero)}")

        elif opcion == "2":
            numero = int(input("Ingrese un numero: "))
            print(f"Cantidad de digitos en {numero}: {contar_digitos(numero)}")

        elif opcion == "3":
            numero = int(input("Ingrese un numero: "))
            try:
                print(f"Raiz cuadrada entera de {numero}: {raiz_cuadrada_entera(numero)}")
            except ValueError as e:
                print(e)

        elif opcion == "4":
            numero = input("Ingrese un numero romano: ")
            print(f"Decimal de {numero}: {convertir_a_decimal(numero)}")

        elif opcion == "5":
            numero = int(input("Ingrese un numero: "))
            print(f"Suma de numeros enteros hasta {numero}: {suma_numeros_enteros(numero)}")

        elif opcion == "6":
            print("Saliendo...")
            break

        else:
            print("Opcion incorrecta")

menu()