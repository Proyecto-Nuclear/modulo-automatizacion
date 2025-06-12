from typing import Dict, Any

class ConfiguradorSistema:
    """Gestiona la configuración del sistema de horarios."""

    def __init__(self):
        """Inicializa el configurador con las configuraciones por defecto."""
        self.default_config = {
            'validar_restricciones': True,
            'crear_con_validacion': True,
            'incluir_metadatos': True,
            'formato_salida': 'dict'
        }

    def configurar(self, **config) -> None:
        """Configura parámetros del sistema."""
        for key, value in config.items():
            if key in self.default_config:
                self.default_config[key] = value

    def obtener_configuracion(self) -> Dict[str, Any]:
        """Obtiene la configuración actual."""
        return self.default_config.copy()