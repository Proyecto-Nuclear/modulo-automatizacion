"""
Clase base para todos los controladores de restricciones.

Esta clase implementa el patrón Chain of Responsibility para validar restricciones
de horarios académicos. Cada handler valida una restricción específica y puede
pasar el control al siguiente handler en la cadena.

Diseñado para soportar tanto validaciones individuales (un bloque específico)
como validaciones globales (horario completo) en el sistema de generación
automática de horarios.
"""

from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import logging

class RestrictionHandler(ABC):
    """
    Clase base abstracta para todos los controladores de restricciones.

    Implementa el patrón Chain of Responsibility permitiendo que múltiples
    restricciones sean evaluadas en secuencia. Si una restricción falla,
    se detiene la cadena y se retorna el error.
    """

    def __init__(self, next_handler: Optional['RestrictionHandler'] = None):
        """
        Inicializa el handler con un handler siguiente opcional.

        :param next_handler: Siguiente handler en la cadena de responsabilidad
        """
        self._next_handler = next_handler
        self._logger = logging.getLogger(self.__class__.__name__)

    def set_next(self, next_handler: 'RestrictionHandler') -> 'RestrictionHandler':
        """
        Establece el siguiente handler en la cadena.

        :param next_handler: Handler que será ejecutado después de este
        :return: El handler que se acaba de establecer (para encadenamiento fluido)
        """
        if next_handler is None:
            raise ValueError("El siguiente handler no puede ser None")

        self._next_handler = next_handler
        return next_handler

    def handle(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Procesa la validación de restricciones en cadena.

        Ejecuta la validación del handler actual y, si es exitosa,
        pasa el control al siguiente handler en la cadena.

        :param context: Contexto con todos los datos necesarios para la validación
        :return: None si todas las validaciones son exitosas,
                 mensaje de error (str) si alguna validación falla
        """
        try:
            # Validar contexto básico antes de procesar
            context_validation = self._validate_context_structure(context)
            if context_validation is not None:
                return context_validation

            # Ejecutar validación específica del handler
            self._logger.debug(f"Ejecutando validación: {self.__class__.__name__}")
            result = self.validate(context)

            if result is not None:
                # La validación falló, registrar y retornar error
                self._logger.warning(f"Validación fallida en {self.__class__.__name__}: {result}")
                return result

            # Validación exitosa, continuar con el siguiente handler
            self._logger.debug(f"Validación exitosa: {self.__class__.__name__}")
            if self._next_handler:
                return self._next_handler.handle(context)

            return None

        except Exception as e:
            # Capturar errores inesperados y convertirlos en mensajes de error
            error_msg = f"Error interno en {self.__class__.__name__}: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            return error_msg

    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Método abstracto que debe ser implementado por cada handler específico.

        Contiene la lógica de validación específica de cada restricción.

        :param context: Contexto con los datos necesarios para la validación
        :return: None si la validación es exitosa,
                 mensaje de error (str) si la validación falla
        """
        raise NotImplementedError("Debe implementar validate() en las subclases.")

    def _validate_context_structure(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida la estructura básica del contexto antes de procesar.

        Puede ser sobrescrito por handlers específicos que requieran
        validaciones de contexto particulares.

        :param context: Contexto a validar
        :return: None si el contexto es válido, mensaje de error si no lo es
        """
        if not isinstance(context, dict):
            return "El contexto debe ser un diccionario."

        if not context:
            return "El contexto no puede estar vacío."

        return None

    def get_handler_name(self) -> str:
        """
        Retorna el nombre del handler para logging y debugging.

        :return: Nombre de la clase del handler
        """
        return self.__class__.__name__

    def get_chain_info(self) -> List[str]:
        """
        Retorna información sobre toda la cadena de handlers.

        Útil para debugging y para mostrar qué validaciones se ejecutarán.

        :return: Lista con los nombres de todos los handlers en la cadena
        """
        chain = [self.get_handler_name()]
        if self._next_handler:
            chain.extend(self._next_handler.get_chain_info())
        return chain

    def validate_all_and_collect_errors(self, context: Dict[str, Any]) -> List[str]:
        """
        Ejecuta todas las validaciones en la cadena y recolecta TODOS los errores,
        en lugar de detenerse en el primer error.

        Útil para mostrar al usuario todos los problemas de una vez,
        especialmente en el enfoque de generación automática.

        :param context: Contexto con los datos para validación
        :return: Lista de todos los mensajes de error encontrados
        """
        errors = []

        try:
            # Validar contexto básico
            context_validation = self._validate_context_structure(context)
            if context_validation is not None:
                errors.append(context_validation)
                return errors  # Si el contexto es inválido, no continuar

            # Ejecutar validación de este handler
            result = self.validate(context)
            if result is not None:
                errors.append(result)

            # Continuar con el siguiente handler independientemente del resultado
            if self._next_handler:
                next_errors = self._next_handler.validate_all_and_collect_errors(context)
                errors.extend(next_errors)

        except Exception as e:
            error_msg = f"Error interno en {self.__class__.__name__}: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            errors.append(error_msg)

        return errors

    def __str__(self) -> str:
        """
        Representación en string del handler y su cadena.

        :return: String describiendo la cadena de handlers
        """
        chain_info = " -> ".join(self.get_chain_info())
        return f"RestrictionChain: {chain_info}"

    def __repr__(self) -> str:
        """
        Representación técnica del handler.

        :return: String con información técnica del handler
        """
        return f"{self.__class__.__name__}(next_handler={self._next_handler.__class__.__name__ if self._next_handler else None})"