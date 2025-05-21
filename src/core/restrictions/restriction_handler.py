"""
Clase base para todos los controladores de restricciones.
"""

from typing import Optional, Dict, Any

class RestrictionHandler:
    def __init__(self, next_handler: Optional['RestrictionHandler'] = None):
        self._next_handler = next_handler

    def set_next(self, next_handler: 'RestrictionHandler') -> 'RestrictionHandler':
        self._next_handler = next_handler
        return next_handler

    def handle(self, context: Dict[str, Any]) -> Optional[str]:
        result = self.validate(context)
        if result is not None:
            return result
        if self._next_handler:
            return self._next_handler.handle(context)
        return None

    def validate(self, context: Dict[str, Any]) -> Optional[str]:
        raise NotImplementedError("You must implement validate() in subclasses.")