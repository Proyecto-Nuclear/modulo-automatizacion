from typing import Dict, List, Any, Tuple, Union, Optional

from src.core.schedules.facade.services.buscador import BuscadorHorarios
from src.core.schedules.facade.services.configurador import ConfiguradorSistema
from src.core.schedules.facade.services.creador import CreadorHorarios
from src.core.schedules.facade.services.estadisticas import GestorEstadisticas
from src.core.schedules.facade.services.exportador import ExportadorHorarios
from src.core.schedules.facade.services.restricciones import GestorRestricciones
from src.core.schedules.facade.services.validador import ValidadorHorarios


class HorarioFacade:
    """
    Facade que proporciona una interfaz unificada para el sistema de horarios.
    Coordina la creación, validación y gestión de horarios delegando a servicios específicos.
    """

    def __init__(self):
        """
        Inicializa la fachada con todos los componentes necesarios.
        """
        self.creador = CreadorHorarios()
        self.validador = ValidadorHorarios()
        self.buscador = BuscadorHorarios()
        self.exportador = ExportadorHorarios()
        self.configurador = ConfiguradorSistema()
        self.estadisticas = GestorEstadisticas()
        self.restricciones = GestorRestricciones()

    # ========== MÉTODOS DELEGADOS ==========

    def crear_horario(self, tipo: str, validar: bool = True, **kwargs) -> Tuple[Any, Optional[str]]:
        # 1. Crear el horario
        horario, error = self.creador.crear_horario(tipo, validar, **kwargs)
        if error:
            # Error en la creación (factory)
            self.estadisticas._update_stats('validaciones_fallidas')
            return None, error

        # 2. Validar si corresponde
        if validar:
            es_valido, error_validacion = self.validador.validar_horario(horario.to_dict() if hasattr(horario, 'to_dict') else horario)
            if not es_valido:
                self.estadisticas._update_stats('validaciones_fallidas')
                return horario, f"Restricción violada: {error_validacion}"

        # 3. Si todo bien, actualizar estadísticas y retornar
        self.estadisticas._update_stats('horarios_creados')
        self.estadisticas._update_stats('validaciones_exitosas')
        return horario, None

    def crear_horarios_lote(self, horarios_data: List[Dict[str, Any]],
                            validar_individual: bool = True,
                            validar_conjunto: bool = True) -> Dict[str, Any]:
        return self.creador.crear_horarios_lote(horarios_data, validar_individual, validar_conjunto)

    def validar_horario(self, horario_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        return self.validador.validar_horario(horario_data)

    def validar_horarios_conjunto(self, horarios_data: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        return self.validador.validar_horarios_conjunto(horarios_data)

    def buscar_horarios_docente(self, docente_id: str, horarios: List[Any]) -> List[Any]:
        return self.buscador.buscar_horarios_docente(docente_id, horarios)

    def buscar_horarios_aula(self, aula_id: str, horarios: List[Any]) -> List[Any]:
        return self.buscador.buscar_horarios_aula(aula_id, horarios)

    def buscar_horarios_dia(self, dia: str, horarios: List[Any]) -> List[Any]:
        return self.buscador.buscar_horarios_dia(dia, horarios)

    def detectar_conflictos(self, horarios: List[Any]) -> Dict[str, List[str]]:
        return self.validador.detectar_conflictos(horarios)

    def configurar(self, **config) -> None:
        self.configurador.configurar(config)

    def obtener_configuracion(self) -> Dict[str, Any]:
        return self.configurador.obtener_configuracion()

    def obtener_estadisticas(self) -> Dict[str, Any]:
        return self.estadisticas.obtener_estadisticas()

    def reiniciar_estadisticas(self) -> None:
        self.estadisticas.reiniciar_estadisticas()

    def exportar_horarios(self, horarios: List[Any], formato: str = 'json') -> Union[str, Dict, List]:
        return self.exportador.exportar_horarios(horarios, formato)

    def obtener_tipos_horarios_disponibles(self) -> List[str]:
        return self.creador.obtener_tipos_horarios_disponibles()

    def es_tipo_horario_valido(self, tipo: str) -> bool:
        return self.creador.es_tipo_horario_valido(tipo)

    def obtener_resumen_sistema(self) -> Dict[str, Any]:
        return {
            'facade_version': '2.0',
            'tipos_horarios_disponibles': self.obtener_tipos_horarios_disponibles(),
            'configuracion': self.obtener_configuracion(),
            'estadisticas': self.obtener_estadisticas(),
            'restricciones_configuradas': self.restricciones.obtener_info_restricciones()
        }

    def __str__(self) -> str:
        return f"HorarioFacade(horarios_creados={self.estadisticas.stats['horarios_creados']}, validaciones_exitosas={self.estadisticas.stats['validaciones_exitosas']})"

    def __repr__(self) -> str:
        return f"HorarioFacade(stats={self.estadisticas.stats})"