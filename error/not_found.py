"""
Módulo de excepción de imagen no encontrada.

Define la excepción lanzada cuando no se encuentra una imagen.
"""

from .base import ImageManagerError


class ImageNotFoundError(ImageManagerError):
    """Excepción lanzada cuando no se encuentra una imagen."""

