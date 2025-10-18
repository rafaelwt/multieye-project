"""
Módulo de persistencia CSV.

Guarda y carga imágenes en formato CSV.
"""

import csv
from pathlib import Path
from typing import List
from domain.image import Image


class CsvRepository:
    """Guarda imágenes en formato CSV."""

    def __init__(self, file_path: str = "storage/image_data.csv"):
        """
        Inicializa el repositorio CSV.

        Args:
            file_path: Ruta del archivo CSV (por defecto en storage/)
        """
        self.file_path = Path(file_path)
        # Asegurar que el directorio existe
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, images: List[Image]) -> None:
        """Guarda las imágenes en CSV."""
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'class_id', 'age', 'diagnostic'])
            writer.writeheader()
            for image in images:
                writer.writerow(image.to_dict())

    def load(self) -> List[Image]:
        """Carga las imágenes desde CSV."""
        if not self.file_path.exists():
            return []

        try:
            images = []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    image = Image(
                        name=row['name'],
                        class_id=int(row['class_id']),
                        age=int(row['age'])
                    )
                    images.append(image)

            return images
        except (OSError, KeyError, ValueError) as e:
            print(f"Error al cargar CSV: {e}")
            return []

