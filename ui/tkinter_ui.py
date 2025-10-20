"""
Módulo de interfaz gráfica con Tkinter.

Define la clase TkinterUI que proporciona una interfaz gráfica de usuario.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Optional
from application.image_manager import ImageManager
from domain.image import Image
from error import (
    ImageNotFoundError,
    DuplicateImageError,
    ImageManagerError
)
from domain.image import DIAGNOSTICS

VALID_DIAGNOSTICS = list(DIAGNOSTICS.values())


class TkinterUI:
    """
    Interfaz gráfica de usuario con Tkinter para el gestor de imágenes.

    Proporciona una ventana con botones y listados para gestionar las imágenes.
    """

    def __init__(self):
        """Inicializa la interfaz gráfica."""
        self._manager = ImageManager()
        self._root = tk.Tk()
        self._root.title("Sistema de Gestión de Imágenes Médicas (MultiEYE)")
        self._root.geometry("900x600")
        self._center_window(self._root)
        self._setup_interface()

    def run(self) -> None:
        """
        Inicia el bucle principal de la interfaz gráfica.
        """
        self._root.mainloop()

    def _center_window(self, window) -> None:
        """
        Centra una ventana en la pantalla.

        Args:
            window: Ventana de Tkinter a centrar
        """
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _get_selected_image(self) -> Optional[Image]:
        """
        Obtiene la imagen seleccionada en la tabla.

        Returns:
            Optional[Image]: Imagen seleccionada o None si no hay selección
        """
        selection = self._tree.selection()
        if not selection:
            return None

        # Obtener el índice del item seleccionado
        item = self._tree.item(selection[0])
        values = item['values']
        if not values:
            return None

        # El primer valor es el nombre de la imagen
        image_name = values[0]
        return self._manager.find_image(image_name)

    def _setup_interface(self) -> None:
        """Configura todos los elementos de la interfaz."""
        # Título
        title = tk.Label(
            self._root,
            text="Sistema de Gestión de Imágenes Médicas (MultiEYE)",
            font=("Arial", 16, "bold"),
            bg="#2196F3",
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        # Frame principal
        main_frame = ttk.Frame(self._root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de botones
        buttons_frame = ttk.LabelFrame(
            main_frame,
            text="Operaciones",
            padding="10"
        )
        buttons_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Botones
        buttons = [
            ("➕ Registrar Imagen", self._register_image),
            ("🔍 Buscar Imagen", self._search_image),
            ("✏️ Modificar Imagen", self._update_image),
            ("🗑️ Eliminar Imagen", self._delete_image),
            ("📁 Cargar desde TXT", self._load_from_txt),
            ("🔄 Actualizar Lista", self._refresh_list),
            ("❌ Salir", self._exit)
        ]

        for text, command in buttons:
            btn = ttk.Button(
                buttons_frame,
                text=text,
                command=command,
                width=20
            )
            btn.pack(pady=5, fill=tk.X)

        # Frame de lista
        list_frame = ttk.LabelFrame(
            main_frame,
            text="Imágenes Registradas",
            padding="10"
        )
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Treeview para mostrar imágenes
        columns = ("Nombre", "Clase", "Diagnóstico", "Edad")
        self._tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="tree headings",
            height=20
        )

        # Configurar columnas
        self._tree.column("#0", width=50)
        self._tree.heading("#0", text="#")
        self._tree.column("Nombre", width=200)
        self._tree.column("Clase", width=80)
        self._tree.column("Diagnóstico", width=300)
        self._tree.column("Edad", width=80)

        for col in columns:
            self._tree.heading(col, text=col)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Cargar datos iniciales
        self._refresh_list()

    def _refresh_list(self) -> None:
        """Actualiza la lista de imágenes en el Treeview."""
        # Limpiar lista
        for item in self._tree.get_children():
            self._tree.delete(item)

        # Cargar imágenes
        images = self._manager.list_images()
        for i, image in enumerate(images, 1):
            self._tree.insert(
                "",
                tk.END,
                text=str(i),
                values=(
                    image.name,
                    image.class_id,
                    f"{image.diagnostic} - {image.diagnostic_full}",
                    image.age
                )
            )

    def _register_image(self) -> None:
        """Registra una nueva imagen."""
        # Crear ventana de diálogo
        dialog = tk.Toplevel(self._root)
        dialog.title("Registrar Nueva Imagen")
        dialog.geometry("400x250")
        dialog.transient(self._root)
        dialog.grab_set()
        self._center_window(dialog)

        # Campos
        ttk.Label(dialog, text="Nombre de la imagen:").pack(pady=5)
        entry_name = ttk.Entry(dialog, width=50)
        entry_name.pack(pady=5)

        ttk.Label(dialog, text="Diagnóstico:").pack(pady=5)
        class_combo = ttk.Combobox(
            dialog,
            width=50,
            state="readonly",
            values=[f"{k}: {v['abbr']} - {v['name']}" for k, v in DIAGNOSTICS.items()]
        )
        class_combo.pack(pady=5)

        ttk.Label(dialog, text="Edad del paciente:").pack(pady=5)
        entry_age = ttk.Entry(dialog, width=50)
        entry_age.pack(pady=5)

        def save():
            try:
                name = entry_name.get().strip()
                if not name:
                    messagebox.showerror("Error", "El nombre no puede estar vacío")
                    return

                class_selection = class_combo.get()
                if not class_selection:
                    messagebox.showerror("Error", "Debe seleccionar un diagnóstico")
                    return

                # Extraer el class_id del formato "0: Normal - Normal"
                class_id = int(class_selection.split(":")[0])
                age = int(entry_age.get())

                self._manager.add_image(name, class_id, age)
                messagebox.showinfo(
                    "Éxito",
                    f"Imagen '{name}' registrada exitosamente"
                )
                dialog.destroy()
                self._refresh_list()

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "La edad debe ser un número entero"
                )
            except DuplicateImageError as e:
                messagebox.showerror("Error", str(e))

        # Botones
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(pady=20)

        ttk.Button(
            buttons_frame,
            text="Guardar",
            command=save
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame,
            text="Cancelar",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _search_image(self) -> None:
        """Busca una imagen por nombre."""
        name = simpledialog.askstring(
            "Buscar Imagen",
            "Ingrese el nombre de la imagen:"
        )

        if name:
            image = self._manager.find_image(name)
            if image:
                messagebox.showinfo(
                    "Imagen Encontrada",
                    f"Nombre: {image.name}\n"
                    f"Clase: {image.class_id}\n"
                    f"Diagnóstico: {image.diagnostic} - {image.diagnostic_full}\n"
                    f"Edad: {image.age} años"
                )
            else:
                messagebox.showwarning(
                    "No Encontrada",
                    f"No se encontró ninguna imagen con el nombre: {name}"
                )

    def _update_image(self) -> None:
        """Modifica una imagen existente."""
        image = self._get_selected_image()

        if not image:
            messagebox.showwarning(
                "Selección Requerida",
                "Debe seleccionar una imagen de la tabla para modificar."
            )
            return

        # Ventana de modificación
        dialog = tk.Toplevel(self._root)
        dialog.title("Modificar Imagen")
        dialog.geometry("400x250")
        dialog.transient(self._root)
        dialog.grab_set()
        self._center_window(dialog)

        ttk.Label(
            dialog,
            text=f"Imagen: {image.name}",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        ttk.Label(dialog, text=f"Nueva clase (actual: {image.class_id} - {image.diagnostic}):").pack(pady=5)
        class_combo = ttk.Combobox(
            dialog,
            width=50,
            state="readonly",
            values=[f"{k}: {v['abbr']} - {v['name']}" for k, v in DIAGNOSTICS.items()]
        )
        class_combo.pack(pady=5)

        ttk.Label(dialog, text=f"Nueva edad (actual: {image.age}):").pack(pady=5)
        entry_age = ttk.Entry(dialog, width=50)
        entry_age.pack(pady=5)

        def save():
            try:
                new_class_id = None
                new_age = None

                class_selection = class_combo.get()
                if class_selection:
                    # Extraer el class_id del formato "0: Normal"
                    new_class_id = int(class_selection.split(":")[0])

                if entry_age.get().strip():
                    new_age = int(entry_age.get())

                self._manager.update_image(
                    image.name,
                    new_class_id=new_class_id,
                    new_age=new_age
                )
                messagebox.showinfo(
                    "Éxito",
                    f"Imagen '{image.name}' modificada exitosamente"
                )
                dialog.destroy()
                self._refresh_list()

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "La edad debe ser un número entero"
                )
            except ImageNotFoundError as e:
                messagebox.showerror("Error", str(e))

        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(pady=20)

        ttk.Button(
            buttons_frame,
            text="Guardar",
            command=save
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame,
            text="Cancelar",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _delete_image(self) -> None:
        """Elimina una imagen del sistema."""
        image = self._get_selected_image()

        if not image:
            messagebox.showwarning(
                "Selección Requerida",
                "Debe seleccionar una imagen de la tabla para eliminar."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar la imagen '{image.name}'?\n\n"
            f"Clase: {image.class_id}\n"
            f"Diagnóstico: {image.diagnostic} - {image.diagnostic_full}\n"
            f"Edad: {image.age} años"
        )

        if confirm:
            try:
                self._manager.delete_image(image.name)
                messagebox.showinfo(
                    "Éxito",
                    f"Imagen '{image.name}' eliminada exitosamente"
                )
                self._refresh_list()
            except ImageNotFoundError as e:
                messagebox.showerror("Error", str(e))

    def _load_from_txt(self) -> None:
        """Carga imágenes desde un archivo TXT."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )

        if file_path:
            try:
                count = self._manager.load_from_txt(file_path)
                messagebox.showinfo(
                    "Éxito",
                    f"Se cargaron {count} imágenes exitosamente"
                )
                self._refresh_list()
            except FileNotFoundError:
                messagebox.showerror(
                    "Error",
                    f"El archivo no existe: {file_path}"
                )
            except ImageManagerError as e:
                messagebox.showerror("Error al Cargar", str(e))

    def _exit(self) -> None:
        """Cierra la aplicación."""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir?"):
            self._root.quit()
