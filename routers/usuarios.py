from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/usuarios")
def crear_usuario(
    nombre: str = Query(..., min_length=3, max_length=50, description="Nombre del usuario"),
    codigo_unico: str = Query(..., min_length=4, max_length=20, description="Código único del usuario"),
    db: Session = Depends(get_db)
):
    if db.query(Usuario).filter(Usuario.codigo_unico == codigo_unico).first():
        raise HTTPException(status_code=400, detail="El código único ya está en uso")

    nuevo_usuario = Usuario(nombre=nombre, codigo_unico=codigo_unico)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "Usuario creado exitosamente", "usuario": nuevo_usuario}

@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
    if not usuarios:
        raise HTTPException(status_code=404, detail="No hay usuarios activos")

    return [
        {"id": u.id, "nombre": u.nombre, "codigo_unico": u.codigo_unico}
        for u in usuarios
    ]

@router.put("/{usuario_id}")
def actualizar_usuario(
    usuario_id: int,
    nombre: str = Query(None, min_length=3, max_length=50, description="Nuevo nombre del usuario"),
    codigo_unico: str = Query(None, min_length=4, max_length=20, description="Nuevo código único del usuario"),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.activo == True).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if codigo_unico and db.query(Usuario).filter(Usuario.codigo_unico == codigo_unico, Usuario.id != usuario_id).first():
        raise HTTPException(status_code=400, detail="Ese código único ya está en uso por otro usuario")

    if nombre:
        usuario.nombre = nombre
    if codigo_unico:
        usuario.codigo_unico = codigo_unico

    db.commit()
    db.refresh(usuario)

    return {"mensaje": "Usuario actualizado correctamente", "usuario": {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "codigo_unico": usuario.codigo_unico
    }}

@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.activo == True).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = False
    db.commit()
    return {"mensaje": "Usuario eliminado lógicamente", "id": usuario.id}
