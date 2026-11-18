"""Punto de entrada: arma los objetos y lanza la interfaz."""
from modelos.filtros import (
    FiltroBrillo, FiltroContraste, FiltroDesenfoque, FiltroGrises, FiltroInvertir,
)
from servicios.editor_imagen import EditorImagen
from interfaz.ventana_principal import VentanaPrincipal


def main() -> None:
    filtros = [FiltroGrises(), FiltroInvertir(), FiltroBrillo(), FiltroContraste(), FiltroDesenfoque()]
    editor = EditorImagen(filtros)
    VentanaPrincipal(editor).mainloop()


if __name__ == "__main__":
    main()
