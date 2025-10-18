"""
Punto de entrada principal del sistema de gestión de imágenes médicas.

Permite seleccionar entre interfaz de consola o gráfica (Tkinter).
"""

from ui.console_ui import ConsoleUI
from ui.tkinter_ui import TkinterUI


def select_ui():
    """
    Permite al usuario seleccionar la interfaz de usuario.

    Returns:
        class: La clase de interfaz seleccionada
    """
    print("\n" + "=" * 60)
    print("  SISTEMA DE GESTIÓN DE IMÁGENES MÉDICAS (MultiEYE)")
    print("=" * 60)
    print("\nSelecciona el modo de interfaz:")
    print("1. Consola (Terminal)")
    print("2. Gráfico (Tkinter)")
    print("-" * 60)
    option = input("Seleccione opción (1-2): ").strip()

    if option == "1":
        return ConsoleUI
    elif option == "2":
        return TkinterUI
    else:
        print("\nOpción inválida, usando Consola por defecto...")
        return ConsoleUI


def main():
    """
    Función principal que inicia el sistema.

    Permite seleccionar la interfaz y la ejecuta.
    """
    try:
        # Seleccionar interfaz
        ui_class = select_ui()

        # Crear instancia y ejecutar
        ui = ui_class()
        ui.run()

    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario")
    except Exception as e:
        print(f"\nError crítico: {e}")
        print("Por favor, contacte al administrador del sistema")


if __name__ == "__main__":
    main()
