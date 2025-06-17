from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime

from src.core.schedules.facade.horario_facade import HorarioFacade
from src.services.aula_disponible_service import AulaDisponibleService
from src.services.reserva_aulas_service import ReservaAulaService

class HorarioCompletoService:
    """
    Servicio que integra todo el flujo: aulas disponibles → reservas → horario final
    usando los patrones de diseño implementados.
    """

    def __init__(self):
        self.facade = HorarioFacade()
        self.aula_service = AulaDisponibleService()
        self.reserva_service = ReservaAulaService()
        self.data_dir = self._get_data_dir()

    def _get_data_dir(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(base_dir, '../../data'))

    def _load_json(self, filename):
        with open(os.path.join(self.data_dir, filename), encoding="utf-8") as f:
            return json.load(f)

    def obtener_aulas_disponibles_con_facade(
            self,
            asignatura_id: str,
            hora_inicio: str,
            hora_fin: str,
            dia: str,
            cantidad_estudiantes: int,
            semestre: int
    ) -> Dict[str, Any]:
        """
        Obtiene aulas disponibles y las valida usando el Facade.
        """
        # 1. Obtener aulas disponibles con el servicio existente
        resultado = self.aula_service.get_aulas_disponibles(
            asignatura_id, hora_inicio, hora_fin, dia, cantidad_estudiantes, semestre
        )

        # 2. Validar cada aula disponible usando el Facade
        aulas_validadas = []
        for aula in resultado.get('aulas_disponibles', []):
            # Crear datos de horario temporal para validación
            horario_data = {
                'tipo': self._determinar_tipo_horario(resultado['asignatura']),
                'asignatura': resultado['asignatura'],
                'aula': aula,
                'start_time': hora_inicio,
                'end_time': hora_fin,
                'dia': dia,
                'sede': aula.get('sede', {}),
                'id': f"temp_{aula['id']}_{asignatura_id}"
            }

            # Validar usando el Facade
            es_valido, error = self.facade.validar_horario(horario_data)
            if es_valido:
                aulas_validadas.append({
                    **aula,
                    'validacion_facade': 'OK'
                })
            else:
                # Mover a no disponibles si falla la validación del Facade
                resultado['aulas_no_disponibles'].append({
                    'id': aula['id'],
                    'nombre': aula['nombre'],
                    'razon': f"Validación Facade falló: {error}"
                })

        resultado['aulas_disponibles'] = aulas_validadas
        resultado['total_disponibles'] = len(aulas_validadas)
        resultado['total_no_disponibles'] = len(resultado['aulas_no_disponibles'])

        return resultado

    def crear_horario_desde_programacion(self, programacion_id: str) -> Dict[str, Any]:
        """
        Crea un horario usando el patrón Builder a partir de una programación reservada.
        """
        try:
            # 1. Obtener la programación
            programaciones = self._load_json("programaciones.json")
            programacion = next((p for p in programaciones if p["id"] == programacion_id), None)

            if not programacion:
                return {"success": False, "error": "Programación no encontrada"}

            if programacion.get("estado") != "reservado":
                return {"success": False, "error": f"La programación debe estar en estado 'reservado', actual: {programacion.get('estado')}"}

            # 2. Cargar datos relacionados
            asignaturas = self._load_json("asignaturas.json")
            aulas = self._load_json("aulas.json")
            docentes = self._load_json("docentes.json")
            sedes = self._load_json("sedes.json")

            # 3. Buscar entidades relacionadas
            asignatura = next((a for a in asignaturas if a["id"] == programacion["asignatura_id"]), None)
            aula = next((a for a in aulas if a["id"] == programacion["aula_id"]), None)
            docente = next((d for d in docentes if d["id"] == programacion.get("docente_id")), None)
            sede = next((s for s in sedes if s["id"] == aula.get("id_sede")), None) if aula else None

            if not all([asignatura, aula]):
                return {"success": False, "error": "No se encontraron todas las entidades relacionadas"}

            # 4. Determinar tipo de horario
            tipo_horario = self._determinar_tipo_horario(asignatura)

            # 5. Preparar datos para el Builder usando el Facade
            horario_data = {
                'tipo': tipo_horario,
                'asignatura': asignatura,
                'aula': aula,
                'docente': docente,
                'sede': sede,
                'start_time': programacion["hora_inicio"],
                'end_time': programacion["hora_fin"],
                'dia': programacion.get("dia", ""),
                'id': f"H_{programacion_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'programacion_id': programacion_id,
                'fecha': programacion.get("fecha"),
                'created_at': datetime.now().isoformat(),
                'estado': 'confirmado'
            }

            # 6. Crear horario usando el Facade
            horario, error = self.facade.crear_horario(**horario_data)

            if error:
                return {"success": False, "error": f"Error al crear horario: {error}"}

            # 7. Cambiar estado de la programación a 'ocupado'
            programacion["estado"] = "ocupado"
            programacion["horario_id"] = horario_data["id"]
            programacion["fecha_confirmacion"] = datetime.now().isoformat()

            # Guardar cambios
            with open(os.path.join(self.data_dir, "programaciones.json"), "w", encoding="utf-8") as f:
                json.dump(programaciones, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "horario": horario.to_dict() if hasattr(horario, 'to_dict') else horario,
                "programacion_actualizada": programacion,
                "tipo_horario": tipo_horario
            }

        except Exception as e:
            return {"success": False, "error": f"Error inesperado: {str(e)}"}

    def crear_horario_completo_semestre(self, semestre: int, validar_conjunto: bool = True) -> Dict[str, Any]:
        """
        Crea el horario completo de un semestre usando todas las programaciones ocupadas.
        """
        try:
            # 1. Obtener todas las programaciones ocupadas del semestre
            programaciones = self._load_json("programaciones.json")
            programaciones_ocupadas = [
                p for p in programaciones
                if p.get("estado") == "reservado" and p.get("semestre") == semestre
            ]

            if not programaciones_ocupadas:
                return {"success": False, "error": f"No hay programaciones ocupadas para el semestre {semestre}"}

            # 2. Crear horarios individuales
            horarios_creados = []
            errores = []

            for prog in programaciones_ocupadas:
                resultado = self.crear_horario_desde_programacion(prog["id"])
                if resultado["success"]:
                    horarios_creados.append(resultado["horario"])
                else:
                    errores.append(f"Programación {prog['id']}: {resultado['error']}")

            # 3. Validar conjunto si se solicita
            if validar_conjunto and horarios_creados:
                es_valido, error_conjunto = self.facade.validar_horarios_conjunto(horarios_creados)
                if not es_valido:
                    return {
                        "success": False,
                        "error": f"Validación de conjunto falló: {error_conjunto}",
                        "horarios_individuales": horarios_creados,
                        "errores_individuales": errores
                    }

            # 4. Obtener estadísticas del Facade
            estadisticas = self.facade.obtener_estadisticas()

            return {
                "success": True,
                "semestre": semestre,
                "total_horarios": len(horarios_creados),
                "horarios": horarios_creados,
                "errores": errores,
                "estadisticas": estadisticas,
                "validacion_conjunto": "OK" if validar_conjunto else "No validado"
            }

        except Exception as e:
            return {"success": False, "error": f"Error inesperado: {str(e)}"}

    def _determinar_tipo_horario(self, asignatura: Dict[str, Any]) -> str:
        """
        Determina el tipo de horario basado en la asignatura.
        """
        tipo_asignatura = asignatura.get('tipo', '').lower()

        if tipo_asignatura == 'laboratorio':
            return 'laboratorio'
        elif tipo_asignatura == 'virtual':
            return 'virtual'
        elif tipo_asignatura == 'bloqueo':
            return 'bloqueo'
        else:
            return 'normal'

    def obtener_resumen_sistema(self) -> Dict[str, Any]:
        """
        Obtiene un resumen completo del sistema usando el Facade.
        """
        return self.facade.obtener_resumen_sistema()