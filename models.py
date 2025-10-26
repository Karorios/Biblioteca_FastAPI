from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date, timedelta
from database import Base

class Autor(Base):
    __tablename__ = "autores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    pais_origen = Column(String, nullable=True)
    anio_nacimiento = Column(Integer, nullable=True)

    libros = relationship("Libro", back_populates="autor")

class Libro(Base):
    __tablename__ = "libros"

    isbn = Column(String, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    anio_publicacion = Column(Integer, nullable=False)
    num_copias = Column(Integer, nullable=False)
    genero = Column(String, nullable=True)

    autor_id = Column(Integer, ForeignKey("autores.id"), nullable=False)
    autor = relationship("Autor", back_populates="libros")

    reservas = relationship("Reserva", back_populates="libro")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    reservas = relationship("Reserva", back_populates="usuario")
class Reserva(Base):
    __tablename__ = "reservas"

    id_reserva = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    isbn_libro = Column(String, ForeignKey("libros.isbn"), nullable=False)
    fecha_reserva = Column(Date, default=date.today)
    fecha_entrega = Column(Date)
    estado = Column(String, default="activa")

    nombre_usuario = Column(String, nullable=True)
    nombre_libro = Column(String, nullable=True)

    usuario = relationship("Usuario", back_populates="reservas")
    libro = relationship("Libro", back_populates="reservas")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.fecha_entrega:
            self.fecha_entrega = date.today() + timedelta(days=15)




