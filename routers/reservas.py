from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Reserva, Usuario, Libro
from database import get_db
from datetime import date, timedelta

router = APIRouter(prefix="/reservas", tags=["Reservas"])

@router.post("/")
def crear_reserva(id_usuario: int, isbn_libro: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    libro = db.query(Libro).filter(Libro.isbn == isbn_libro).first()

    if not usuario or not libro:
        raise HTTPException(status_code=404, detail="Usuario o libro no encontrado")

    reserva = Reserva(
        id_usuario=id_usuario,
        isbn_libro=isbn_libro,
        fecha_reserva=date.today(),
        fecha_entrega=date.today() + timedelta(days=15),
        estado="activa",
        nombre_usuario=usuario.nombre,
        nombre_libro=libro.titulo
    )

    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva

@router.get("/")
def listar_reservas(db: Session = Depends(get_db)):
    return db.query(Reserva).all()

@router.get("/{reserva_id}")
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id_reserva == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva
