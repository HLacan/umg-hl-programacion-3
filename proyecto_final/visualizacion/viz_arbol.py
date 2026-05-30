from juego.tablero import Tablero

_AJUSTE_GANAR  =  1.0
_AJUSTE_EMPATE =  0.2
_AJUSTE_PERDER = -0.6

def arbol_b_a_dot(historial):
    arbol = historial._arbol

    if arbol.vacio():
        return (
            'digraph { node [shape=box, fontname="Helvetica"];'
            ' vacio [label="El historial está vacío.\\nJuega algunas partidas primero."]; }'
        )

    nodos_desc = arbol.estructura()
    id_a_nombre = {desc['id']: f'n{i}' for i, desc in enumerate(nodos_desc)}

    orden = arbol.orden
    total = historial.total()

    lineas = [
        'digraph ArbolB {',
        f'  label="Árbol B del Historial  ({total} partidas guardadas, orden={orden})";',
        '  labelloc=t; labeljust=c;',
        '  rankdir=TB;',
        '  nodesep=0.6; ranksep=1.2;',
        '  node [shape=none, margin=0];',
        '  edge [fontsize=8, fontname="Helvetica", arrowsize=0.7];',
        '',
    ]

    for desc in nodos_desc:
        nombre    = id_a_nombre[desc['id']]
        registros = [(c, historial.obtener(c)) for c in desc['claves']]
        n         = len(registros)
        es_hoja   = desc['es_hoja']

        filas = ['<TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0">']

        filas.append('<TR>')
        if not es_hoja:
            filas.append(
                '<TD PORT="p0" ROWSPAN="5" BGCOLOR="#95A5A6" WIDTH="14">'
                '<FONT POINT-SIZE="1"> </FONT></TD>'
            )
        for i, (clave, reg) in enumerate(registros):
            if reg and reg.ganador == 'X':
                bg_clave  = '#1A5276'
                badge     = 'X GANÓ'
                badge_bg  = '#2980B9'
            elif reg and reg.ganador == 'O':
                bg_clave  = '#78281F'
                badge     = 'O GANÓ'
                badge_bg  = '#E74C3C'
            else:
                bg_clave  = '#7D6608'
                badge     = 'EMPATE'
                badge_bg  = '#D4AC0D'

            filas.append(
                f'<TD COLSPAN="3" BGCOLOR="#1C2833" CELLPADDING="0">'
                f'<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR>'
                f'<TD BGCOLOR="{bg_clave}" CELLPADDING="3">'
                f'<FONT COLOR="white" POINT-SIZE="8"><B>ID:{clave}</B></FONT></TD>'
                f'<TD BGCOLOR="{badge_bg}" CELLPADDING="3">'
                f'<FONT COLOR="white" POINT-SIZE="7">{badge}</FONT></TD>'
                f'</TR></TABLE>'
                f'</TD>'
            )
            if i < n - 1:
                if not es_hoja:
                    filas.append(
                        f'<TD PORT="p{i + 1}" ROWSPAN="5" BGCOLOR="#95A5A6" WIDTH="14">'
                        f'<FONT POINT-SIZE="1"> </FONT></TD>'
                    )
                else:
                    filas.append(
                        '<TD ROWSPAN="5" BGCOLOR="#D5D8DC" WIDTH="4">'
                        '<FONT POINT-SIZE="1"> </FONT></TD>'
                    )
        if not es_hoja:
            filas.append(
                f'<TD PORT="p{n}" ROWSPAN="5" BGCOLOR="#95A5A6" WIDTH="14">'
                f'<FONT POINT-SIZE="1"> </FONT></TD>'
            )
        filas.append('</TR>')

        filas.append('<TR>')
        for clave, reg in registros:
            if reg:
                if reg.ganador == 'X':
                    texto_peso = f'X:+{_AJUSTE_GANAR:.1f}  O:{_AJUSTE_PERDER:.1f}'
                    bg_peso    = '#D6EAF8'
                elif reg.ganador == 'O':
                    texto_peso = f'X:{_AJUSTE_PERDER:.1f}  O:+{_AJUSTE_GANAR:.1f}'
                    bg_peso    = '#FADBD8'
                else:
                    texto_peso = f'X:+{_AJUSTE_EMPATE:.1f}  O:+{_AJUSTE_EMPATE:.1f}'
                    bg_peso    = '#FEF9E7'
            else:
                texto_peso = '?'
                bg_peso    = '#FDFEFE'
            filas.append(
                f'<TD COLSPAN="3" BGCOLOR="{bg_peso}" CELLPADDING="2">'
                f'<FONT POINT-SIZE="7">Δpeso: {texto_peso}</FONT></TD>'
            )
        filas.append('</TR>')

        for fila in range(3):
            filas.append('<TR>')
            for clave, reg in registros:
                if reg:
                    tablero_str = reg.clave_final()
                    for col in range(3):
                        idx       = fila * 3 + col
                        val       = tablero_str[idx]
                        bg        = '#AED6F1' if val == 'X' else '#F1948A' if val == 'O' else '#FDFEFE'
                        celda_val = val if val in ('X', 'O') else ' '
                        filas.append(
                            f'<TD BGCOLOR="{bg}" WIDTH="14" HEIGHT="12">'
                            f'<FONT POINT-SIZE="7"><B>{celda_val}</B></FONT></TD>'
                        )
                else:
                    filas.append('<TD COLSPAN="3">?</TD>')
            filas.append('</TR>')

        filas.append('</TABLE>')
        lineas.append(f'  {nombre} [label=<{"".join(filas)}>];')

    for desc in nodos_desc:
        if not desc['es_hoja']:
            padre = id_a_nombre[desc['id']]
            for i, id_hijo in enumerate(desc['hijos']):
                if id_hijo in id_a_nombre:
                    hijo = id_a_nombre[id_hijo]
                    lineas.append(f'  {padre}:p{i} -> {hijo} [color="#2C3E50"];')

    lineas.append('}')
    return '\n'.join(lineas)

