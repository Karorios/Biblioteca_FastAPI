from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import Reserva, Usuario, Libro
from database import get_db

router = APIRouter(prefix="/reservas", tags=["Reservas"])

@router.post("/")
def crear_reserva(usuario_id: int, isbn: str, db: Session = Depends(get_db)):
    """
    Crea una reserva usando el ID del usuario y el ISBN del libro.
    - El usuario debe estar activo.
    - Máximo 3 reservas activas por usuario.
    """

    # Verificar existencia del usuario activo
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.activo == True).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o inactivo")

    # Verificar existencia del libro
    libro = db.query(Libro).filter(Libro.isbn == isbn).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado con ese ISBN")

    # Verificar disponibilidad
    if libro.copias_disponibles <= 0:
        raise HTTPException(status_code=400, detail="No hay copias disponibles de este libro")

    # Contar reservas activas del usuario
    reservas_activas = db.query(Reserva).filter(
        Reserva.id_usuario == usuario.id,
        Reserva.estado == "activo",
        Reserva.activo == True
    ).count()

    if reservas_activas >= 3:
        raise HTTPException(status_code=400, detail="El usuario ya tiene el máximo de 3 reservas activas")

    # Evitar duplicado del mismo libro
    reserva_existente = db.query(Reserva).filter(
        Reserva.id_usuario == usuario.id,
        Reserva.isbn_libro == libro.isbn,
        Reserva.estado == "activo",
        Reserva.activo == True
    ).first()

    if reserva_existente:
        raise HTTPException(status_code=400, detail="El usuario ya tiene una reserva activa para este libro")

    # Crear la reserva con fecha de entrega 7 días después
    fecha_reserva = datetime.now()
    fecha_entrega = fecha_reserva + timedelta(days=7)

    nueva_reserva = Reserva(
        id_usuario=usuario.id,
        isbn_libro=libro.isbn,
        fecha_reserva=fecha_reserva,
        fecha_entrega=fecha_entrega,
        estado="activo",
        activo=True
    )

    # Reducir copias disponibles
    libro.copias_disponibles -= 1

    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)

    return {
        "mensaje": "Reserva creada exitosamente",
        "reserva": {
            "id": nueva_reserva.id,
            "id_usuario": usuario.id,
            "nombre_usuario": usuario.nombre,
            "isbn": libro.isbn,
            "titulo_libro": libro.titulo,
            "fecha_reserva": nueva_reserva.fecha_reserva,
            "fecha_entrega": nueva_reserva.fecha_entrega,
            "estado": nueva_reserva.estado
        }
    }


@router.get("/")
def listar_reservas(db: Session = Depends(get_db)):
    """
    Lista todas las reservas activas mostrando nombre de usuario y título del libro.
    """
    reservas = db.query(Reserva).filter(Reserva.activo == True).all()
    if not reservas:
        raise HTTPException(status_code=404, detail="No hay reservas activas registradas")

    resultado = []
    for r in reservas:
        usuario = db.query(Usuario).filter(Usuario.id == r.id_usuario).first()
        libro = db.query(Libro).filter(Libro.isbn == r.isbn_libro).first()
        resultado.append({
            "id": r.id,
            "id_usuario": r.id_usuario,
            "nombre_usuario": usuario.nombre if usuario else None,
            "isbn": r.isbn_libro,
            "titulo_libro": libro.titulo if libro else None,
            "fecha_reserva": r.fecha_reserva,
            "fecha_entrega": r.fecha_entrega,
            "estado": r.estado
        })
    return resultado


@router.get("/{id_reserva}")
def obtener_reserva(id_reserva: int, db: Session = Depends(get_db)):
    """
    Obtiene una reserva específica con datos del usuario y el libro.
    """
    reserva = db.query(Reserva).filter(Reserva.id == id_reserva, Reserva.activo == True).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    usuario = db.query(Usuario).filter(Usuario.id == reserva.id_usuario).first()
    libro = db.query(Libro).filter(Libro.isbn == reserva.isbn_libro).first()

    return {
        "id": reserva.id,
        "id_usuario": reserva.id_usuario,
        "nombre_usuario": usuario.nombre if usuario else None,
        "isbn": reserva.isbn_libro,
        "titulo_libro": libro.titulo if libro else None,
        "fecha_reserva": reserva.fecha_reserva,
        "fecha_entrega": reserva.fecha_entrega,
        "estado": reserva.estado
    }


@router.put("/{id_reserva}")
def actualizar_reserva(
    id_reserva: int,
    estado: str = Form(..., description="Nuevo estado de la reserva (activo, entregada, cancelada)"),
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de una reserva (activo, entregada o cancelada).
    """
    db_reserva = db.query(Reserva).filter(Reserva.id == id_reserva, Reserva.activo == True).first()
    if not db_reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if estado.lower() not in ["activo", "entregada", "cancelada"]:
        raise HTTPException(status_code=400, detail="Estado inválido. Use: activo, entregada o cancelada")

    db_reserva.estado = estado.lower()

    # Si se entrega o cancela, se libera una copia del libro
    if db_reserva.estado in ["entregada", "cancelada"]:
        libro = db.query(Libro).filter(Libro.isbn == db_reserva.isbn_libro).first()
        if libro:
            libro.copias_disponibles += 1

    db.commit()
    db.refresh(db_reserva)

    return {
        "mensaje": "Reserva actualizada correctamente",
        "id": db_reserva.id,
        "estado": db_reserva.estado
    }


@router.delete("/{id_reserva}")
def eliminar_reserva(id_reserva: int, db: Session = Depends(get_db)):
    """
    Elimina una reserva y libera la copia si estaba activa.
    """
    reserva = db.query(Reserva).filter(Reserva.id == id_reserva, Reserva.activo == True).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    reserva.activo = False

    if reserva.estado == "activo":
        libro = db.query(Libro).filter(Libro.isbn == reserva.isbn_libro).first()
        if libro:
            libro.copias_disponibles += 1

    db.commit()
    return {"mensaje": "Reserva eliminada ", "id_reserva": reserva.id}
