from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from sqlalchemy.orm import Session
from models import Libro, Autor
from database import get_db
from pydantic import BaseModel


class LibroCreate(BaseModel):
    titulo: str
    isbn: str
    anio_publicacion: int
    copias_disponibles: int
    autores: List[str]  # autor1, autor2, autor3 en una lista


router = APIRouter(prefix="/libros", tags=["Libros"])


@router.post("/")
def crear_libro(libro: LibroCreate, db: Session = Depends(get_db)):
    # Validar duplicado ISBN
    if db.query(Libro).filter(Libro.isbn == libro.isbn).first():
        raise HTTPException(status_code=400, detail="Ya existe un libro con ese ISBN")

    # Buscar autores existentes
    autores = db.query(Autor).filter(Autor.nombre.in_(libro.autores), Autor.activo == True).all()
    if not autores or len(autores) != len(libro.autores):
        raise HTTPException(status_code=400, detail="Uno o más autores no existen o están inactivos")

    nuevo_libro = Libro(
        titulo=libro.titulo,
        isbn=libro.isbn,
        anio_publicacion=libro.anio_publicacion,
        copias_disponibles=libro.copias_disponibles,
        autores=autores
    )

    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)

    return {
        "mensaje": f"Libro '{nuevo_libro.titulo}' creado correctamente",
        "isbn": nuevo_libro.isbn,
        "anio_publicacion": nuevo_libro.anio_publicacion,
        "copias_disponibles": nuevo_libro.copias_disponibles,
        "autores_asociados": [autor.nombre for autor in autores]
    }

@router.get("/")
def listar_libros(anio: int = None, db: Session = Depends(get_db)):
    query = db.query(Libro).filter(Libro.activo == True)

    if anio:
        query = query.filter(Libro.anio_publicacion == anio)

    libros = query.all()

    if not libros:
        detalle = f"No se encontró ningún libro registrado del año {anio}" if anio else "No hay libros registrados actualmente en la base de datos"
        raise HTTPException(status_code=404, detail=detalle)

    resultado = []
    for libro in libros:
        autores_activos = [autor.nombre for autor in libro.autores if autor.activo]
        resultado.append({
            "id": libro.id,
            "titulo": libro.titulo,
            "isbn": libro.isbn,
            "anio_publicacion": libro.anio_publicacion,
            "copias_disponibles": libro.copias_disponibles,
            "cantidad_autores": len(autores_activos),
            "autores": autores_activos
        })

    return resultado


@router.get("/{libro_id}")
def obtener_libro_con_autores(libro_id: int, db: Session = Depends(get_db)):
    libro = db.query(Libro).filter(Libro.id == libro_id, Libro.activo == True).first()

    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    # Verificamos si tiene autores asociados
    if not libro.autores:
        autores_info = "Este libro no tiene autores registrados"
    else:
        autores_info = [
            {
                "id": autor.id,
                "nombre": autor.nombre,
                "pais": autor.pais,
                "activo": autor.activo
            }
            for autor in libro.autores
        ]

    return {
        "id": libro.id,
        "titulo": libro.titulo,
        "isbn": libro.isbn,
        "anio_publicacion": libro.anio_publicacion,
        "copias_disponibles": libro.copias_disponibles,
        "autores": autores_info
    }


@router.put("/{libro_id}")
def actualizar_libro(
    libro_id: int,
    titulo: Optional[str] = None,
    copias_disponibles: Optional[int] = None,
    autor1: Optional[str] = Query(None, description="Nombre del autor principal (opcional)"),
    autor2: Optional[str] = Query(None, description="Nombre del segundo autor (opcional)"),
    autor3: Optional[str] = Query(None, description="Nombre del tercer autor (opcional)"),
    db: Session = Depends(get_db)
):
    libro = db.query(Libro).filter(Libro.id == libro_id, Libro.activo == True).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    if titulo:
        libro.titulo = titulo

    if copias_disponibles is not None:
        if copias_disponibles < 0:
            raise HTTPException(status_code=400, detail="Las copias no pueden ser negativas")
        libro.copias_disponibles = copias_disponibles

    nombres_autores = []
    if autor1:
        nombres_autores.append(autor1)
    if autor2:
        nombres_autores.append(autor2)
    if autor3:
        nombres_autores.append(autor3)

    if nombres_autores:
        autores = db.query(Autor).filter(Autor.nombre.in_(nombres_autores), Autor.activo == True).all()
        if len(autores) != len(nombres_autores):
            raise HTTPException(
                status_code=400,
                detail="Uno o más autores no existen o están inactivos. Verifica los nombres ingresados."
            )
        libro.autores = autores

    db.commit()
    db.refresh(libro)

    return {
        "mensaje": f"Libro '{libro.titulo}' actualizado correctamente",
        "isbn": libro.isbn,
        "anio_publicacion": libro.anio_publicacion,
        "copias_disponibles": libro.copias_disponibles,
        "autores_asociados": [autor.nombre for autor in libro.autores]
    }

@router.delete("/{libro_id}")
def eliminar_libro(libro_id: int, db: Session = Depends(get_db)):
    libro = db.query(Libro).filter(Libro.id == libro_id, Libro.activo == True).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    libro.activo = False
    db.commit()
    return {"mensaje": f"Libro '{libro.titulo}' marcado como inactivo"}
