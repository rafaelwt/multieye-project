"""
Módulo de excepciones personalizadas.

Define las excepciones utilizadas en el sistema.
"""


class ImageManagerError(Exception):
    """Excepción base para errores del gestor de imágenes."""


class ImageNotFoundError(ImageManagerError):
    """Excepción lanzada cuando no se encuentra una imagen."""


class DuplicateImageError(ImageManagerError):
    """Excepción lanzada cuando se intenta agregar una imagen duplicada."""
