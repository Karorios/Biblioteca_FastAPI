from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from database import Base, engine
from models import *
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestión de Biblioteca")

from routers import libros, autores, usuarios, reservas
app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(usuarios.router)
app.include_router(reservas.router)

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido al Sistema de Gestión de Biblioteca"}


@app.get("/endpoints", response_class=PlainTextResponse)
def mostrar_endpoints():
    return """
AUTORES
POST   /autores/
GET    /autores/
GET    /autores/{autor_id}/libros
PUT    /autores/{autor_id}
DELETE /autores/{autor_id}

LIBROS
POST   /libros/
GET    /libros/
GET    /libros/{libro_id}
PUT    /libros/{libro_id}
DELETE /libros/{libro_id}

USUARIOS
POST   /usuarios/
GET    /usuarios/
GET    /usuarios/{usuario_id}
PUT    /usuarios/{usuario_id}
DELETE /usuarios/{usuario_id}

RESERVAS
POST   /reservas/
GET    /reservas/
GET    /reservas/{id_reserva}
PUT    /reservas/{id_reserva}
DELETE /reservas/{id_reserva}


GET    /endpoints
"""