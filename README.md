# PruebasSoftwareTareas

## Requisitos
- Python 3.12+
- PostgreSQL 14+ en local

# Instalar dependencias
pip install -r requirements.txt

## Configurar base de datos
La app usa `DATABASE_URL` (por defecto `postgresql://postgres:123@localhost:5432/tarea1`).

```powershell
$env:DATABASE_URL = "postgresql://postgres:123@localhost:5432/tarea1"

# crear DB si no existe
psql "postgresql://postgres:123@localhost:5432/postgres" -c "CREATE DATABASE tarea1;"

# aplicar esquema
psql "postgresql://postgres:123@localhost:5432/tarea1" -f schema.sql
```

## Crear usuario administrador
```powershell
python -c "from domain import create_user; print(create_user('admin','admin123','admin'))"
```

## Ejecutar interfaz de consola
```powershell
python interface\main.py
```
- Puedes registrarte como usuario/admin o iniciar sesión (admin/admin123 si se creó el admin arriba).
- Menú de usuario permite gestionar eventos, ventas/devoluciones y ver reportes.

## Ejecutar smoke tests
```powershell
python test.py
```

## Notas
- Categorías permitidas: Charla, Taller, Show, Otro.
- Precios: enteros (CLP).
- Zona horaria: se interpreta local y se guarda en UTC.