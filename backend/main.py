"""Archivo principal de FastAPI."""

from fastapi import FastAPI

from backend.rutas import libros


app = FastAPI(
    title="Sistema de prestamos para Biblioteca Escolar",
    description="Primera etapa: CRUD de una sola tabla",
    version="nose xd",
)

app.include_router(libros.router)


@app.get("/", tags=["Estado"])
def inicio():
    return {"estado": "ok", "mensaje": "La API esta funcionando"}

