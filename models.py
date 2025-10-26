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



