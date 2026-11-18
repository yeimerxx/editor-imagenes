"""Lógica de aplicación del editor, independiente de la interfaz gráfica."""
from __future__ import annotations

from PIL import Image

from modelos.documento_imagen import DocumentoImagen
from modelos.errores import ImagenNoCargadaError, ParametroInvalidoError
from modelos.filtros import Filtro, FiltroConIntensidad


class EditorImagen:
    """Coordina las operaciones sobre la imagen abierta.

    Relaciones:
      * Agregación con ``Filtro``: recibe el catálogo de filtros ya creado;
        los filtros existen aunque el editor desaparezca.
      * Composición con ``DocumentoImagen``: el editor crea y es dueño del
        documento que se abre.
    """

    LADO_MAXIMO = 8000

    def __init__(self, filtros: list[Filtro]) -> None:
        self._filtros = {filtro.nombre: filtro for filtro in filtros}
        self._documento: DocumentoImagen | None = None

    # Consulta -------------------------------------------------------------
    @property
    def nombres_filtros(self) -> list[str]:
        return list(self._filtros)

    @property
    def hay_imagen(self) -> bool:
        return self._documento is not None

    @property
    def puede_deshacer(self) -> bool:
        return self._documento is not None and self._documento.puede_deshacer

    @property
    def tamano(self) -> tuple[int, int]:
        return self._requerir_documento().tamano

    def obtener_filtro(self, nombre: str) -> Filtro:
        try:
            return self._filtros[nombre]
        except KeyError as error:
            raise ParametroInvalidoError(f"El filtro '{nombre}' no existe.") from error

    def imagen_actual(self) -> Image.Image:
        return self._requerir_documento().imagen

    # Operaciones ----------------------------------------------------------
    def abrir(self, ruta: str) -> None:
        self._documento = DocumentoImagen.desde_archivo(ruta)

    def aplicar_filtro(self, nombre: str, intensidad: float | None = None) -> None:
        documento = self._requerir_documento()
        filtro = self.obtener_filtro(nombre)
        if intensidad is not None and isinstance(filtro, FiltroConIntensidad):
            filtro.intensidad = intensidad
        documento.aplicar(filtro.aplicar(documento.imagen))

    def rotar(self, grados: int) -> None:
        documento = self._requerir_documento()
        documento.aplicar(documento.imagen.rotate(-grados, expand=True))

    def voltear(self, horizontal: bool = True) -> None:
        documento = self._requerir_documento()
        modo = Image.Transpose.FLIP_LEFT_RIGHT if horizontal else Image.Transpose.FLIP_TOP_BOTTOM
        documento.aplicar(documento.imagen.transpose(modo))

    def redimensionar(self, ancho: str | int, alto: str | int) -> None:
        documento = self._requerir_documento()
        try:
            ancho, alto = int(ancho), int(alto)
        except (TypeError, ValueError) as error:
            raise ParametroInvalidoError("Ancho y alto deben ser números enteros.") from error
        if not (1 <= ancho <= self.LADO_MAXIMO and 1 <= alto <= self.LADO_MAXIMO):
            raise ParametroInvalidoError(
                f"Ancho y alto deben estar entre 1 y {self.LADO_MAXIMO} píxeles."
            )
        documento.aplicar(documento.imagen.resize((ancho, alto), Image.Resampling.LANCZOS))

    def deshacer(self) -> bool:
        return self._requerir_documento().deshacer()

    def exportar(self, ruta: str) -> None:
        self._requerir_documento().guardar(ruta)

    # Interno --------------------------------------------------------------
    def _requerir_documento(self) -> DocumentoImagen:
        if self._documento is None:
            raise ImagenNoCargadaError("Primero abre una imagen.")
        return self._documento
