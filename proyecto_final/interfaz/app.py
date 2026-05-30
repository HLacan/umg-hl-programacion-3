import base64
import glob
import os
import shutil
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from juego.tablero import Tablero
from juego.logica import ganador, empate, terminada, lineas_ganadoras
from aprendizaje.cerebro import Cerebro, poblar_todos_estados
from aprendizaje.entrenador import Entrenador
from historial.historial import Historial
from estructuras.lista import Lista
from visualizacion.viz_partida import partida_a_dot
from visualizacion.viz_arbol import arbol_b_a_dot, camino_ia_a_dot

azul_oscuro = '#1E1B4B'
azul_btn    = '#312E81'
azul_activo = '#6366F1'
blanco      = '#F5F3FF'
color_x     = '#C7D2FE'
color_o     = '#FECDD3'
color_win   = '#FDE68A'
color_vacia = '#EEF2FF'

_btn_verde   = '#059669'
_btn_rojo    = '#DC2626'
_btn_violeta = '#7C3AED'
_gris_texto  = '#4B5563'
_gris_suave  = '#9CA3AF'

def _asegurar_graphviz():
    if shutil.which('dot'):
        return
    if sys.platform != 'win32':
        return
    localappdata = os.environ.get('LOCALAPPDATA', '')
    patrones = [
        r'C:\Program Files\Graphviz*\bin\dot.exe',
        r'C:\Program Files (x86)\Graphviz*\bin\dot.exe',
        os.path.join(localappdata, r'Programs\Graphviz*\bin\dot.exe'),
        os.path.join(localappdata, r'Microsoft\WinGet\Packages\Graphviz*\Graphviz*\bin\dot.exe'),
    ]
    for patron in patrones:
        encontrados = glob.glob(patron)
        if encontrados:
            directorio = os.path.dirname(encontrados[0])
            os.environ['PATH'] = directorio + os.pathsep + os.environ.get('PATH', '')
            return

