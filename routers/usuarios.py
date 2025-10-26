from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario
from database import get_db

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/")
def registrar_usuario(nombre: str, db: Session = Depends(get_db)):
    usuario = Usuario(nombre=nombre)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
