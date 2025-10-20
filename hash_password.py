"""
Script de utilidad para generar hashes de contraseñas

Uso:
    python hash_password.py

Este script te permite generar hashes de contraseñas que puedes usar
para insertar/actualizar workers en la base de datos
"""

from src.utils.auth import get_password_hash


def main():
    print("=" * 60)
    print("GENERADOR DE HASH DE CONTRASEÑAS - CURSITO API")
    print("=" * 60)
    print()

    password = input("Ingresa la contraseña a hashear: ")

    if not password:
        print("Error: La contraseña no puede estar vacía")
        return

    hashed = get_password_hash(password)

    print()
    print("-" * 60)
    print("Hash generado:")
    print(hashed)
    print("-" * 60)
    print()
    print("Puedes usar este hash en la base de datos para el campo 'password'")
    print()
    print("Ejemplo de SQL:")
    print(f"UPDATE worker SET password = '{hashed}' WHERE email = 'usuario@example.com';")
    print()


if __name__ == "__main__":
    main()
