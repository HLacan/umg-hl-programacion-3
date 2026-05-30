from estructuras.lista import Lista

_LINEAS = [
    ((0,0),(0,1),(0,2)),
    ((1,0),(1,1),(1,2)),
    ((2,0),(2,1),(2,2)),
    ((0,0),(1,0),(2,0)),
    ((0,1),(1,1),(2,1)),
    ((0,2),(1,2),(2,2)),
    ((0,0),(1,1),(2,2)),
    ((0,2),(1,1),(2,0)),
]

def ganador(tablero):
    for linea in _LINEAS:
        a = tablero.obtener(linea[0][0], linea[0][1])
        b = tablero.obtener(linea[1][0], linea[1][1])
        c = tablero.obtener(linea[2][0], linea[2][1])
        if a != ' ' and a == b == c:
            return a
    return None

def empate(tablero):
    return tablero.lleno() and ganador(tablero) is None

def terminada(tablero):
    return ganador(tablero) is not None or empate(tablero)

def lineas_ganadoras(tablero, simbolo):
    resultado = Lista()
    for linea in _LINEAS:
        a = tablero.obtener(linea[0][0], linea[0][1])
        b = tablero.obtener(linea[1][0], linea[1][1])
        c = tablero.obtener(linea[2][0], linea[2][1])
        if a == b == c == simbolo:
            sublista = Lista()
            for pos in linea:
                sublista.agregar(pos)
            resultado.agregar(sublista)
    return resultado

