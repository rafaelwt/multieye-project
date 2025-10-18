"""
Paquete de excepciones personalizadas.

Define las excepciones utilizadas en el sistema de gestión de imágenes.
"""

from .base import ImageManagerError
from .not_found import ImageNotFoundError
from .duplicate import DuplicateImageError

__all__ = [
    "ImageManagerError",
    "ImageNotFoundError",
    "DuplicateImageError"
]

