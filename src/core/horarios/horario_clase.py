from .horario_base import HorarioBase

class HorarioClaseNormal(HorarioBase):
    def description(self):
        return f"Clase normal de {self.asignatura['nombre']} en {self.aula['nombre']} dada por {self.docente['nombre']} {self.docente['apellido']} de {self.start_time} a {self.end_time} en {self.sede['nombre']} el {self.dia}"

class HorarioLaboratorio(HorarioBase):
    def description(self):
        return f"Laboratorio de {self.asignatura['nombre']} en {self.aula['nombre']} dada por {self.docente['nombre']} {self.docente['apellido']} de {self.start_time} a {self.end_time} en {self.sede['nombre']} el {self.dia}"

class HorarioVirtual(HorarioBase):
    def description(self):
        return f"Clase virtual de {self.asignatura['nombre']} dada por {self.docente['nombre']} {self.docente['apellido']} de {self.start_time} a {self.end_time} el {self.dia}"

class HorarioBloqueo(HorarioBase):
    def description(self):
        return f"Bloqueo de {self.asignatura['nombre']} en {self.aula['nombre']} de {self.start_time} a {self.end_time} en {self.sede['nombre']} el {self.dia}"