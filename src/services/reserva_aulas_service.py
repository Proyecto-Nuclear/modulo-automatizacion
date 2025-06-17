import json
import os
from datetime import datetime

class ReservaAulaService:
    def __init__(self):
        self.data_dir = self._get_data_dir()

    def _get_data_dir(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(base_dir, '../../data'))

    def _load_json(self, filename):
        with open(os.path.join(self.data_dir, filename), encoding="utf-8") as f:
            return json.load(f)

    def _save_json(self, filename, data):
        with open(os.path.join(self.data_dir, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def reservar_aula(self, reserva: dict, id_usuario: str) -> dict:
        programaciones = self._load_json("programaciones.json")

        # Validar que no exista una reserva en el mismo horario
        for programacion in programaciones:
            if (
                    programacion["aula_id"] == reserva["aula_id"]
                    and programacion["fecha"] == reserva["fecha"]
                    and not (reserva["hora_fin"] <= programacion["hora_inicio"] or reserva["hora_inicio"] >= programacion["hora_fin"])
            ):
                return {"success": False, "message": "El aula ya está reservada en ese horario."}

        # Crear la nueva programación
        nueva_programacion = {
            "id": f"PROG{len(programaciones)+1:03d}",
            "aula_id": reserva["aula_id"],
            "docente_id": reserva.get("docente_id"),
            "asignatura_id": reserva["asignatura_id"],
            "fecha": reserva["fecha"],
            "hora_inicio": reserva["hora_inicio"],
            "hora_fin": reserva["hora_fin"],
            "id_usuario": id_usuario,
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d"),
            "hora_creacion": datetime.now().strftime("%H:%M"),
            "estado": "reservado",
            "dia": reserva.get("dia", ""),
            "semestre": reserva.get("semestre", None),
        }

        programaciones.append(nueva_programacion)
        self._save_json("programaciones.json", programaciones)

        return {"success": True, "message": "Reserva realizada con éxito.", "reserva": nueva_programacion}

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