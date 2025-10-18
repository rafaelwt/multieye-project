"""
Módulo de entidad Image.

Define la clase Image que representa una imagen médica con sus metadatos.
"""


# Constantes para mapeo de clases a diagnósticos
DIAGNOSTICS = {
    0: "Normal",
    1: "dAMD",
    2: "CSC",
    3: "DR",
    4: "GLC",
    5: "MEM",
    6: "RVO",
    7: "wAMD"
}


class Image:
    """
    Representa una imagen médica de fondo de ojo.

    Attributes:
        name (str): Nombre del archivo de imagen
        class_id (int): Clase numérica de la condición (0-7)
        age (int): Edad del paciente
        diagnostic (str): Diagnóstico descriptivo
    """

    def __init__(self, name: str, class_id: int, age: int):
        """
        Crea una nueva imagen médica.

        Args:
            name: Nombre del archivo de imagen
            class_id: Clase numérica (0-7)
            age: Edad del paciente
        """
        self.name = name
        self.class_id = class_id
        self.age = age
        self.diagnostic = DIAGNOSTICS.get(class_id, "Desconocido")

    def to_dict(self):
        """Convierte la imagen a diccionario para guardar en CSV."""
        return {
            "name": self.name,
            "class_id": self.class_id,
            "age": self.age,
            "diagnostic": self.diagnostic
        }

    def __str__(self):
        """Imprime la representación en cadena de la imagen."""
        return f"{self.name} | Clase: {self.class_id} ({self.diagnostic}) | Edad: {self.age}"

