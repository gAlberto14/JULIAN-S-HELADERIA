# Majö Helado Yogurt (Python + FastAPI + Supabase)

## Ejecutar
```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn majo.main:app --reload                       # http://127.0.0.1:8000
pytest                                               # pruebas de la lógica
```
Sin `.env` corre en **modo demo** (memoria): admin@majo.co / admin123 y mesero@majo.co / mesero123.

## Con Supabase
1. Ejecuta `majo-supabase-schema.sql` en el SQL Editor de Supabase y crea tus usuarios en Authentication.
2. Copia `.env.example` a `.env` y completa URL, anon key y service key.
   La **service key es secreta**: solo va en el servidor, nunca en el navegador ni en Git.

## Despliegue
Listo para **Render** y **Railway** (`render.yaml`, `railway.json`, `Procfile` y `.python-version`).
Netlify no ejecuta Python/FastAPI, así que no sirve para este backend.
Guía paso a paso, variables y comprobaciones: [`docs/DESPLIEGUE.md`](docs/DESPLIEGUE.md).
Health check: `GET /healthz`.

## Arquitectura (por capas)
```
web (routes, templates)  →  services (reglas de negocio)  →  repositories (interfaces)
                                                                 ├─ memory.py      (demo y tests)
                                                                 └─ supabase_repo.py
domain/models.py = objetos del negocio     container.py = arma todo
```
Patrones usados:
- **Repository**: `repositories/base.py` define contratos; los servicios no saben si hay Supabase o memoria.
- **Service Layer**: `services/services.py` concentra las reglas (precios desde BD, validaciones, reportes).
- **Factory + Inyección de dependencias**: `container.py` elige la implementación; FastAPI la entrega con `Depends`.

Para aprender: agrega un `SqliteProductRepository` sin tocar servicios ni rutas; o agrega el descuento por producto en `SalesService`.

## Interfaz
Sistema de diseño, componentes y decisiones: `docs/DISENO_UI.md`. Pruebas: `pytest` (lógica y páginas por rol).
