# PruebasSoftwareTareas

Repositorio para la tarea de Pruebas de Software (2025-2).

Este repositorio contiene una pequeña aplicación CLI para gestionar micro-eventos (charlas, talleres, shows): crear eventos, vender/devolver entradas, y generar reportes simples. Además incluye tests unitarios e integraciones guardadas y documentación del entregable pedida en la tarea.

Cómo correr (resumen):

1. Crear y activar un entorno virtual Python 3.10+.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Preparar una base Postgres y exportar `DATABASE_URL` (por ejemplo: `postgresql://user:pass@127.0.0.1:5432/dbname`).
4. (Opcional) Reiniciar esquema: `python3 scripts/reset_db.py`.
5. Ejecutar la aplicación: `python3 main.py` desde la raíz.
6. Ejecutar tests: `python -m pytest -q.

Notas:

- Las pruebas de integración requieren un servidor Postgres accesible y el driver `psycopg[binary]`.
- Para reproducir el entorno de integración utilice la opción `--reset-db` en pytest (ver `tests/conftest.py`).

