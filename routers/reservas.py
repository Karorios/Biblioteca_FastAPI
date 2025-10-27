from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models import Reserva, Usuario, Libro
from pydantic import BaseModel

router = APIRouter(prefix="/reservas", tags=["Reservas"])

# Modelo Pydantic para crear reserva
class ReservaCreate(BaseModel):
    id_usuario: int
    isbn_libro: str

# Crear reserva
@router.post("/")
def crear_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == reserva.id_usuario, Usuario.activo == True).first()
    libro = db.query(Libro).filter(Libro.isbn == reserva.isbn_libro, Libro.activo == True).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    if libro.copias_disponibles <= 0:
        raise HTTPException(status_code=400, detail="No hay copias disponibles para reservar")

    fecha_reserva = datetime.now()
    fecha_entrega = fecha_reserva + timedelta(days=15)

    nueva_reserva = Reserva(
        id_usuario=reserva.id_usuario,
        isbn_libro=reserva.isbn_libro,
        fecha_reserva=fecha_reserva,
        fecha_entrega=fecha_entrega,
        estado="activa",
        activo=True
    )

    libro.copias_disponibles -= 1

    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)

    return {
        "mensaje": "Reserva creada exitosamente",
        "reserva": {
            "id": nueva_reserva.id,
            "usuario": {"id": usuario.id, "nombre": usuario.nombre, "codigo_unico": usuario.codigo_unico},
            "libro": {"isbn": libro.isbn, "titulo": libro.titulo},
            "fecha_reserva": fecha_reserva,
            "fecha_entrega": fecha_entrega,
            "estado": nueva_reserva.estado
        }
    }

# Listar todas las reservas
@router.get("/")
def listar_reservas(db: Session = Depends(get_db)):
    reservas = db.query(Reserva).filter(Reserva.activo == True).all()
    resultado = []
    for r in reservas:
        usuario = db.query(Usuario).filter(Usuario.id == r.id_usuario).first()
        libro = db.query(Libro).filter(Libro.isbn == r.isbn_libro).first()
        resultado.append({
            "id": r.id,
            "usuario": {"id": usuario.id, "nombre": usuario.nombre} if usuario else None,
            "libro": {"isbn": libro.isbn, "titulo": libro.titulo} if libro else None,
            "fecha_reserva": r.fecha_reserva,
            "fecha_entrega": r.fecha_entrega,
            "estado": r.estado
        })
    return resultado

# Obtener reserva por ID
@router.get("/{id_reserva}")
def obtener_reserva(id_reserva: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == id_reserva, Reserva.activo == True).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    usuario = db.query(Usuario).filter(Usuario.id == reserva.id_usuario).first()
    libro = db.query(Libro).filter(Libro.isbn == reserva.isbn_libro).first()

    return {
        "id": reserva.id,
        "usuario": {"id": usuario.id, "nombre": usuario.nombre} if usuario else None,
        "libro": {"isbn": libro.isbn, "titulo": libro.titulo} if libro else None,
        "fecha_reserva": reserva.fecha_reserva,
        "fecha_entrega": reserva.fecha_entrega,
        "estado": reserva.estado
    }

# Modelo para actualizar estado
class ReservaUpdate(BaseModel):
    estado: str

# Actualizar estado de reserva
@router.put("/{id_reserva}")
def actualizar_reserva(id_reserva: int, reserva: ReservaUpdate, db: Session = Depends(get_db)):
    db_reserva = db.query(Reserva).filter(Reserva.id == id_reserva, Reserva.activo == True).first()
    if not db_reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    db_reserva.estado = reserva.estado
    db.commit()
    db.refresh(db_reserva)

    return {"mensaje": "Reserva actualizada", "estado": db_reserva.estado}

# Eliminar reserva (lógica)
@router.delete("/{id_reserva}")
def eliminar_reserva(id_reserva: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == id_reserva, Reserva.activo == True).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    reserva.activo = False

    # Devolver copia al libro si estaba activa
    if reserva.estado == "activa":
        libro = db.query(Libro).filter(Libro.isbn == reserva.isbn_libro).first()
        if libro:
            libro.copias_disponibles += 1

    db.commit()
    return {"mensaje": "Reserva eliminada lógicamente", "id_reserva": reserva.id}
