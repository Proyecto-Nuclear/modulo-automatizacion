from typing import Dict, Any
from .builder_factory import BuilderFactory
from .horario_builder_interface import IHorarioBuilder
from ..horario_base import HorarioBase

class HorarioDirector:
    """
    Director que orquesta la construcción de horarios utilizando un builder.
    """

    def __init__(self):
        self._builder = None

    def set_builder(self, builder: IHorarioBuilder) -> None:
        """
        Establece el builder a utilizar.

        :param builder: Instancia de un builder que implementa IHorarioBuilder
        """
        self._builder = builder

    def get_builder_tipo(self) -> str:
        """
        Obtiene el tipo de builder configurado.

        :return: Tipo de builder o None si no hay builder configurado
        """
        return self._builder.get_tipo() if self._builder else None

    def construct_horario_completo(self, datos: Dict[str, Any]) -> HorarioBase:
        """
        Construye un horario completo a partir de un diccionario de datos.

        :param datos: Diccionario con todos los datos necesarios para el horario
        :return: Instancia de HorarioBase construida
        :raises ValueError: Si no hay builder configurado
        """
        if not self._builder:
            raise ValueError("No hay builder configurado. Debe establecer uno con set_builder()")

        self._builder.reset()

        # Establecer los datos solo si están presentes y no son None
        if datos.get('docente') is not None:
            self._builder.set_docente(datos['docente'])
        if datos.get('aula') is not None:
            self._builder.set_aula(datos['aula'])
        if datos.get('asignatura') is not None:
            self._builder.set_asignatura(datos['asignatura'])
        if datos.get('start_time') is not None and datos.get('end_time') is not None:
            self._builder.set_tiempo(datos['start_time'], datos['end_time'])
        if datos.get('dia') is not None:
            self._builder.set_dia(datos['dia'])
        if datos.get('sede') is not None:
            self._builder.set_sede(datos['sede'])
        if datos.get('id') is not None:
            self._builder.set_id(datos['id'])

        # Establecer metadatos adicionales
        metadatos = {k: v for k, v in datos.items() if k not in [
            'docente', 'aula', 'asignatura', 'start_time', 'end_time', 'dia', 'sede', 'id'
        ]}
        if metadatos:
            self._builder.set_metadatos(**metadatos)

        return self._builder.build()

    def construct_horario_basico(
            self,
            tipo: str,
            docente: Dict[str, Any] = None,
            aula: Dict[str, Any] = None,
            asignatura: Dict[str, Any] = None,
            start_time: str = None,
            end_time: str = None,
            dia: str = None,
            sede: Dict[str, Any] = None,
            horario_id: str = None
    ) -> HorarioBase:
        """
        Construye un horario básico utilizando el BuilderFactory.

        :param tipo: Tipo de horario a construir (normal, laboratorio, virtual, bloqueo)
        :param docente: Diccionario con información del docente
        :param aula: Diccionario con información del aula
        :param asignatura: Diccionario con información de la asignatura
        :param start_time: Hora de inicio
        :param end_time: Hora de fin
        :param dia: Día de la semana
        :param sede: Diccionario con información de la sede
        :param horario_id: ID del horario
        :return: Instancia de HorarioBase construida
        """
        builder = BuilderFactory.create_builder(tipo)
        self.set_builder(builder)

        builder.reset()

        if docente is not None:
            builder.set_docente(docente)
        if aula is not None:
            builder.set_aula(aula)
        if asignatura is not None:
            builder.set_asignatura(asignatura)
        if start_time is not None and end_time is not None:
            builder.set_tiempo(start_time, end_time)
        if dia is not None:
            builder.set_dia(dia)
        if sede is not None:
            builder.set_sede(sede)
        if horario_id is not None:
            builder.set_id(horario_id)

        return builder.build()