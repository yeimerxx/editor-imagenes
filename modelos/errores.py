"""Excepciones propias de la aplicación.

Tener excepciones específicas permite que la interfaz muestre mensajes
claros sin depender de los detalles internos de Pillow.
"""


class ErrorEditor(Exception):
    """Clase base de los errores previsibles del editor."""


class ImagenNoCargadaError(ErrorEditor):
    """Se intentó operar sin haber abierto una imagen."""


class ArchivoInvalidoError(ErrorEditor):
    """El archivo no existe o no es una imagen compatible."""


class ParametroInvalidoError(ErrorEditor):
    """Un valor numérico está fuera del rango permitido."""
