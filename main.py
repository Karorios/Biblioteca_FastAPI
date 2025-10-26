from fastapi import FastAPI
from routers import libros, autores, usuarios, reservas
from database import Base, engine
from models import *

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestión de Biblioteca")

app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(usuarios.router)
app.include_router(reservas.router)

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido al Sistema de Gestión de Biblioteca"}
