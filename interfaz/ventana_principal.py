"""Interfaz gráfica (Tkinter). Solo presenta datos y delega en EditorImagen."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from modelos.errores import ErrorEditor
from servicios.editor_imagen import EditorImagen
from modelos.filtros import FiltroConIntensidad

TIPOS_IMAGEN = [("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"), ("Todos", "*.*")]


class VentanaPrincipal(tk.Tk):
    """Ventana principal. Tiene un ``EditorImagen`` (asociación)."""

    def __init__(self, editor: EditorImagen) -> None:
        super().__init__()
        self._editor = editor
        self._foto: ImageTk.PhotoImage | None = None  # evita que Tk la recicle

        self.title("Editor de Imágenes POO")
        self.geometry("980x640")
        self.minsize(760, 520)

        self._var_filtro = tk.StringVar(value=editor.nombres_filtros[0])
        self._var_intensidad = tk.DoubleVar(value=1.0)
        self._var_ancho = tk.StringVar()
        self._var_alto = tk.StringVar()
        self._var_estado = tk.StringVar(value="Abre una imagen para comenzar.")

        self._construir_widgets()
        self._al_cambiar_filtro()
        self._actualizar_controles()
        self.bind("<Control-z>", lambda _e: self._deshacer())
        self.bind("<Control-o>", lambda _e: self._abrir())
        self.bind("<Control-s>", lambda _e: self._exportar())

    # Construcción ---------------------------------------------------------
    def _construir_widgets(self) -> None:
        panel = ttk.Frame(self, padding=10)
        panel.pack(side=tk.LEFT, fill=tk.Y)

        archivo = ttk.LabelFrame(panel, text="Archivo", padding=8)
        archivo.pack(fill=tk.X, pady=(0, 8))
        self._btn_abrir = ttk.Button(archivo, text="Abrir…", command=self._abrir)
        self._btn_exportar = ttk.Button(archivo, text="Exportar…", command=self._exportar)
        self._btn_deshacer = ttk.Button(archivo, text="Deshacer", command=self._deshacer)
        for boton in (self._btn_abrir, self._btn_exportar, self._btn_deshacer):
            boton.pack(fill=tk.X, pady=2)

        filtros = ttk.LabelFrame(panel, text="Filtros", padding=8)
        filtros.pack(fill=tk.X, pady=(0, 8))
        self._combo = ttk.Combobox(
            filtros, textvariable=self._var_filtro,
            values=self._editor.nombres_filtros, state="readonly",
        )
        self._combo.pack(fill=tk.X)
        self._combo.bind("<<ComboboxSelected>>", lambda _e: self._al_cambiar_filtro())
        self._lbl_intensidad = ttk.Label(filtros, text="Intensidad")
        self._lbl_intensidad.pack(anchor=tk.W, pady=(8, 0))
        self._escala = ttk.Scale(filtros, variable=self._var_intensidad, from_=0, to=1)
        self._escala.pack(fill=tk.X)
        self._lbl_valor = ttk.Label(filtros, text="")
        self._lbl_valor.pack(anchor=tk.E)
        self._var_intensidad.trace_add("write", lambda *_: self._mostrar_valor())
        self._btn_filtro = ttk.Button(filtros, text="Aplicar filtro", command=self._aplicar_filtro)
        self._btn_filtro.pack(fill=tk.X, pady=(6, 0))

        transformar = ttk.LabelFrame(panel, text="Transformar", padding=8)
        transformar.pack(fill=tk.X, pady=(0, 8))
        fila = ttk.Frame(transformar)
        fila.pack(fill=tk.X)
        self._btn_transformar = [
            ttk.Button(fila, text="⟲ 90°", width=8, command=lambda: self._ejecutar(lambda: self._editor.rotar(-90))),
            ttk.Button(fila, text="⟳ 90°", width=8, command=lambda: self._ejecutar(lambda: self._editor.rotar(90))),
        ]
        self._btn_transformar[0].pack(side=tk.LEFT, padx=(0, 4))
        self._btn_transformar[1].pack(side=tk.LEFT)
        fila2 = ttk.Frame(transformar)
        fila2.pack(fill=tk.X, pady=4)
        self._btn_transformar += [
            ttk.Button(fila2, text="↔ Voltear", width=8, command=lambda: self._ejecutar(lambda: self._editor.voltear(True))),
            ttk.Button(fila2, text="↕ Voltear", width=8, command=lambda: self._ejecutar(lambda: self._editor.voltear(False))),
        ]
        self._btn_transformar[2].pack(side=tk.LEFT, padx=(0, 4))
        self._btn_transformar[3].pack(side=tk.LEFT)

        tamano = ttk.LabelFrame(panel, text="Tamaño (px)", padding=8)
        tamano.pack(fill=tk.X)
        ttk.Label(tamano, text="Ancho").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(tamano, textvariable=self._var_ancho, width=8).grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(tamano, text="Alto").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(tamano, textvariable=self._var_alto, width=8).grid(row=1, column=1, padx=4, pady=2)
        self._btn_tamano = ttk.Button(tamano, text="Redimensionar", command=self._redimensionar)
        self._btn_tamano.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=(6, 0))

        derecha = ttk.Frame(self)
        derecha.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._lienzo = tk.Canvas(derecha, background="#2b2b2b", highlightthickness=0)
        self._lienzo.pack(fill=tk.BOTH, expand=True)
        self._lienzo.bind("<Configure>", lambda _e: self._dibujar())
        ttk.Label(derecha, textvariable=self._var_estado, anchor=tk.W, padding=(8, 4)).pack(fill=tk.X)

    # Callbacks ------------------------------------------------------------
    def _abrir(self) -> None:
        ruta = filedialog.askopenfilename(title="Abrir imagen", filetypes=TIPOS_IMAGEN)
        if ruta:
            self._ejecutar(lambda: self._editor.abrir(ruta), f"Abierta: {ruta}")

    def _exportar(self) -> None:
        if not self._editor.hay_imagen:
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar imagen", defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")],
        )
        if ruta:
            self._ejecutar(lambda: self._editor.exportar(ruta), f"Exportada en: {ruta}")

    def _deshacer(self) -> None:
        if self._editor.puede_deshacer:
            self._ejecutar(self._editor.deshacer, "Cambio deshecho.")

    def _aplicar_filtro(self) -> None:
        nombre = self._var_filtro.get()
        filtro = self._editor.obtener_filtro(nombre)
        valor = self._var_intensidad.get() if filtro.usa_intensidad else None
        self._ejecutar(lambda: self._editor.aplicar_filtro(nombre, valor), f"Filtro aplicado: {nombre}")

    def _redimensionar(self) -> None:
        self._ejecutar(
            lambda: self._editor.redimensionar(self._var_ancho.get(), self._var_alto.get()),
            "Imagen redimensionada.",
        )

    def _al_cambiar_filtro(self) -> None:
        filtro = self._editor.obtener_filtro(self._var_filtro.get())
        if isinstance(filtro, FiltroConIntensidad):
            self._escala.configure(from_=filtro.minimo, to=filtro.maximo, state="normal")
            self._var_intensidad.set(filtro.intensidad)
            self._lbl_intensidad.configure(text="Intensidad")
        else:
            self._escala.configure(state="disabled")
            self._lbl_intensidad.configure(text="Este filtro no tiene intensidad")
            self._lbl_valor.configure(text="")
        self._mostrar_valor()

    def _mostrar_valor(self) -> None:
        if self._editor.obtener_filtro(self._var_filtro.get()).usa_intensidad:
            self._lbl_valor.configure(text=f"{self._var_intensidad.get():.2f}")

    # Apoyo ----------------------------------------------------------------
    def _ejecutar(self, accion, mensaje: str | None = None) -> None:
        """Ejecuta una operación del editor y traduce los errores en avisos."""
        try:
            accion()
        except ErrorEditor as error:
            messagebox.showwarning("No se pudo completar", str(error), parent=self)
            self._var_estado.set(str(error))
            return
        if mensaje:
            self._var_estado.set(mensaje)
        self._actualizar_vista()

    def _actualizar_vista(self) -> None:
        if self._editor.hay_imagen:
            ancho, alto = self._editor.tamano
            self._var_ancho.set(str(ancho))
            self._var_alto.set(str(alto))
        self._dibujar()
        self._actualizar_controles()

    def _actualizar_controles(self) -> None:
        estado = "normal" if self._editor.hay_imagen else "disabled"
        for boton in [self._btn_exportar, self._btn_filtro, self._btn_tamano, *self._btn_transformar]:
            boton.configure(state=estado)
        self._btn_deshacer.configure(state="normal" if self._editor.puede_deshacer else "disabled")

    def _dibujar(self) -> None:
        self._lienzo.delete("all")
        if not self._editor.hay_imagen:
            return
        ancho_l = max(self._lienzo.winfo_width(), 50)
        alto_l = max(self._lienzo.winfo_height(), 50)
        vista = self._editor.imagen_actual()
        vista.thumbnail((ancho_l - 20, alto_l - 20), Image.Resampling.LANCZOS)
        self._foto = ImageTk.PhotoImage(vista)
        self._lienzo.create_image(ancho_l // 2, alto_l // 2, image=self._foto)
