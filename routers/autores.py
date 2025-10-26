from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Autor
from database import get_db

router = APIRouter(prefix="/autores", tags=["Autores"])

@router.post("/")
def crear_autor(nombre: str, pais_origen: str = None, anio_nacimiento: int = None, db: Session = Depends(get_db)):
    autor = Autor(nombre=nombre, pais_origen=pais_origen, anio_nacimiento=anio_nacimiento)
    db.add(autor)
    db.commit()
    db.refresh(autor)
    return autor

@router.get("/")
def listar_autores(db: Session = Depends(get_db)):
    return db.query(Autor).all()

@router.get("/{autor_id}")
def obtener_autor(autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(Autor).filter(Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor
