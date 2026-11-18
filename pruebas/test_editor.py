import pytest
from PIL import Image

from modelos.errores import ArchivoInvalidoError, ImagenNoCargadaError, ParametroInvalidoError
from modelos.filtros import FiltroBrillo, FiltroGrises
from servicios.editor_imagen import EditorImagen


@pytest.fixture
def ruta_png(tmp_path):
    ruta = tmp_path / "base.png"
    Image.new("RGB", (40, 20), (10, 120, 200)).save(ruta)
    return str(ruta)


@pytest.fixture
def editor(ruta_png):
    e = EditorImagen([FiltroGrises(), FiltroBrillo()])
    e.abrir(ruta_png)
    return e


def test_sin_imagen_lanza_error():
    e = EditorImagen([FiltroGrises()])
    assert not e.hay_imagen
    with pytest.raises(ImagenNoCargadaError):
        e.rotar(90)


def test_abrir_archivo_inexistente():
    with pytest.raises(ArchivoInvalidoError):
        EditorImagen([]).abrir("no_existe.png")


def test_abrir_archivo_que_no_es_imagen(tmp_path):
    texto = tmp_path / "nota.txt"
    texto.write_text("hola")
    with pytest.raises(ArchivoInvalidoError):
        EditorImagen([]).abrir(str(texto))


def test_aplicar_filtro_y_deshacer(editor):
    antes = editor.imagen_actual().getpixel((0, 0))
    editor.aplicar_filtro("Escala de grises")
    assert editor.imagen_actual().getpixel((0, 0)) != antes
    assert editor.puede_deshacer
    assert editor.deshacer()
    assert editor.imagen_actual().getpixel((0, 0)) == antes
    assert not editor.deshacer()


def test_filtro_inexistente(editor):
    with pytest.raises(ParametroInvalidoError):
        editor.aplicar_filtro("Inventado")


def test_intensidad_fuera_de_rango_no_cambia_imagen(editor):
    with pytest.raises(ParametroInvalidoError):
        editor.aplicar_filtro("Brillo", 50)
    assert not editor.puede_deshacer


def test_rotar_intercambia_dimensiones(editor):
    editor.rotar(90)
    assert editor.tamano == (20, 40)


def test_voltear_conserva_tamano(editor):
    editor.voltear(True)
    editor.voltear(False)
    assert editor.tamano == (40, 20)


def test_redimensionar(editor):
    editor.redimensionar("100", "50")
    assert editor.tamano == (100, 50)


@pytest.mark.parametrize("ancho,alto", [("abc", "10"), ("0", "10"), ("-5", "5"), ("99999", "10"), ("", "")])
def test_redimensionar_invalido(editor, ancho, alto):
    with pytest.raises(ParametroInvalidoError):
        editor.redimensionar(ancho, alto)
    assert editor.tamano == (40, 20)


def test_exportar_png(editor, tmp_path):
    destino = tmp_path / "salida.png"
    editor.exportar(str(destino))
    assert Image.open(destino).size == (40, 20)


def test_exportar_extension_desconocida(editor, tmp_path):
    with pytest.raises(ArchivoInvalidoError):
        editor.exportar(str(tmp_path / "salida.xyz"))


def test_imagen_actual_es_copia(editor):
    editor.imagen_actual().putpixel((0, 0), (1, 2, 3))
    assert editor.imagen_actual().getpixel((0, 0)) != (1, 2, 3)
