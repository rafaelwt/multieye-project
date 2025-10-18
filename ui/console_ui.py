"""
Módulo de interfaz de consola.

Define la clase ConsoleUI que proporciona la interfaz de usuario en terminal.
"""

from typing import Optional
from application.image_manager import ImageManager
from error import (
    ImageNotFoundError,
    DuplicateImageError,
    ImageManagerError
)
from domain.image import DIAGNOSTICS

VALID_DIAGNOSTICS = list(DIAGNOSTICS.values())


class ConsoleUI:
    """
    Interfaz de usuario en consola para el gestor de imágenes.

    Proporciona un menú interactivo para que el usuario pueda realizar
    operaciones sobre las imágenes médicas.
    """

    def __init__(self):
        """Inicializa la interfaz de consola."""
        self._manager = ImageManager()
        self._running = True

    def run(self) -> None:
        """
        Ejecuta el bucle principal de la interfaz de usuario.

        Muestra el menú y procesa las opciones del usuario hasta que
        decide salir.
        """
        self._show_welcome()

        while self._running:
            self._show_menu()
            option = self._read_option()
            self._process_option(option)

        self._show_goodbye()

    def _show_welcome(self) -> None:
        """Muestra el mensaje de bienvenida."""
        print("\n" + "=" * 60)
        print("  SISTEMA DE GESTIÓN DE IMÁGENES MÉDICAS (MultiEYE)")
        print("  Dataset: MultiEYE - Imágenes de Fondo de Ojo")
        print("=" * 60)

    def _show_goodbye(self) -> None:
        """Muestra el mensaje de despedida."""
        print("\n" + "=" * 60)
        print("  Saliendo del Sistema")
        print("=" * 60 + "\n")

    def _show_menu(self) -> None:
        """Muestra el menú principal de opciones."""
        print("\n" + "-" * 60)
        print("====================== MENÚ PRINCIPAL ======================")
        print("-" * 60)
        print("1. Registrar nueva imagen")
        print("2. Buscar imagen")
        print("3. Modificar imagen")
        print("4. Eliminar imagen")
        print("5. Listar todas las imágenes")
        print("6. Listar imágenes por diagnóstico")
        print("7. Cargar imágenes desde archivo TXT")
        print("0. Salir")
        print("-" * 60)

    def _read_option(self) -> str:
        """
        Lee la opción seleccionada por el usuario.

        Returns:
            str: Opción ingresada por el usuario
        """
        return input("Seleccione una opción: ").strip()

    def _process_option(self, option: str) -> None:
        """
        Procesa la opción seleccionada por el usuario.

        Args:
            option (str): Opción a procesar
        """
        options = {
            "1": self._register_image,
            "2": self._search_image,
            "3": self._update_image,
            "4": self._delete_image,
            "5": self._list_images,
            "6": self._list_by_diagnostic,
            "7": self._load_from_txt,
            "0": self._exit
        }

        action = options.get(option)
        if action:
            try:
                action()
            except (
                ImageNotFoundError,
                DuplicateImageError,
                FileNotFoundError,
                OSError,
                ValueError
            ) as e:
                print(f"\nError: {e}")
        else:
            print("\nOpción inválida. Por favor, seleccione una opción del 1 al 7 o 0 para salir.")

    def _register_image(self) -> None:
        """Registra una nueva imagen en el sistema."""
        print("\n" + "=" * 60)
        print("REGISTRAR NUEVA IMAGEN")
        print("=" * 60)

        try:
            name = input("Nombre de la imagen: ").strip()
            if not name:
                print("El nombre no puede estar vacío")
                return

            class_id = self._read_integer(
                "Clase (0-7): ",
                minimum=0,
                maximum=7
            )
            if class_id is None:
                return

            age = self._read_integer(
                "Edad del paciente: ",
                minimum=0,
                maximum=150
            )
            if age is None:
                return

            image = self._manager.add_image(name, class_id, age)
            print("\nImagen registrada exitosamente:")
            self._show_image(image)

        except DuplicateImageError as e:
            print(f"\n{e}")

    def _search_image(self) -> None:
        """Busca y muestra una imagen por su nombre."""
        print("\n" + "=" * 60)
        print("BUSCAR IMAGEN")
        print("=" * 60)

        name = input("Nombre de la imagen a buscar: ").strip()
        if not name:
            print("El nombre no puede estar vacío")
            return

        image = self._manager.find_image(name)
        if image:
            print("\nImagen encontrada:")
            self._show_image(image)
        else:
            print(f"\nNo se encontró ninguna imagen con el nombre: {name}")

    def _update_image(self) -> None:
        """Modifica los metadatos de una imagen existente."""
        print("\n" + "=" * 60)
        print("MODIFICAR IMAGEN")
        print("=" * 60)

        name = input("Nombre de la imagen a modificar: ").strip()
        if not name:
            print("El nombre no puede estar vacío")
            return

        image = self._manager.find_image(name)
        if not image:
            print(f"\nNo se encontró ninguna imagen con el nombre: {name}")
            return

        print("\nDatos actuales:")
        self._show_image(image)

        print("\nIngrese los nuevos valores (presione Enter para mantener el actual):")

        new_class_id = self._read_optional_integer(
            f"Nueva clase (actual: {image.class_id}): ",
            minimum=0,
            maximum=7
        )

        new_age = self._read_optional_integer(
            f"Nueva edad (actual: {image.age}): ",
            minimum=0,
            maximum=150
        )

        try:
            updated_image = self._manager.update_image(
                name,
                new_class_id=new_class_id,
                new_age=new_age
            )
            print("\nImagen modificada exitosamente:")
            self._show_image(updated_image)

        except ImageNotFoundError as e:
            print(f"\n{e}")

    def _delete_image(self) -> None:
        """Elimina una imagen del sistema."""
        print("\n" + "=" * 60)
        print("ELIMINAR IMAGEN")
        print("=" * 60)

        name = input("Nombre de la imagen a eliminar: ").strip()
        if not name:
            print("El nombre no puede estar vacío")
            return

        image = self._manager.find_image(name)
        if not image:
            print(f"\nNo se encontró ninguna imagen con el nombre: {name}")
            return

        print("\nImagen a eliminar:")
        self._show_image(image)

        confirmation = input("\n¿Está seguro que desea eliminar esta imagen? (s/n): ").strip().lower()
        if confirmation == 's':
            try:
                self._manager.delete_image(name)
                print("\nImagen eliminada exitosamente")
            except ImageNotFoundError as e:
                print(f"\n{e}")
        else:
            print("\nOperación cancelada")

    def _list_images(self) -> None:
        """Lista todas las imágenes registradas."""
        print("\n" + "=" * 60)
        print("LISTADO DE TODAS LAS IMÁGENES")
        print("=" * 60)

        images = self._manager.list_images()
        if not images:
            print("\nNo hay imágenes registradas")
            return

        print(f"\nTotal de imágenes: {len(images)}\n")
        for i, image in enumerate(images, 1):
            print(f"{i}. {image.name}")
            print(f"   Clase: {image.class_id} | Diagnóstico: {image.diagnostic} | Edad: {image.age}")
            print()

    def _list_by_diagnostic(self) -> None:
        """Lista imágenes filtradas por diagnóstico."""
        print("\n" + "=" * 60)
        print("LISTAR IMÁGENES POR DIAGNÓSTICO")
        print("=" * 60)

        print("\nDiagnósticos disponibles:")
        for i, diagnostic in enumerate(VALID_DIAGNOSTICS, 1):
            print(f"{i}. {diagnostic}")

        option = self._read_integer(
            f"\nSeleccione diagnóstico (1-{len(VALID_DIAGNOSTICS)}): ",
            minimum=1,
            maximum=len(VALID_DIAGNOSTICS)
        )
        if option is None:
            return

        diagnostic = VALID_DIAGNOSTICS[option - 1]
        images = self._manager.list_images(diagnostic=diagnostic)

        if not images:
            print(f"\nNo hay imágenes con diagnóstico: {diagnostic}")
            return

        print(f"\nImágenes con diagnóstico '{diagnostic}': {len(images)}\n")
        for i, image in enumerate(images, 1):
            print(f"{i}. {image.name} (Edad: {image.age})")

    def _load_from_txt(self) -> None:
        """Carga imágenes desde un archivo TXT."""
        print("\n" + "=" * 60)
        print("CARGAR IMÁGENES DESDE ARCHIVO TXT")
        print("=" * 60)

        path = input("\nRuta del archivo (ej: large9cls.txt): ").strip()
        if not path:
            print("Debe especificar una ruta")
            return

        try:
            count = self._manager.load_from_txt(path)
            print(f"\nSe cargaron {count} imágenes exitosamente")
        except FileNotFoundError:
            print(f"\nEl archivo no existe: {path}")
        except ImageManagerError as e:
            print(f"\nError al cargar archivo:\n{e}")

    def _exit(self) -> None:
        """Finaliza la ejecución del programa."""
        self._running = False

    def _show_image(self, image) -> None:
        """
        Muestra la información de una imagen.

        Args:
            image: Imagen a mostrar
        """
        print("-" * 40)
        print(f"Nombre:      {image.name}")
        print(f"Clase:       {image.class_id}")
        print(f"Diagnóstico: {image.diagnostic}")
        print(f"Edad:        {image.age} años")
        print("-" * 40)

    def _read_integer(
        self,
        message: str,
        minimum: Optional[int] = None,
        maximum: Optional[int] = None
    ) -> Optional[int]:
        """
        Lee un número entero del usuario con validación.

        Args:
            message (str): Mensaje a mostrar
            minimum (Optional[int]): Valor mínimo permitido
            maximum (Optional[int]): Valor máximo permitido

        Returns:
            Optional[int]: Número ingresado o None si hay error
        """
        try:
            value = int(input(message))
            if minimum is not None and value < minimum:
                print(f"El valor debe ser al menos {minimum}")
                return None
            if maximum is not None and value > maximum:
                print(f"El valor debe ser como máximo {maximum}")
                return None
            return value
        except ValueError:
            print("Debe ingresar un número entero válido")
            return None

    def _read_optional_integer(
        self,
        message: str,
        minimum: Optional[int] = None,
        maximum: Optional[int] = None
    ) -> Optional[int]:
        """
        Lee un número entero opcional (permite Enter para omitir).

        Args:
            message (str): Mensaje a mostrar
            minimum (Optional[int]): Valor mínimo permitido
            maximum (Optional[int]): Valor máximo permitido

        Returns:
            Optional[int]: Número ingresado o None si se omite
        """
        input_str = input(message).strip()
        if not input_str:
            return None

        return self._read_integer_from_string(input_str, minimum, maximum)

    def _read_integer_from_string(
        self,
        input_str: str,
        minimum: Optional[int] = None,
        maximum: Optional[int] = None
    ) -> Optional[int]:
        """
        Convierte una cadena a entero con validación.

        Args:
            input_str (str): Cadena a convertir
            minimum (Optional[int]): Valor mínimo permitido
            maximum (Optional[int]): Valor máximo permitido

        Returns:
            Optional[int]: Número convertido o None si hay error
        """
        try:
            value = int(input_str)
            if minimum is not None and value < minimum:
                print(f"El valor debe ser al menos {minimum}")
                return None
            if maximum is not None and value > maximum:
                print(f"El valor debe ser como máximo {maximum}")
                return None
            return value
        except ValueError:
            print("Debe ingresar un número entero válido")
            return None
