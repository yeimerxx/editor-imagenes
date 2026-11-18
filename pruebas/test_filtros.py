import pytest
from PIL import Image

from modelos.errores import ParametroInvalidoError
from modelos.filtros import (
    Filtro, FiltroBrillo, FiltroConIntensidad, FiltroContraste,
    FiltroDesenfoque, FiltroGrises, FiltroInvertir,
)

TODOS = [FiltroGrises, FiltroInvertir, FiltroBrillo, FiltroContraste, FiltroDesenfoque]


def imagen_color():
    return Image.new("RGB", (20, 10), (200, 50, 100))


def test_filtro_abstracto_no_se_puede_instanciar():
    with pytest.raises(TypeError):
        Filtro("x")
    with pytest.raises(TypeError):
        FiltroConIntensidad("x", 0, 1, 0.5)


@pytest.mark.parametrize("clase", TODOS)
def test_polimorfismo_todos_devuelven_imagen_nueva(clase):
    original = imagen_color()
    resultado = clase().aplicar(original)
    assert isinstance(resultado, Image.Image)
    assert resultado is not original
    assert resultado.size == original.size


def test_grises_iguala_canales():
    r, g, b = FiltroGrises().aplicar(imagen_color()).getpixel((0, 0))
    assert r == g == b


def test_invertir():
    assert FiltroInvertir().aplicar(imagen_color()).getpixel((0, 0)) == (55, 205, 155)


def test_brillo_aumenta_y_reduce():
    f = FiltroBrillo()
    base = imagen_color().getpixel((0, 0))[0]
    f.intensidad = 0.5
    assert f.aplicar(imagen_color()).getpixel((0, 0))[0] < base


@pytest.mark.parametrize("valor", [-1, 99, "abc", None])
def test_intensidad_invalida(valor):
    with pytest.raises(ParametroInvalidoError):
        FiltroDesenfoque().intensidad = valor


def test_intensidad_valida_se_guarda():
    f = FiltroContraste()
    f.intensidad = "2.0"
    assert f.intensidad == 2.0