def _mostrar_dot(dot_string, titulo, ventana_padre):
    import graphviz
    _asegurar_graphviz()

    top = tk.Toplevel(ventana_padre)
    top.title(titulo)
    top.geometry('950x700')

    foto = None
    error = ''
    try:
        png = graphviz.Source(dot_string).pipe(format='png')
        foto = tk.PhotoImage(data=base64.b64encode(png).decode('ascii'))
    except Exception as e:
        error = str(e)

    if foto:
        hbar = tk.Scrollbar(top, orient='horizontal')
        hbar.pack(side='bottom', fill='x')
        marco = tk.Frame(top)
        marco.pack(fill='both', expand=True)
        vbar = tk.Scrollbar(marco, orient='vertical')
        vbar.pack(side='right', fill='y')
        lienzo = tk.Canvas(marco, bg=blanco, xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        lienzo.pack(side='left', fill='both', expand=True)
        hbar.config(command=lienzo.xview)
        vbar.config(command=lienzo.yview)
        lienzo.create_image(0, 0, anchor='nw', image=foto)
        lienzo.configure(scrollregion=(0, 0, foto.width(), foto.height()))
        lienzo._foto = foto
        lienzo.bind('<MouseWheel>', lambda e: lienzo.yview_scroll(-1 if e.delta > 0 else 1, 'units'))
    else:
        tk.Label(top, text=f'Error: {error}', fg='red').pack(pady=8)
        hbar = tk.Scrollbar(top, orient='horizontal')
        hbar.pack(side='bottom', fill='x')
        marco = tk.Frame(top)
        marco.pack(fill='both', expand=True)
        vbar = tk.Scrollbar(marco, orient='vertical')
        vbar.pack(side='right', fill='y')
        texto = tk.Text(marco, wrap='none', font=('Courier', 8),
                        xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        texto.pack(side='left', fill='both', expand=True)
        hbar.config(command=texto.xview)
        vbar.config(command=texto.yview)
        texto.insert('1.0', dot_string)
        texto.config(state='disabled')

class VistaJugar(tk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, bg=blanco)
        self.app = app
        self._tablero = Tablero()
        self._turno = 'X'
        self._terminada = False
        self._jugadas = Lista()
        self._construir()

    def _construir(self):
        tk.Label(self, text='Humano vs IA', font=('Helvetica', 16, 'bold'),
                 bg=blanco).pack(pady=(20, 4))
        tk.Label(self, text='Tú juegas con X. La IA juega con O.',
                 font=('Helvetica', 10), bg=blanco, fg=_gris_texto).pack(pady=(0, 12))

        self._estado_var = tk.StringVar(value='Tu turno (X)')
        tk.Label(self, textvariable=self._estado_var, font=('Helvetica', 12, 'bold'),
                 bg=blanco).pack(pady=(0, 8))

        marco_tablero = tk.Frame(self, bg='#C4B5FD')
        marco_tablero.pack(pady=4)
        self._botones = []
        for f in range(3):
            fila = []
            for c in range(3):
                btn = tk.Button(
                    marco_tablero, text='', font=('Helvetica', 36, 'bold'),
                    width=3, height=1, bg=color_vacia, relief=tk.FLAT, bd=0,
                    activebackground='#E8E8E8',
                    command=lambda f=f, c=c: self._clic(f, c),
                )
                btn.grid(row=f, column=c, padx=2, pady=2)
                fila.append(btn)
            self._botones.append(fila)

        tk.Button(self, text='Nueva partida', command=self._nueva_partida,
                  font=('Helvetica', 11), width=16, bg=azul_btn,
                  fg=blanco, relief=tk.FLAT, cursor='hand2').pack(pady=16)

    def _nueva_partida(self):
        self._tablero.reiniciar()
        self._jugadas = Lista()
        self._turno = 'X'
        self._terminada = False
        self._estado_var.set('Tu turno (X)')
        self._refrescar()

    def _clic(self, f, c):
        if self._terminada or self._turno != 'X':
            return
        self._hacer_jugada(f, c)

    def _hacer_jugada(self, f, c):
        if not self._tablero.colocar(f, c, self._turno):
            return
        self._jugadas.agregar((f, c, self._turno))
        self._refrescar()
        resultado = ganador(self._tablero)
        if resultado:
            self._fin(resultado)
            return
        if empate(self._tablero):
            self._fin(None)
            return
        self._turno = 'O' if self._turno == 'X' else 'X'
        self._estado_var.set(f'Turno: {self._turno}')
        if self._turno == 'O':
            self.after(300, self._turno_ia)

    def _turno_ia(self):
        if self._terminada:
            return
        jugada = self.app.cerebro_o.elegir(self._tablero)
        if jugada:
            self._hacer_jugada(jugada.fila, jugada.columna)

    def _fin(self, resultado):
        self._terminada = True
        if resultado == 'X':
            self.app.cerebro_o.reforzar('perdio')
            self._estado_var.set('¡Ganaste!')
        elif resultado == 'O':
            self.app.cerebro_o.reforzar('gano')
            self._estado_var.set('¡La IA gana!')
        else:
            self.app.cerebro_o.reforzar('empato')
            self._estado_var.set('¡Empate!')

        self._refrescar(resultado)
        registro = self.app.historial.agregar(resultado, self._jugadas)

        self.app.actualizar_contador()

        dot = partida_a_dot(registro, self.app.cerebro_x, self.app.cerebro_o)
        _mostrar_dot(dot, f'Partida #{registro.id} — {registro.resumen()}', self)

    def _refrescar(self, resultado=None):
        posiciones_win = set()
        if resultado:
            for linea in lineas_ganadoras(self._tablero, resultado):
                for pos in linea:
                    posiciones_win.add(pos)
        for f in range(3):
            for c in range(3):
                val = self._tablero.obtener(f, c)
                if (f, c) in posiciones_win:
                    bg = color_win
                elif val == 'X':
                    bg = color_x
                elif val == 'O':
                    bg = color_o
                else:
                    bg = color_vacia
                self._botones[f][c].config(text=val if val != ' ' else '', bg=bg)

    def al_mostrar(self):
        self._nueva_partida()

class VistaIAvsIA(tk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, bg=blanco)
        self.app = app
        self._tablero = Tablero()
        self._turno = 'X'
        self._activo = False
        self._partidas_sesion = 0
        self._tarea = None
        self._construir()

    def _construir(self):
        tk.Label(self, text='IA vs IA', font=('Helvetica', 16, 'bold'),
                 bg=blanco).pack(pady=(20, 4))

        marco_tablero = tk.Frame(self, bg='#C4B5FD')
        marco_tablero.pack(pady=4)
        self._botones = []
        for f in range(3):
            fila = []
            for c in range(3):
                btn = tk.Label(
                    marco_tablero, text='', font=('Helvetica', 36, 'bold'),
                    width=3, height=1, bg=color_vacia, relief=tk.RIDGE, bd=1,
                )
                btn.grid(row=f, column=c, padx=2, pady=2)
                fila.append(btn)
            self._botones.append(fila)

        self._partidas_var = tk.StringVar(value='Partidas esta sesión: 0')
        tk.Label(self, textvariable=self._partidas_var, font=('Helvetica', 10),
                 bg=blanco).pack(pady=4)

        marco_btns = tk.Frame(self, bg=blanco)
        marco_btns.pack(pady=8)
        self._btn_iniciar = tk.Button(marco_btns, text='Iniciar', command=self._iniciar,
                                      font=('Helvetica', 11), width=10, bg=_btn_verde,
                                      fg=blanco, relief=tk.FLAT, cursor='hand2')
        self._btn_iniciar.pack(side='left', padx=6)
        self._btn_detener = tk.Button(marco_btns, text='Detener', command=self._detener,
                                      font=('Helvetica', 11), width=10, bg=_btn_rojo,
                                      fg=blanco, relief=tk.FLAT, cursor='hand2',
                                      state='disabled')
        self._btn_detener.pack(side='left', padx=6)

    def _iniciar(self):
        self._activo = True
        self._btn_iniciar.config(state='disabled')
        self._btn_detener.config(state='normal')
        self._tablero.reiniciar()
        self._turno = 'X'
        self._jugadas = Lista()
        self._refrescar()
        self._siguiente_jugada()

    def _detener(self):
        self._activo = False
        if self._tarea:
            self.after_cancel(self._tarea)
            self._tarea = None
        self._btn_iniciar.config(state='normal')
        self._btn_detener.config(state='disabled')

    def _siguiente_jugada(self):
        if not self._activo:
            return
        cerebro = self.app.cerebro_x if self._turno == 'X' else self.app.cerebro_o
        jugada = cerebro.elegir(self._tablero, exploracion=0.1)
        if jugada:
            self._tablero.colocar(jugada.fila, jugada.columna, self._turno)
            self._jugadas.agregar((jugada.fila, jugada.columna, self._turno))
            self._refrescar()

        resultado = ganador(self._tablero)
        if resultado:
            self._fin_partida_ia(resultado)
            return
        if empate(self._tablero):
            self._fin_partida_ia(None)
            return

        self._turno = 'O' if self._turno == 'X' else 'X'
        self._tarea = self.after(300, self._siguiente_jugada)

    def _fin_partida_ia(self, resultado):
        if resultado:
            self.app.cerebro_x.reforzar('gano' if resultado == 'X' else 'perdio')
            self.app.cerebro_o.reforzar('gano' if resultado == 'O' else 'perdio')
        else:
            self.app.cerebro_x.reforzar('empato')
            self.app.cerebro_o.reforzar('empato')

        self._refrescar(resultado)
        self._partidas_sesion += 1
        self._partidas_var.set(f'Partidas esta sesión: {self._partidas_sesion}')
        self.app.historial.agregar(resultado, self._jugadas)
        self.app.actualizar_contador()

        if self._activo:
            self._tarea = self.after(600, self._nueva_partida_ia)

    def _nueva_partida_ia(self):
        if not self._activo:
            return
        self._tablero.reiniciar()
        self._turno = 'X'
        self._jugadas = Lista()
        self._refrescar()
        self._siguiente_jugada()

    def _refrescar(self, resultado=None):
        posiciones_win = set()
        if resultado:
            for linea in lineas_ganadoras(self._tablero, resultado):
                for pos in linea:
                    posiciones_win.add(pos)
        for f in range(3):
            for c in range(3):
                val = self._tablero.obtener(f, c)
                if (f, c) in posiciones_win:
                    bg = color_win
                elif val == 'X':
                    bg = color_x
                elif val == 'O':
                    bg = color_o
                else:
                    bg = color_vacia
                self._botones[f][c].config(text=val if val != ' ' else '', bg=bg)

    def al_mostrar(self):
        self._detener()
        self._tablero.reiniciar()
        self._refrescar()

class VistaHistorial(tk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, bg=blanco)
        self.app = app
        self._construir()

    def _construir(self):
        tk.Label(self, text='Historial de partidas', font=('Helvetica', 16, 'bold'),
                 bg=blanco).pack(pady=(20, 12))

        marco = tk.Frame(self, bg=blanco)
        marco.pack(fill='both', expand=True, padx=20)

        scroll = tk.Scrollbar(marco, orient='vertical')
        self._lista = tk.Listbox(marco, height=14, width=36, font=('Courier', 10),
                                  yscrollcommand=scroll.set, selectbackground=azul_activo)
        scroll.config(command=self._lista.yview)
        self._lista.pack(side='left')
        scroll.pack(side='left', fill='y')

        self._detalle_var = tk.StringVar(value='Selecciona una partida')
        tk.Label(marco, textvariable=self._detalle_var, font=('Courier', 10),
                 bg=blanco, justify='left', wraplength=240).pack(side='left', padx=20, anchor='n')

        self._lista.bind('<<ListboxSelect>>', self._al_seleccionar)

        marco_btns = tk.Frame(self, bg=blanco)
        marco_btns.pack(pady=8)
        tk.Button(marco_btns, text='Ver árbol B', command=self._ver_arbol_historial,
                  font=('Helvetica', 10), bg=azul_btn, fg=blanco,
                  relief=tk.FLAT, cursor='hand2', width=14).pack(side='left', padx=4)
        tk.Button(marco_btns, text='Ver partida', command=self._ver_partida,
                  font=('Helvetica', 10), bg=azul_btn, fg=blanco,
                  relief=tk.FLAT, cursor='hand2', width=12).pack(side='left', padx=4)
        tk.Button(marco_btns, text='Ver camino IA', command=self._ver_camino_ia,
                  font=('Helvetica', 10), bg=_btn_violeta, fg=blanco,
                  relief=tk.FLAT, cursor='hand2', width=14).pack(side='left', padx=4)

    def _al_seleccionar(self, evento):
        seleccion = self._lista.curselection()
        if not seleccion:
            return
        texto = self._lista.get(seleccion[0])
        id_partida = int(texto.split()[0].lstrip('#'))
        reg = self.app.historial.obtener(id_partida)
        if reg:
            tablero_final = reg.clave_final()
            sim = {' ': '·', 'X': 'X', 'O': 'O'}
            f0 = sim[tablero_final[0]] + sim[tablero_final[1]] + sim[tablero_final[2]]
            f1 = sim[tablero_final[3]] + sim[tablero_final[4]] + sim[tablero_final[5]]
            f2 = sim[tablero_final[6]] + sim[tablero_final[7]] + sim[tablero_final[8]]
            self._detalle_var.set(
                f'Partida #{reg.id}\n{reg.resumen()}\n\n{f0}\n{f1}\n{f2}'
            )

    def _ver_arbol_historial(self):
        dot = arbol_b_a_dot(self.app.historial)
        total = self.app.historial.total()
        _mostrar_dot(dot, f'Árbol B del Historial ({total} partidas)', self)

    def _ver_camino_ia(self):
        seleccion = self._lista.curselection()
        if not seleccion:
            messagebox.showwarning('Sin selección', 'Selecciona una partida primero.')
            return
        texto = self._lista.get(seleccion[0])
        id_partida = int(texto.split()[0].lstrip('#'))
        reg = self.app.historial.obtener(id_partida)
        if reg:
            dot = camino_ia_a_dot(reg, self.app.cerebro_o)
            _mostrar_dot(dot, f'Camino de la IA — Partida #{reg.id}', self)

    def _ver_partida(self):
        seleccion = self._lista.curselection()
        if not seleccion:
            messagebox.showwarning('Sin selección', 'Selecciona una partida primero.')
            return
        texto = self._lista.get(seleccion[0])
        id_partida = int(texto.split()[0].lstrip('#'))
        reg = self.app.historial.obtener(id_partida)
        if reg:
            dot = partida_a_dot(reg, self.app.cerebro_x, self.app.cerebro_o)
            _mostrar_dot(dot, f'Partida #{reg.id} — {reg.resumen()}', self)

    def al_mostrar(self):
        self._lista.delete(0, tk.END)
        registros = list(self.app.historial.todos())
        for reg in reversed(registros):
            self._lista.insert(tk.END, f'#{reg.id:<4} {reg.resumen()}')
        self._detalle_var.set('Selecciona una partida')

class VistaEntrenar(tk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, bg=blanco)
        self.app = app
        self._entrenando = False
        self._construir()

    def _construir(self):
        tk.Label(self, text='Entrenamiento automático', font=('Helvetica', 16, 'bold'),
                 bg=blanco).pack(pady=(20, 16))

        marco_n = tk.Frame(self, bg=blanco)
        marco_n.pack()
        tk.Label(marco_n, text='Partidas a simular:', font=('Helvetica', 11),
                 bg=blanco).pack(side='left')
        self._n_var = tk.IntVar(value=100)
        tk.Spinbox(marco_n, from_=10, to=10000, increment=100,
                   textvariable=self._n_var, width=7,
                   font=('Helvetica', 11)).pack(side='left', padx=8)

        self._btn_entrenar = tk.Button(self, text='Entrenar', command=self._entrenar,
                                       font=('Helvetica', 12), width=14, bg=_btn_verde,
                                       fg=blanco, relief=tk.FLAT, cursor='hand2')
        self._btn_entrenar.pack(pady=16)

        self._estado_var = tk.StringVar(value='')
        tk.Label(self, textvariable=self._estado_var, font=('Helvetica', 11, 'bold'),
                 bg=blanco).pack()

        self._reporte_var = tk.StringVar(value='')
        tk.Label(self, textvariable=self._reporte_var, font=('Courier', 11),
                 bg=blanco, justify='left').pack(pady=(8, 4))

        tk.Label(self, text='Partidas simuladas:', font=('Helvetica', 10, 'bold'),
                 bg=blanco).pack(anchor='w', padx=24)
        marco_lista = tk.Frame(self, bg=blanco)
        marco_lista.pack(fill='both', expand=True, padx=24, pady=(2, 8))
        scroll_lista = tk.Scrollbar(marco_lista, orient='vertical')
        self._lista_partidas = tk.Listbox(marco_lista, height=7, font=('Courier', 9),
                                          yscrollcommand=scroll_lista.set,
                                          selectbackground=azul_activo)
        scroll_lista.config(command=self._lista_partidas.yview)
        self._lista_partidas.pack(side='left', fill='both', expand=True)
        scroll_lista.pack(side='left', fill='y')

    def _entrenar(self):
        if self._entrenando:
            return
        n = self._n_var.get()
        self._entrenando = True
        self._btn_entrenar.config(state='disabled')
        self._estado_var.set(f'Entrenando {n} partidas...')
        self._reporte_var.set('')

        def ejecutar():
            entrenador = Entrenador()
            stats = entrenador.entrenar(self.app.cerebro_x, self.app.cerebro_o, n,
                                        historial=self.app.historial)
            self.after(0, lambda: self._al_terminar(stats, n))

        threading.Thread(target=ejecutar, daemon=True).start()

    def _al_terminar(self, stats, n):
        self._entrenando = False
        self._btn_entrenar.config(state='normal')
        self._estado_var.set('¡Entrenamiento completado!')

        self._reporte_var.set(
            f'Partidas jugadas : {n}\n'
            f'X ganó           : {stats["X"]}\n'
            f'O ganó           : {stats["O"]}\n'
            f'Empates          : {stats["empate"]}'
        )

        self._lista_partidas.delete(0, tk.END)
        for registro in stats['partidas']:
            self._lista_partidas.insert(tk.END, f'#{registro.id:<5} {registro.resumen()}')

        self.app.actualizar_contador()

    def al_mostrar(self):
        pass

class VistaIntegrantes(tk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, bg=blanco)
        self.app = app
        self._construir()

    def _construir(self):
        tk.Label(self, text='Integrantes del grupo', font=('Helvetica', 16, 'bold'),
                 bg=blanco).pack(pady=(30, 16))
        tk.Label(self,
                 text='Programación III',
                 font=('Helvetica', 11), bg=blanco, fg=_gris_texto,
                 justify='center').pack(pady=(0, 24))

        self._info = tk.Label(self,
                              text='Luis Emilio Sipac Maldonado\nCarné: 9490-24-5565\n\n'
                                   'Herbert Rafael Lacan Hernandez\nCarné: 9490-24-21332',
                              font=('Helvetica', 12), bg=blanco, justify='center')
        self._info.pack()

    def al_mostrar(self):
        pass

class VistaLimpiar(tk.Frame):

    def __init__(self, padre, app):
        super().__init__(padre, bg=blanco)
        self.app = app
        self._construir()

    def _construir(self):
        tk.Label(self, text='Limpiar / Reiniciar', font=('Helvetica', 16, 'bold'),
                 bg=blanco).pack(pady=(30, 12))

        tk.Label(self,
                 text='Esta opción borrará todo el aprendizaje\n'
                      'y el historial de partidas guardado.\n\n',
                 font=('Helvetica', 11), bg=blanco, fg=_gris_texto,
                 justify='center').pack(pady=(0, 20))

        marco_orden = tk.Frame(self, bg=blanco)
        marco_orden.pack(pady=(0, 6))

        tk.Label(marco_orden, text='Grado del Árbol B:',
                 font=('Helvetica', 11), bg=blanco).pack(side='left', padx=(0, 8))

        self._orden_var = tk.IntVar(value=4)
        tk.Spinbox(marco_orden, from_=3, to=8, textvariable=self._orden_var,
                   width=4, font=('Helvetica', 11)).pack(side='left')

        self._lbl_orden_info = tk.Label(self,
                 text='',
                 font=('Helvetica', 9), bg=blanco, fg=_gris_suave)
        self._lbl_orden_info.pack(pady=(0, 16))

        self._orden_var.trace_add('write', self._actualizar_info_orden)

        tk.Button(self, text='Sí, reiniciar todo',
                  command=self._confirmar_reinicio,
                  font=('Helvetica', 12), width=18,
                  bg=_btn_rojo, fg=blanco,
                  relief=tk.FLAT, cursor='hand2').pack(pady=8)

        self._estado_var = tk.StringVar(value='')
        tk.Label(self, textvariable=self._estado_var,
                 font=('Helvetica', 11, 'bold'), bg=blanco).pack(pady=12)

    def _actualizar_info_orden(self, *_):
        try:
            orden = self._orden_var.get()
        except Exception:
            return
        max_claves = orden - 1
        min_claves = (orden // 2) - 1
        self._lbl_orden_info.config(
            text=f''
        )

    def _confirmar_reinicio(self):
        orden = self._orden_var.get()
        respuesta = messagebox.askyesno(
            'Confirmar reinicio',
            f'¿Reiniciar todo con grado {orden} en el Árbol B+?\n\n'
            'Se borrará el aprendizaje y el historial completo.'
        )
        if respuesta:
            self.app.reiniciar(orden_arbol=orden)
            self._estado_var.set(f'¡Reinicio completado! (grado árbol B+: {orden})')

    def al_mostrar(self):
        self._estado_var.set('')
        orden_actual = self.app.historial._arbol.orden
        self._orden_var.set(orden_actual)
        self._actualizar_info_orden()

class TotitoApp(tk.Tk):
    _TAB_ORDEN = ['jugar', 'ia_vs_ia', 'historial', 'entrenar', 'limpiar', 'integrantes']
    _TAB_LABEL = {
        'jugar':       'Jugar vs IA',
        'ia_vs_ia':    'IA vs IA',
        'historial':   'Historial',
        'entrenar':    'Entrenar',
        'limpiar':     'Limpiar',
        'integrantes': 'Integrantes',
    }

    def __init__(self):
        super().__init__()
        self.title('Totito')
        self.resizable(True, True)
        self.configure(bg=azul_oscuro)
        self.minsize(680, 560)

        self.cerebro_x = Cerebro('X')
        self.cerebro_o = Cerebro('O')
        self.historial = Historial()

        self._lbl_contador = None
        self._construir_ui()
        poblar_todos_estados(self.cerebro_x, self.cerebro_o)
        self._notebook.select(0)
        self._vistas['jugar'].al_mostrar()

    def _construir_ui(self):
        # ── Encabezado superior ───────────────────────────────────────────────
        header = tk.Frame(self, bg=azul_oscuro, height=56)
        header.pack(side='top', fill='x')
        header.pack_propagate(False)

        tk.Label(header, text='TOTITO',
                 font=('Helvetica', 22, 'bold'),
                 bg=azul_oscuro, fg='#C7D2FE').pack(side='left', padx=(20, 6), pady=10)

        tk.Label(header, text='.',
                 font=('Helvetica', 11),
                 bg=azul_oscuro, fg='#818CF8').pack(side='left', pady=18)

        self._lbl_contador = tk.Label(header, text='Partidas: 0',
                                      font=('Helvetica', 10, 'bold'),
                                      bg=azul_oscuro, fg='#A5B4FC')
        self._lbl_contador.pack(side='right', padx=24)

        # ── Pestañas (Notebook) ───────────────────────────────────────────────
        style = ttk.Style(self)
        style.theme_use('default')
        style.configure('TNotebook',
                        background=azul_btn,
                        borderwidth=0,
                        tabmargins=[0, 0, 0, 0])
        style.configure('TNotebook.Tab',
                        background=azul_btn,
                        foreground='#C7D2FE',
                        font=('Helvetica', 10, 'bold'),
                        padding=[18, 9],
                        borderwidth=0,
                        focuscolor=azul_btn)
        style.map('TNotebook.Tab',
                  background=[('selected', azul_activo), ('active', '#4338CA')],
                  foreground=[('selected', '#FFFFFF'),   ('active', '#FFFFFF')])

        self._notebook = ttk.Notebook(self, style='TNotebook')
        self._notebook.pack(fill='both', expand=True)

        self._vistas = {
            'jugar':       VistaJugar(self._notebook, self),
            'ia_vs_ia':    VistaIAvsIA(self._notebook, self),
            'historial':   VistaHistorial(self._notebook, self),
            'entrenar':    VistaEntrenar(self._notebook, self),
            'limpiar':     VistaLimpiar(self._notebook, self),
            'integrantes': VistaIntegrantes(self._notebook, self),
        }

        for clave in self._TAB_ORDEN:
            self._notebook.add(self._vistas[clave], text=self._TAB_LABEL[clave])

        self._notebook.bind('<<NotebookTabChanged>>', self._al_cambiar_tab)

    def _al_cambiar_tab(self, _evento):
        vista_ia = self._vistas['ia_vs_ia']
        if getattr(vista_ia, '_activo', False):
            vista_ia._detener()

        idx   = self._notebook.index('current')
        clave = self._TAB_ORDEN[idx]
        self._vistas[clave].al_mostrar()

    def actualizar_contador(self):
        total = self.historial.total()
        if self._lbl_contador:
            self._lbl_contador.config(text=f'Partidas: {total}')

    def reiniciar(self, orden_arbol=4):
        self.cerebro_x._memoria.limpiar()
        self.cerebro_o._memoria.limpiar()
        self.historial = Historial(orden=orden_arbol)
        poblar_todos_estados(self.cerebro_x, self.cerebro_o)
        self.actualizar_contador()

