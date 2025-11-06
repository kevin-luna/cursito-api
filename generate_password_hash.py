#!/usr/bin/env python3
"""
Script para generar hashes de contraseñas usando bcrypt.
Útil para insertar usuarios directamente en la base de datos.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_hash(password: str) -> str:
    """Genera el hash bcrypt de una contraseña"""
    return pwd_context.hash(password)

if __name__ == "__main__":
    # Contraseñas de ejemplo
    passwords = {
        "admin123": "Contraseña para admin",
        "trabajador123": "Contraseña para trabajador",
        "teacher123": "Contraseña para docente",
        "password": "Contraseña genérica"
    }

    print("=" * 70)
    print("HASHES DE CONTRASEÑAS GENERADOS CON BCRYPT")
    print("=" * 70)
    print()

    for password, description in passwords.items():
        hashed = generate_hash(password)
        print(f"Contraseña: {password}")
        print(f"Descripción: {description}")
        print(f"Hash: {hashed}")
        print("-" * 70)
        print()

    # Generar hash personalizado
    print("\n" + "=" * 70)
    print("GENERAR HASH PERSONALIZADO")
    print("=" * 70)
    custom_password = input("\nIngresa la contraseña que deseas hashear: ")
    if custom_password:
        custom_hash = generate_hash(custom_password)
        print(f"\nContraseña: {custom_password}")
        print(f"Hash: {custom_hash}")
