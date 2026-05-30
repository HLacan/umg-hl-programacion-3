class Registro:
    _siguiente_id = 1

    def __init__(self, ganador, jugadas):
        self.id = Registro._siguiente_id
        Registro._siguiente_id += 1
        self.ganador = ganador
        self.jugadas = jugadas

    def resumen(self):
        total = len(self.jugadas)
        if self.ganador:
            return f"{self.ganador} ganó en {total} jugadas"
        return f"Empate en {total} jugadas"

    def resultado(self):
        return self.ganador if self.ganador else 'empate'

    def total_jugadas(self):
        return len(self.jugadas)

    def clave_final(self):
        texto = '         '
        for (f, c, s) in self.jugadas:
            idx = f * 3 + c
            texto = texto[:idx] + s + texto[idx+1:]
        return texto

