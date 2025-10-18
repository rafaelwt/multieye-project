"""
Módulo de excepción de imagen duplicada.

Define la excepción lanzada cuando se intenta agregar una imagen duplicada.
"""

from .base import ImageManagerError


class DuplicateImageError(ImageManagerError):
    """Excepción lanzada cuando se intenta agregar una imagen duplicada."""

