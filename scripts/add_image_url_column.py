"""
Script para agregar la columna image_url a la tabla posts
Ejecutar con: python scripts/add_image_url_column.py
"""

import os
import sys

# Agregar el directorio raíz al path para importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.core.db import engine


def add_image_url_column():
    """Agrega la columna image_url a la tabla posts si no existe"""
    with engine.connect() as conn:
        try:
            # Verificar si la columna ya existe
            check_query = text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'posts' 
                AND column_name = 'image_url'
            """
            )

            result = conn.execute(check_query)
            if result.fetchone():
                print("✅ La columna image_url ya existe en la tabla posts")
                return

            # Agregar la columna
            alter_query = text(
                """
                ALTER TABLE posts 
                ADD COLUMN image_url VARCHAR(300) NULL
            """
            )

            conn.execute(alter_query)
            conn.commit()
            print("✅ Columna image_url agregada exitosamente a la tabla posts")

        except Exception as e:
            conn.rollback()
            print(f"❌ Error al agregar la columna: {e}")
            raise


if __name__ == "__main__":
    print("Ejecutando migración para agregar columna image_url...")
    add_image_url_column()
