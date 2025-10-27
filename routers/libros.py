from fastapi import APIRouter, Depends, HTTPException, Form, Path
from sqlalchemy.orm import Session
from typing import Optional
from models import Libro, Autor
from database import get_db

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.post("/")
def crear_libro(
    titulo: str = Form(..., min_length=3, max_length=100, description="Título del libro (3 a 100 caracteres)"),
    isbn: str = Form(..., min_length=10, max_length=20, description="Código ISBN único del libro"),
    anio_publicacion: int = Form(..., ge=1500, le=2025, description="Año de publicación entre 1500 y 2025"),
    copias_disponibles: int = Form(..., ge=1, le=1000, description="Número de copias disponibles (1-1000)"),
    autores: str = Form(..., min_length=3, description="Nombres de los autores separados por coma"),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo libro validando duplicados, año y autores existentes.
    """

    if db.query(Libro).filter(Libro.isbn == isbn).first():
        raise HTTPException(status_code=400, detail="Ya existe un libro con ese ISBN")

    lista_autores = [a.strip() for a in autores.split(",") if a.strip()]
    if not lista_autores:
        raise HTTPException(status_code=400, detail="Debe indicar al menos un autor válido")

    autores_encontrados = db.query(Autor).filter(Autor.nombre.in_(lista_autores)).all()

    if len(autores_encontrados) != len(lista_autores):
        raise HTTPException(status_code=400, detail="Uno o más autores no existen o están inactivos")

    nuevo_libro = Libro(
        titulo=titulo,
        isbn=isbn,
        anio_publicacion=anio_publicacion,
        copias_disponibles=copias_disponibles,
        autores=autores_encontrados
    )

    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)

    return {"mensaje": f"Libro '{titulo}' creado correctamente"}


@router.get("/")
def listar_libros(db: Session = Depends(get_db)):
    """
    Lista todos los libros registrados en la base de datos con sus autores y disponibilidad.
    """
    libros = db.query(Libro).all()
    if not libros:
        raise HTTPException(status_code=404, detail="No hay libros registrados")

    return [
        {
            "id": libro.id,
            "titulo": libro.titulo,
            "isbn": libro.isbn,
            "anio_publicacion": libro.anio_publicacion,
            "copias_disponibles": libro.copias_disponibles,
            "activo": libro.activo,
            "autores": [{"nombre": a.nombre, "activo": a.activo} for a in libro.autores]
        }
        for libro in libros
    ]


@router.get("/buscar_por_anio/{anio_publicacion}")
def buscar_libros_por_anio(
    anio_publicacion: int = Path(..., description="Año de publicación del libro"),
    db: Session = Depends(get_db)
):
    """
    Busca todos los libros publicados en un año específico.
    """
    libros = db.query(Libro).filter(Libro.anio_publicacion == anio_publicacion).all()
    if not libros:
        raise HTTPException(status_code=404, detail=f"No se encontraron libros del año {anio_publicacion}")

    return libros


@router.put("/{libro_id}")
def actualizar_libro(
    libro_id: int,
    titulo: Optional[str] = Form(None, min_length=3, max_length=100, description="Nuevo título del libro"),
    isbn: Optional[str] = Form(None, min_length=10, max_length=20, description="Nuevo código ISBN"),
    anio_publicacion: Optional[int] = Form(None, ge=1500, le=2025, description="Nuevo año de publicación"),
    copias_disponibles: Optional[int] = Form(None, ge=0, le=1000, description="Cantidad de copias disponibles (0-1000)"),
    autores: Optional[str] = Form(None, description="Nuevos autores separados por coma"),
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un libro existente. Permite modificar título, ISBN, año, copias y autores.
    """
    libro = db.query(Libro).filter(Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    if isbn and db.query(Libro).filter(Libro.isbn == isbn, Libro.id != libro_id).first():
        raise HTTPException(status_code=400, detail="Ya existe otro libro con ese ISBN")

    if titulo:
        libro.titulo = titulo
    if isbn:
        libro.isbn = isbn
    if anio_publicacion:
        libro.anio_publicacion = anio_publicacion
    if copias_disponibles is not None:
        libro.copias_disponibles = copias_disponibles

    if autores:
        nombres_autores = [a.strip() for a in autores.split(",") if a.strip()]
        autores_nuevos = db.query(Autor).filter(Autor.nombre.in_(nombres_autores)).all()
        if len(autores_nuevos) != len(nombres_autores):
            raise HTTPException(status_code=400, detail="Algunos autores no existen o están inactivos")
        libro.autores = autores_nuevos

    db.commit()
    db.refresh(libro)

    return {"mensaje": f"Libro '{libro.titulo}' actualizado correctamente"}


@router.delete("/{libro_id}")
def eliminar_libro(libro_id: int, db: Session = Depends(get_db)):
    """
    Elimina una copia de un libro o lo marca como inactivo si no quedan copias.
    """
    libro = db.query(Libro).filter(Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    if libro.copias_disponibles > 0:
        libro.copias_disponibles -= 1
        if libro.copias_disponibles == 0:
            libro.activo = False
    else:
        libro.activo = False

    db.commit()
    db.refresh(libro)

    return {
        "mensaje": f"Libro '{libro.titulo}' actualizado tras eliminación de una copia.",
        "copias_restantes": libro.copias_disponibles,
        "activo": libro.activo
    }
