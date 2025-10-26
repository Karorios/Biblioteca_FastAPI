from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Libro, Autor
from database import get_db

router = APIRouter(prefix="/libros", tags=["Libros"])

@router.post("/")
def crear_libro(isbn: str, titulo: str, anio_publicacion: int, num_copias: int, genero: str, autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(Autor).filter(Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    libro = Libro(isbn=isbn, titulo=titulo, anio_publicacion=anio_publicacion, num_copias=num_copias, genero=genero, autor_id=autor_id)
    db.add(libro)
    db.commit()
    db.refresh(libro)
    return libro

@router.get("/")
def listar_libros(db: Session = Depends(get_db)):
    return db.query(Libro).all()

@router.get("/{isbn}")
def obtener_libro(isbn: str, db: Session = Depends(get_db)):
    libro = db.query(Libro).filter(Libro.isbn == isbn).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro
