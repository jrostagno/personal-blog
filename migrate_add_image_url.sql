-- Script para agregar la columna image_url a la tabla posts
-- Ejecutar este script directamente en Dataplus o psql

-- Verificar si la columna ya existe (opcional, para evitar errores)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'posts' 
        AND column_name = 'image_url'
    ) THEN
        -- Agregar la columna image_url
        ALTER TABLE posts 
        ADD COLUMN image_url VARCHAR(300) NULL;
        
        RAISE NOTICE 'Columna image_url agregada exitosamente a la tabla posts';
    ELSE
        RAISE NOTICE 'La columna image_url ya existe en la tabla posts';
    END IF;
END $$;