def camino_ia_a_dot(registro, cerebro_o):
    jugadas_lista = [(f, c, s) for f, c, s in registro.jugadas]

    lineas = [
        'digraph Camino {',
        f'  label="Camino IA — Partida #{registro.id}  —  {registro.resumen()}";',
        '  labelloc=t; labeljust=c;',
        '  rankdir=TB;',
        '  nodesep=0.8; ranksep=1.4;',
        '  node [shape=none, margin=0];',
        '  edge [fontsize=11, fontname="Helvetica", arrowsize=0.8];',
        '',
    ]

    tablero = Tablero()
    nodos_o = []
    xmoves  = []

    for fila, col, simbolo in jugadas_lista:
        clave_antes = tablero.clave()
        tablero.colocar(fila, col, simbolo)

        if simbolo == 'X':
            xmoves.append(f'X({fila},{col})')
        else:
            jugadas_ia = cerebro_o._memoria.buscar(clave_antes)
            peso = None
            if jugadas_ia is not None:
                for j in jugadas_ia:
                    if j.fila == fila and j.columna == col:
                        peso = j.peso
                        break
            nodos_o.append({
                'num'        : len(nodos_o) + 1,
                'clave'      : tablero.clave(),
                'fila'       : fila,
                'col'        : col,
                'peso'       : peso,
                'xmoves_prev': list(xmoves),
            })
            xmoves = []

    if not nodos_o:
        return (
            'digraph { node [shape=box, fontname="Helvetica"];'
            ' vacio [label="La IA (O) no realizó ninguna jugada."]; }'
        )

    for i, n in enumerate(nodos_o):
        clave    = n['clave']
        fila     = n['fila']
        col      = n['col']
        peso_txt = f'{n["peso"]:.2f}' if n['peso'] is not None else '?'

        celdas = ['<TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0">']

        celdas += [
            '<TR>',
            f'<TD COLSPAN="3" BGCOLOR="#78281F" CELLPADDING="4">'
            f'<FONT COLOR="white" POINT-SIZE="10">'
            f'<B>Turno {n["num"]}  —  O({fila},{col})</B></FONT></TD>',
            '</TR>',
        ]

        for f in range(3):
            celdas.append('<TR>')
            for c in range(3):
                idx = f * 3 + c
                val = clave[idx]
                es_dest = (f == fila and c == col)
                bg  = ('#F9E79F' if es_dest
                       else '#AED6F1' if val == 'X'
                       else '#F1948A' if val == 'O'
                       else '#FDFEFE')
                sym = val if val in ('X', 'O') else ' '
                fc  = '#1A5276' if val == 'X' else '#78281F' if val == 'O' else '#CCCCCC'
                celdas.append(
                    f'<TD BGCOLOR="{bg}" WIDTH="30" HEIGHT="26">'
                    f'<FONT COLOR="{fc}" POINT-SIZE="14"><B>{sym}</B></FONT></TD>'
                )
            celdas.append('</TR>')

        celdas += [
            '<TR>',
            f'<TD COLSPAN="3" BGCOLOR="#EBF5FB" CELLPADDING="4">'
            f'<FONT POINT-SIZE="10">peso = <B>{peso_txt}</B></FONT></TD>',
            '</TR>',
            '</TABLE>',
        ]

        lineas.append(f'  o{i} [label=<{"".join(celdas)}>];')

    for i in range(len(nodos_o) - 1):
        xm  = nodos_o[i + 1]['xmoves_prev']
        etq = '  '.join(xm) if xm else '...'
        lineas.append(
            f'  o{i} -> o{i + 1} '
            f'[label="{etq}", color="#1A5276", fontcolor="#1A5276"];'
        )

    lineas.append('}')
    return '\n'.join(lineas)

