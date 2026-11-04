"""Punto de entrada: uvicorn majo.main:app --reload"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from majo.web.routes import router

app = FastAPI(title="Majö Helado Yogurt")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "web" / "static"), name="static")
app.include_router(router)


@app.get("/healthz", include_in_schema=False)
def healthz():
    """Health check para Render/Railway (no toca la base de datos)."""
    return {"status": "ok"}
