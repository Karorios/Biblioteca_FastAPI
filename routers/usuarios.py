from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from pydantic import BaseModel

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Modelo Pydantic para creación y actualización
class UsuarioCreate(BaseModel):
    nombre: str
    codigo_unico: str

@router.post("/")
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.codigo_unico == usuario.codigo_unico).first():
        raise HTTPException(status_code=400, detail="El código ya está registrado")

    nuevo_usuario = Usuario(nombre=usuario.nombre, codigo_unico=usuario.codigo_unico)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "codigo_unico": nuevo_usuario.codigo_unico
    }

@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    return [
        {"id": u.id, "nombre": u.nombre, "codigo_unico": u.codigo_unico}
        for u in usuarios
    ]

@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.activo == True).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "codigo_unico": usuario.codigo_unico
    }

@router.put("/{usuario_id}")
def actualizar_usuario(usuario_id: int, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    existing_usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.activo == True).first()
    if not existing_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if db.query(Usuario).filter(Usuario.codigo_unico == usuario.codigo_unico, Usuario.id != usuario_id).first():
        raise HTTPException(status_code=400, detail="Ese código único ya está en uso por otro usuario")

    existing_usuario.nombre = usuario.nombre
    existing_usuario.codigo_unico = usuario.codigo_unico
    db.commit()
    db.refresh(existing_usuario)

    return {
        "mensaje": "Usuario actualizado correctamente",
        "id": existing_usuario.id,
        "nombre": existing_usuario.nombre,
        "codigo_unico": existing_usuario.codigo_unico
    }

@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.activo == True).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = False
    db.commit()

    return {"mensaje": "Usuario eliminado lógicamente", "id": usuario.id}
