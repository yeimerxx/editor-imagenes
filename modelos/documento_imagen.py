"""Modelo que representa la imagen que se está editando."""
from __future__ import annotations

from PIL import Image

from modelos.errores import ArchivoInvalidoError


class DocumentoImagen:
    """Imagen abierta junto con su historial de cambios (deshacer).

    Encapsula la imagen de Pillow: el exterior solo puede leerla mediante
    propiedades que devuelven copias, y solo se modifica a través de
    ``aplicar`` y ``deshacer``, que mantienen el historial coherente.
    """

    LIMITE_HISTORIAL = 20

    def __init__(self, imagen: Image.Image, ruta_origen: str = "") -> None:
        self._imagen = imagen.convert("RGB")
        self._ruta_origen = ruta_origen
        self._historial: list[Image.Image] = []

    @classmethod
    def desde_archivo(cls, ruta: str) -> "DocumentoImagen":
        try:
            with Image.open(ruta) as img:
                img.load()
                return cls(img.copy(), ruta)
        except (FileNotFoundError, OSError) as error:
            raise ArchivoInvalidoError(
                f"No se pudo abrir '{ruta}' como imagen."
            ) from error

    @property
    def imagen(self) -> Image.Image:
        """Copia de la imagen actual (la original queda protegida)."""
        return self._imagen.copy()

    @property
    def tamano(self) -> tuple[int, int]:
        return self._imagen.size

    @property
    def ruta_origen(self) -> str:
        return self._ruta_origen

    @property
    def puede_deshacer(self) -> bool:
        return bool(self._historial)

    def aplicar(self, nueva_imagen: Image.Image) -> None:
        """Reemplaza la imagen actual guardando la anterior en el historial."""
        self._historial.append(self._imagen)
        if len(self._historial) > self.LIMITE_HISTORIAL:
            self._historial.pop(0)
        self._imagen = nueva_imagen.convert("RGB")

    def deshacer(self) -> bool:
        """Restaura el estado anterior. Devuelve False si no hay nada que deshacer."""
        if not self._historial:
            return False
        self._imagen = self._historial.pop()
        return True

    def guardar(self, ruta: str) -> None:
        try:
            self._imagen.save(ruta)
        except (OSError, ValueError, KeyError) as error:
            raise ArchivoInvalidoError(
                f"No se pudo guardar en '{ruta}'. Usa una extensión como .png o .jpg."
            ) from error
