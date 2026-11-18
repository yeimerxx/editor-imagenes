"""Filtros de imagen.

Jerarquía:

    Filtro (abstracta)
    ├── FiltroGrises
    ├── FiltroInvertir
    └── FiltroConIntensidad (abstracta, valida el parámetro)
        ├── FiltroBrillo
        ├── FiltroContraste
        └── FiltroDesenfoque

Todos comparten el método ``aplicar``: el editor trabaja con cualquier
``Filtro`` sin saber de cuál se trata (polimorfismo).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from modelos.errores import ParametroInvalidoError


class Filtro(ABC):
    """Contrato que debe cumplir cualquier filtro del editor."""

    def __init__(self, nombre: str) -> None:
        self._nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def usa_intensidad(self) -> bool:
        """Indica si la interfaz debe mostrar un control de intensidad."""
        return False

    @abstractmethod
    def aplicar(self, imagen: Image.Image) -> Image.Image:
        """Devuelve una imagen nueva; nunca modifica la recibida."""

    def __str__(self) -> str:
        return self._nombre


class FiltroGrises(Filtro):
    def __init__(self) -> None:
        super().__init__("Escala de grises")

    def aplicar(self, imagen: Image.Image) -> Image.Image:
        return ImageOps.grayscale(imagen).convert("RGB")


class FiltroInvertir(Filtro):
    def __init__(self) -> None:
        super().__init__("Invertir colores")

    def aplicar(self, imagen: Image.Image) -> Image.Image:
        return ImageOps.invert(imagen.convert("RGB"))


class FiltroConIntensidad(Filtro):
    """Base de los filtros que reciben un valor numérico validado."""

    def __init__(self, nombre: str, minimo: float, maximo: float, inicial: float) -> None:
        super().__init__(nombre)
        self._minimo = minimo
        self._maximo = maximo
        self._intensidad = inicial
        self.intensidad = inicial  # pasa por la validación del setter

    @property
    def usa_intensidad(self) -> bool:
        return True

    @property
    def minimo(self) -> float:
        return self._minimo

    @property
    def maximo(self) -> float:
        return self._maximo

    @property
    def intensidad(self) -> float:
        return self._intensidad

    @intensidad.setter
    def intensidad(self, valor: float) -> None:
        try:
            valor = float(valor)
        except (TypeError, ValueError) as error:
            raise ParametroInvalidoError("La intensidad debe ser un número.") from error
        if not self._minimo <= valor <= self._maximo:
            raise ParametroInvalidoError(
                f"La intensidad de '{self._nombre}' debe estar entre "
                f"{self._minimo} y {self._maximo}."
            )
        self._intensidad = valor

    @abstractmethod
    def aplicar(self, imagen: Image.Image) -> Image.Image:
        ...


class FiltroBrillo(FiltroConIntensidad):
    def __init__(self) -> None:
        super().__init__("Brillo", 0.2, 3.0, 1.3)

    def aplicar(self, imagen: Image.Image) -> Image.Image:
        return ImageEnhance.Brightness(imagen).enhance(self.intensidad)


class FiltroContraste(FiltroConIntensidad):
    def __init__(self) -> None:
        super().__init__("Contraste", 0.2, 3.0, 1.5)

    def aplicar(self, imagen: Image.Image) -> Image.Image:
        return ImageEnhance.Contrast(imagen).enhance(self.intensidad)


class FiltroDesenfoque(FiltroConIntensidad):
    def __init__(self) -> None:
        super().__init__("Desenfoque", 0.0, 20.0, 3.0)

    def aplicar(self, imagen: Image.Image) -> Image.Image:
        return imagen.filter(ImageFilter.GaussianBlur(self.intensidad))
