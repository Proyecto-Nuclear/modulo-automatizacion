import json
import os
from datetime import datetime, timedelta


class ReservaAulaService:
    def __init__(self):
        self.data_dir = self._get_data_dir()

    def _get_data_dir(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(base_dir, '../../data'))

    def _load_json(self, filename):
        with open(os.path.join(self.data_dir, filename), encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def obtener_num_meses(duracion_str):
        return int(duracion_str.split()[0])

    @staticmethod
    def obtener_dia_num(dia_nombre):
        dias = {
            "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
            "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
        }
        return dias[dia_nombre.lower()]

    @staticmethod
    def generar_fechas_recurrentes(fecha_inicio_str, dia_semana, meses):
        fechas = []
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%d/%m/%Y")
        # Encuentra el primer día de clase (puede ser la misma fecha_inicio o el siguiente día_semana)
        while fecha_inicio.weekday() != dia_semana:
            fecha_inicio += timedelta(days=1)
        fecha_actual = fecha_inicio
        fecha_fin = fecha_inicio + timedelta(days=meses*30)  # Aproximación de meses
        while fecha_actual < fecha_fin:
            fechas.append(fecha_actual.strftime("%d/%m/%Y"))
            fecha_actual += timedelta(days=7)
        return fechas

    def _save_json(self, filename, data):
        with open(os.path.join(self.data_dir, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def reservar_aula(self, reserva: dict, id_usuario: str) -> dict:
        programaciones = self._load_json("programaciones.json")
        asignaturas = self._load_json("asignaturas.json")
        asignatura = next((a for a in asignaturas if a["id"] == reserva["asignatura_id"]), None)
        if not asignatura:
            return {"success": False, "message": "Asignatura no encontrada."}

        duracion_meses = self.obtener_num_meses(asignatura["duracion"])
        dia_num = self.obtener_dia_num(reserva["dia"])
        fechas = self.generar_fechas_recurrentes(reserva["fecha"], dia_num, duracion_meses)

        nuevas_programaciones = []
        for fecha in fechas:
            # Validar que no exista una reserva en el mismo horario y fecha
            conflicto = any(
                p["aula_id"] == reserva["aula_id"] and
                p["fecha"] == fecha and
                not (reserva["hora_fin"] <= p["hora_inicio"] or reserva["hora_inicio"] >= p["hora_fin"])
                for p in programaciones
            )
            if conflicto:
                return {"success": False, "message": f"El aula ya está reservada el {fecha} en ese horario."}

            nueva_programacion = {
                "id": f"PROG{len(programaciones)+len(nuevas_programaciones)+1:03d}",
                "aula_id": reserva["aula_id"],
                "docente_id": reserva.get("docente_id"),
                "asignatura_id": reserva["asignatura_id"],
                "fecha": fecha,
                "hora_inicio": reserva["hora_inicio"],
                "hora_fin": reserva["hora_fin"],
                "id_usuario": id_usuario,
                "fecha_creacion": datetime.now().strftime("%Y-%m-%d"),
                "hora_creacion": datetime.now().strftime("%H:%M"),
                "estado": "reservado",
                "dia": reserva.get("dia", ""),
                "semestre": reserva.get("semestre", None),
            }
            nuevas_programaciones.append(nueva_programacion)

        programaciones.extend(nuevas_programaciones)
        self._save_json("programaciones.json", programaciones)

        return {
            "success": True,
            "message": f"Reserva realizada para {len(nuevas_programaciones)} sesiones.",
            "reservas": nuevas_programaciones
        }

    def obtener_todas_programaciones(self) -> list:
        return self._load_json("programaciones.json")

    def obtener_programacion_por_id(self, programacion_id: str) -> dict:
        programaciones = self._load_json("programaciones.json")
        return next((p for p in programaciones if p["id"] == programacion_id), None)

    def cambiar_estado_programacion(self, programacion_id: str, nuevo_estado: str) -> dict:
        programaciones = self._load_json("programaciones.json")
        programacion = next((p for p in programaciones if p["id"] == programacion_id), None)

        if not programacion:
            return {"success": False, "message": "Programación no encontrada"}

        programacion["estado"] = nuevo_estado
        self._save_json("programaciones.json", programaciones)

        return {"success": True, "message": f"Estado cambiado a {nuevo_estado}", "programacion": programacion}