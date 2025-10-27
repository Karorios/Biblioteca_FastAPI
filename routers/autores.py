from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Autor, Libro
from database import get_db
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/autores", tags=["Autores"])

# Modelo para crear autor
class AutorCreate(BaseModel):
    nombre: str
    pais: str
    anio_nacimiento: int

# Crear autor
@router.post("/")
def crear_autor(autor: AutorCreate, db: Session = Depends(get_db)):
    autor_existente = db.query(Autor).filter(Autor.nombre == autor.nombre).first()
    if autor_existente:
        raise HTTPException(status_code=400, detail=f"El autor '{autor.nombre}' ya está registrado")

    nuevo_autor = Autor(
        nombre=autor.nombre,
        pais=autor.pais,
        anio_nacimiento=autor.anio_nacimiento
    )
    db.add(nuevo_autor)
    db.commit()
    db.refresh(nuevo_autor)

    return {
        "mensaje": f"Autor '{nuevo_autor.nombre}' creado correctamente",
        "nombre": nuevo_autor.nombre,
        "pais": nuevo_autor.pais,
        "anio_nacimiento": nuevo_autor.anio_nacimiento
    }

# Listar autores (opcional por país)
@router.get("/")
def listar_autores(pais: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Autor).filter(Autor.activo == True)
    if pais:
        query = query.filter(Autor.pais == pais)
    autores = query.all()
    if not autores:
        raise HTTPException(status_code=404, detail="No hay autores registrados")
    return autores

# Obtener libros de un autor
@router.get("/{autor_id}/libros")
def obtener_autor_libros(autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(Autor).filter(Autor.id == autor_id, Autor.activo == True).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    libros = [
        {
            "id": libro.id,
            "titulo": libro.titulo,
            "isbn": libro.isbn,
            "anio_publicacion": libro.anio_publicacion,
            "copias_disponibles": libro.copias_disponibles
        }
        for libro in autor.libros if libro.activo
    ]

    if not libros:
        return {
            "autor": autor.nombre,
            "pais": autor.pais,
            "anio_nacimiento": autor.anio_nacimiento,
            "libros": "Este autor no tiene libros registrados"
        }

    return {
        "autor": autor.nombre,
        "pais": autor.pais,
        "anio_nacimiento": autor.anio_nacimiento,
        "libros": libros
    }

# Actualizar autor
@router.put("/{autor_id}")
def actualizar_autor(autor_id: int, nombre: Optional[str] = None, pais: Optional[str] = None, anio_nacimiento: Optional[int] = None, db: Session = Depends(get_db)):
    autor = db.query(Autor).filter(Autor.id == autor_id, Autor.activo == True).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    if nombre:
        autor.nombre = nombre
    if pais:
        autor.pais = pais
    if anio_nacimiento:
        autor.anio_nacimiento = anio_nacimiento
    db.commit()
    db.refresh(autor)
    return autor

# Eliminar autor (lógicamente)
@router.delete("/{autor_id}")
def eliminar_autor(autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(Autor).filter(Autor.id == autor_id, Autor.activo == True).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    # Desvincular libros
    for libro in autor.libros:
        libro.autores = [a for a in libro.autores if a.id != autor.id]
    autor.activo = False
    db.commit()
    return {"mensaje": f"Autor '{autor.nombre}' marcado como inactivo y desvinculado de sus libros"}
