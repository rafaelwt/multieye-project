"""
Módulo de gestión de imágenes.

Define la clase ImageManager que maneja las operaciones CRUD sobre imágenes.
"""

from pathlib import Path
from typing import List, Optional
from domain.image import Image, DIAGNOSTICS
from error import (
    ImageManagerError,
    ImageNotFoundError,
    DuplicateImageError
)
from infrastructure.csv_repository import CsvRepository


class ImageManager:
    """
    Gestiona el registro, modificación y eliminación de imágenes médicas.

    Los datos se guardan en formato CSV usando la biblioteca estándar.
    """

    def __init__(self, csv_file: str = "image_data.csv"):
        """
        Inicializa el gestor de imágenes.

        Args:
            csv_file: Nombre del archivo CSV para guardar los datos
        """
        self._images: List[Image] = []
        self._repository = CsvRepository(csv_file)
        self._load_data()

    @property
    def images(self) -> List[Image]:
        """Obtiene la lista de imágenes."""
        return self._images.copy()

    def add_image(
        self,
        name: str,
        class_id: int,
        age: int
    ) -> Image:
        """
        Agrega una nueva imagen al sistema.

        Args:
            name (str): Nombre del archivo de imagen
            class_id (int): Clase numérica (0-7) de la condición
            age (int): Edad del paciente

        Returns:
            Image: La imagen creada y agregada

        Raises:
            DuplicateImageError: Si ya existe una imagen con ese nombre
        """
        if self._image_exists(name):
            raise DuplicateImageError(
                f"Ya existe una imagen con el nombre: {name}"
            )

        image = Image(name, class_id, age)
        self._images.append(image)
        self._save_data()

        return image

    def find_image(self, name: str) -> Optional[Image]:
        """
        Busca una imagen por su nombre.

        Args:
            name (str): Nombre de la imagen a buscar

        Returns:
            Optional[Image]: La imagen encontrada o None si no existe
        """
        for image in self._images:
            if image.name == name:
                return image
        return None

    def update_image(
        self,
        name: str,
        new_class_id: Optional[int] = None,
        new_age: Optional[int] = None,
        new_diagnostic: Optional[str] = None
    ) -> Image:
        """
        Modifica los metadatos de una imagen existente.

        Args:
            name (str): Nombre de la imagen a modificar
            new_class_id (Optional[int]): Nueva clase (si se proporciona)
            new_age (Optional[int]): Nueva edad (si se proporciona)
            new_diagnostic (Optional[str]): Nuevo diagnóstico (si se proporciona)

        Returns:
            Image: La imagen modificada

        Raises:
            ImageNotFoundError: Si la imagen no existe
        """
        image = self.find_image(name)
        if image is None:
            raise ImageNotFoundError(
                f"No se encontró la imagen con nombre: {name}"
            )

        if new_class_id is not None:
            image.class_id = new_class_id
            image.diagnostic = DIAGNOSTICS.get(new_class_id, "Desconocido")

        if new_age is not None:
            image.age = new_age

        if new_diagnostic is not None:
            image.diagnostic = new_diagnostic

        self._save_data()
        return image

    def delete_image(self, name: str) -> bool:
        """
        Elimina una imagen del sistema.

        Args:
            name (str): Nombre de la imagen a eliminar

        Returns:
            bool: True si se eliminó, False si no se encontró

        Raises:
            ImageNotFoundError: Si la imagen no existe
        """
        image = self.find_image(name)
        if image is None:
            raise ImageNotFoundError(
                f"No se encontró la imagen con nombre: {name}"
            )

        self._images.remove(image)
        self._save_data()
        return True

    def list_images(
        self,
        diagnostic: Optional[str] = None,
        class_id: Optional[int] = None
    ) -> List[Image]:
        """
        Lista todas las imágenes, opcionalmente filtradas.

        Args:
            diagnostic (Optional[str]): Filtrar por diagnóstico
            class_id (Optional[int]): Filtrar por clase

        Returns:
            List[Image]: Lista de imágenes (filtradas si se especifica)
        """
        result = self._images.copy()

        if diagnostic is not None:
            result = [
                img for img in result
                if img.diagnostic == diagnostic
            ]

        if class_id is not None:
            result = [
                img for img in result
                if img.class_id == class_id
            ]

        return result

    def load_from_txt(self, txt_file: str) -> int:
        """
        Carga imágenes desde un archivo de texto tipo large9cls.txt.

        El formato esperado es: nombre_imagen clase
        Por ejemplo: 1ffa9600-8d87-11e8-9daf-6045cb817f5b.jpg 7

        Args:
            txt_file (str): Ruta al archivo de texto

        Returns:
            int: Número de imágenes cargadas

        Raises:
            FileNotFoundError: Si el archivo no existe
            ImageManagerError: Si hay errores en el formato
        """
        path = Path(txt_file)
        if not path.exists():
            raise FileNotFoundError(f"El archivo no existe: {txt_file}")

        counter = 0
        errors = []

        with open(path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    parts = line.split()
                    if len(parts) < 2:
                        errors.append(
                            f"Línea {line_number}: formato inválido"
                        )
                        continue

                    name = parts[0]
                    class_id = int(parts[1])

                    if not self._image_exists(name):
                        age = 0
                        self.add_image(name, class_id, age)
                        counter += 1

                except ValueError as e:
                    errors.append(f"Línea {line_number}: {str(e)}")
                    continue

        if errors:
            error_message = "\n".join(errors[:10])
            if len(errors) > 10:
                error_message += f"\n... y {len(errors) - 10} errores más"
            raise ImageManagerError(
                f"Se encontraron {len(errors)} errores al cargar:\n"
                f"{error_message}"
            )

        return counter

    def _image_exists(self, name: str) -> bool:
        """
        Verifica si existe una imagen con el nombre dado.

        Args:
            name (str): Nombre a verificar

        Returns:
            bool: True si existe, False en caso contrario
        """
        return self.find_image(name) is not None

    def _load_data(self) -> None:
        """Carga los datos desde el repositorio."""
        self._images = self._repository.load()

    def _save_data(self) -> None:
        """
        Guarda los datos en el repositorio.

        Raises:
            ImageManagerError: Si hay error al guardar
        """
        try:
            self._repository.save(self._images)
        except Exception as e:
            raise ImageManagerError(f"Error al guardar los datos: {e}") from e

    def __len__(self) -> int:
        """
        Obtiene el número de imágenes gestionadas.

        Returns:
            int: Cantidad de imágenes
        """
        return len(self._images)
