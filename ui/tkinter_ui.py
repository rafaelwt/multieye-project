"""
Módulo de interfaz gráfica con Tkinter.

Define la clase TkinterUI que proporciona una interfaz gráfica de usuario.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from application.image_manager import ImageManager
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
        self._root.title("Sistema de Gestión de Imágenes Médicas")
        self._root.geometry("800x600")
        self._setup_interface()

    def run(self) -> None:
        """
        Inicia el bucle principal de la interfaz gráfica.
        """
        self._root.mainloop()

    def _setup_interface(self) -> None:
        """Configura todos los elementos de la interfaz."""
        # Título
        title = tk.Label(
            self._root,
            text="Sistema de Gestión de Imágenes Médicas",
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

        for col in columns:
            self._tree.column(col, width=150)
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
                    image.diagnostic,
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

        # Campos
        ttk.Label(dialog, text="Nombre de la imagen:").pack(pady=5)
        entry_name = ttk.Entry(dialog, width=40)
        entry_name.pack(pady=5)

        ttk.Label(dialog, text="Clase (0-7):").pack(pady=5)
        entry_class = ttk.Entry(dialog, width=40)
        entry_class.pack(pady=5)

        ttk.Label(dialog, text="Edad del paciente:").pack(pady=5)
        entry_age = ttk.Entry(dialog, width=40)
        entry_age.pack(pady=5)

        def save():
            try:
                name = entry_name.get().strip()
                class_id = int(entry_class.get())
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
                    "Clase y edad deben ser números enteros"
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
                    f"Diagnóstico: {image.diagnostic}\n"
                    f"Edad: {image.age} años"
                )
            else:
                messagebox.showwarning(
                    "No Encontrada",
                    f"No se encontró ninguna imagen con el nombre: {name}"
                )

    def _update_image(self) -> None:
        """Modifica una imagen existente."""
        name = simpledialog.askstring(
            "Modificar Imagen",
            "Ingrese el nombre de la imagen a modificar:"
        )

        if not name:
            return

        image = self._manager.find_image(name)
        if not image:
            messagebox.showwarning(
                "No Encontrada",
                f"No se encontró ninguna imagen con el nombre: {name}"
            )
            return

        # Ventana de modificación
        dialog = tk.Toplevel(self._root)
        dialog.title("Modificar Imagen")
        dialog.geometry("400x250")
        dialog.transient(self._root)
        dialog.grab_set()

        ttk.Label(
            dialog,
            text=f"Modificando: {name}",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        ttk.Label(dialog, text=f"Nueva clase (actual: {image.class_id}):").pack(pady=5)
        entry_class = ttk.Entry(dialog, width=40)
        entry_class.pack(pady=5)

        ttk.Label(dialog, text=f"Nueva edad (actual: {image.age}):").pack(pady=5)
        entry_age = ttk.Entry(dialog, width=40)
        entry_age.pack(pady=5)

        def save():
            try:
                new_class_id = None
                new_age = None

                if entry_class.get().strip():
                    new_class_id = int(entry_class.get())

                if entry_age.get().strip():
                    new_age = int(entry_age.get())

                self._manager.update_image(
                    name,
                    new_class_id=new_class_id,
                    new_age=new_age
                )
                messagebox.showinfo(
                    "Éxito",
                    f"Imagen '{name}' modificada exitosamente"
                )
                dialog.destroy()
                self._refresh_list()

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Los valores deben ser números enteros"
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
        name = simpledialog.askstring(
            "Eliminar Imagen",
            "Ingrese el nombre de la imagen a eliminar:"
        )

        if not name:
            return

        image = self._manager.find_image(name)
        if not image:
            messagebox.showwarning(
                "No Encontrada",
                f"No se encontró ninguna imagen con el nombre: {name}"
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar la imagen '{name}'?\n\n"
            f"Clase: {image.class_id}\n"
            f"Diagnóstico: {image.diagnostic}\n"
            f"Edad: {image.age} años"
        )

        if confirm:
            try:
                self._manager.delete_image(name)
                messagebox.showinfo(
                    "Éxito",
                    f"Imagen '{name}' eliminada exitosamente"
                )
                self._refresh_list()
            except ImageNotFoundError as e:
                messagebox.showerror("Error", str(e))

    def _load_from_txt(self) -> None:
        """Carga imágenes desde un archivo TXT."""
        from tkinter import filedialog

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
