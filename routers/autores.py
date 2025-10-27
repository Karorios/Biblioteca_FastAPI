from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from models import Autor
from database import get_db
from typing import Optional
from pydantic import Field

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.post("/")
def crear_autor(
    nombre: str = Form(..., description="Nombre completo del autor"),
    pais: str = Form(..., description="País de origen del autor"),
    anio_nacimiento: int = Form(..., description="Año de nacimiento del autor"),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo autor si no existe otro con el mismo nombre.
    Valida que el nombre no esté vacío y que el año de nacimiento sea coherente.
    """
    # Validaciones Pydantic manuales
    if len(nombre.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nombre debe tener al menos 2 caracteres.")
    if len(pais.strip()) < 2:
        raise HTTPException(status_code=400, detail="El país debe tener al menos 2 caracteres.")
    if anio_nacimiento < 1500 or anio_nacimiento > 2025:
        raise HTTPException(status_code=400, detail="El año de nacimiento no es válido.")

    autor_existente = db.query(Autor).filter(Autor.nombre == nombre).first()
    if autor_existente:
        raise HTTPException(status_code=400, detail=f"El autor '{nombre}' ya está registrado")

    nuevo_autor = Autor(nombre=nombre, pais=pais, anio_nacimiento=anio_nacimiento)
    db.add(nuevo_autor)
    db.commit()
    db.refresh(nuevo_autor)
    return {"mensaje": f"Autor '{nuevo_autor.nombre}' creado correctamente"}


@router.get("/")
def listar_autores(pais: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Lista todos los autores, o filtra por país si se especifica.
    """
    query = db.query(Autor)
    if pais:
        query = query.filter(Autor.pais == pais)
    autores = query.all()
    if not autores:
        raise HTTPException(status_code=404, detail="No hay autores registrados")
    return autores


@router.get("/{autor_id}/libros")
def obtener_autor_libros(autor_id: int, db: Session = Depends(get_db)):
    """
    Muestra la información de un autor y los libros que tiene registrados.
    """
    autor = db.query(Autor).filter(Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    libros = [
        {
            "titulo": libro.titulo,
            "anio_publicacion": libro.anio_publicacion,
            "isbn": libro.isbn,
            "activo": libro.activo,
            "copias_disponibles": libro.copias_disponibles
        }
        for libro in autor.libros
    ]

    return {
        "autor": autor.nombre,
        "pais": autor.pais,
        "anio_nacimiento": autor.anio_nacimiento,
        "activo": autor.activo,
        "libros": libros or "Este autor no tiene libros registrados"
    }


@router.put("/{autor_id}")
def actualizar_autor(
    autor_id: int,
    nombre: Optional[str] = Form(None, description="Nuevo nombre del autor"),
    pais: Optional[str] = Form(None, description="Nuevo país del autor"),
    anio_nacimiento: Optional[int] = Form(None, description="Nuevo año de nacimiento"),
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un autor existente.
    Solo se cambian los campos enviados.
    """
    autor = db.query(Autor).filter(Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    if nombre:
        if len(nombre.strip()) < 2:
            raise HTTPException(status_code=400, detail="El nombre debe tener al menos 2 caracteres.")
        autor.nombre = nombre

    if pais:
        if len(pais.strip()) < 2:
            raise HTTPException(status_code=400, detail="El país debe tener al menos 2 caracteres.")
        autor.pais = pais

    if anio_nacimiento:
        if anio_nacimiento < 1500 or anio_nacimiento > 2025:
            raise HTTPException(status_code=400, detail="El año de nacimiento no es válido.")
        autor.anio_nacimiento = anio_nacimiento

    db.commit()
    db.refresh(autor)
    return {"mensaje": f"Autor '{autor.nombre}' actualizado correctamente"}


@router.delete("/{autor_id}")
def eliminar_autor(autor_id: int, db: Session = Depends(get_db)):
    """
    Marca un autor como inactivo (no lo elimina físicamente).
    """
    autor = db.query(Autor).filter(Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    autor.activo = False
    db.commit()
    return {"mensaje": f"Autor '{autor.nombre}' marcado como inactivo (los libros conservarán su nombre)"}
