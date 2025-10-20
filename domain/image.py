"""
Módulo de entidad Image.

Define la clase Image que representa una imagen médica con sus metadatos.
"""


# Constantes para mapeo de clases a diagnósticos
DIAGNOSTICS = {
    0: {"abbr": "Normal", "name": "Normal"},
    1: {"abbr": "dAMD", "name": "Degeneración macular asociada a la edad (seca)"},
    2: {"abbr": "CSC",  "name": "Corioretinopatía serosa central"},
    3: {"abbr": "DR",   "name": "Retinopatía diabética"},
    4: {"abbr": "GLC",  "name": "Glaucoma"},
    5: {"abbr": "MEM",  "name": "Membrana epirretiniana"},
    6: {"abbr": "RVO",  "name": "Oclusión venosa retiniana"},
    7: {"abbr": "wAMD", "name": "Degeneración macular asociada a la edad (húmeda)"}
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
        diagnostic_info = DIAGNOSTICS.get(class_id, {"abbr": "Desconocido", "name": "Desconocido"})
        self.diagnostic = diagnostic_info["abbr"]
        self.diagnostic_full = diagnostic_info["name"]

    def to_dict(self):
        """Convierte la imagen a diccionario para guardar en CSV."""
        return {
            "name": self.name,
            "class_id": self.class_id,
            "age": self.age,
            "diagnostic": self.diagnostic
        }

    def __str__(self):
        """Representación en texto de la imagen."""
        return f"{self.name} | Clase: {self.class_id} ({self.diagnostic}) | Edad: {self.age}"

