from juego.tablero import Tablero
from juego.logica import lineas_ganadoras

_COLOR_CELDA = {'X': '#AED6F1', 'O': '#F1948A', ' ': '#FFFFFF'}
_COLOR_SIM   = {'X': '#1A5276', 'O': '#78281F'}
_COLOR_WIN   = '#F9E79F'

def _tablero_html(tablero, ganador_sim=None, anotacion=''):
    posiciones_win = set()
    if ganador_sim:
        for linea in lineas_ganadoras(tablero, ganador_sim):
            for pos in linea:
                posiciones_win.add(pos)

    filas = ['<TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">']
    for f in range(3):
        filas.append('<TR>')
        for c in range(3):
            val = tablero.obtener(f, c)
            bg = _COLOR_WIN if (f, c) in posiciones_win else _COLOR_CELDA.get(val, '#FFFFFF')
            if val != ' ':
                color = _COLOR_SIM.get(val, '#000000')
                celda = f'<FONT COLOR="{color}" POINT-SIZE="13"><B>{val}</B></FONT>'
            else:
                celda = '<FONT POINT-SIZE="13"> </FONT>'
            filas.append(f'<TD BGCOLOR="{bg}">{celda}</TD>')
        filas.append('</TR>')
    if anotacion:
        filas.append(
            f'<TR><TD COLSPAN="3" ALIGN="CENTER" BGCOLOR="#EAECEE">'
            f'<FONT POINT-SIZE="8">{anotacion}</FONT></TD></TR>'
        )
    filas.append('</TABLE>')
    return ''.join(filas)

def partida_a_dot(registro, cerebro_x, cerebro_o):
    tablero = Tablero()
    lineas = [
        'digraph Partida {',
        f'  label="Partida #{registro.id}  —  {registro.resumen()}";',
        '  labelloc=t; labeljust=c;',
        '  rankdir=LR;',
        '  nodesep=0.5; ranksep=1.0;',
        '  node [shape=none, margin=0];',
        '  edge [fontsize=9, fontname="Helvetica", arrowsize=0.7];',
        '',
    ]

    id_prev = 'e0'
    lineas.append(f'  {id_prev} [label=<{_tablero_html(tablero, anotacion="inicio")}>];')

    lista_jugadas = list(registro.jugadas)
    for i, (f, c, sim) in enumerate(lista_jugadas, 1):
        cerebro = cerebro_x if sim == 'X' else cerebro_o
        jugadas_estado = cerebro._memoria.buscar(tablero.clave())
        peso = None
        if jugadas_estado:
            for j in jugadas_estado:
                if j.fila == f and j.columna == c:
                    peso = j.peso
                    break

        tablero.colocar(f, c, sim)
        id_nodo = f'e{i}'
        es_ultimo = (i == len(lista_jugadas))
        gan_nodo = registro.ganador if es_ultimo else None
        ann = registro.resumen() if es_ultimo else ''
        html = _tablero_html(tablero, gan_nodo, ann)
        lineas.append(f'  {id_nodo} [label=<{html}>];')

        color = _COLOR_SIM.get(sim, '#444444')
        etiq = f'{sim}({f},{c})'
        if peso is not None:
            etiq += f' p={peso:.2f}'
        lineas.append(
            f'  {id_prev} -> {id_nodo} '
            f'[label="{etiq}", color="{color}", fontcolor="{color}"];'
        )
        id_prev = id_nodo

    lineas.append('}')
    return '\n'.join(lineas)

