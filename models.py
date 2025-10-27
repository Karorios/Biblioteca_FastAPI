from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

libros_autores = Table(
    "libros_autores",
    Base.metadata,
    Column("libro_id", Integer, ForeignKey("libros.id", ondelete="CASCADE")),
    Column("autor_id", Integer, ForeignKey("autores.id", ondelete="CASCADE"))
)

class Autor(Base):
    __tablename__ = "autores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    pais = Column(String, index=True, nullable=False)
    anio_nacimiento = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True)

    libros = relationship(
        "Libro",
        secondary=libros_autores,
        back_populates="autores"
    )


class Libro(Base):
    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    isbn = Column(String, unique=True, index=True)
    anio_publicacion = Column(Integer)
    copias_disponibles = Column(Integer, default=1)
    cantidad_autores = Column(Integer, default=0)  # ← nuevo campo
    activo = Column(Boolean, default=True)

    autores = relationship(
        "Autor",
        secondary=libros_autores,
        back_populates="libros"
    )

    reservas = relationship("Reserva", back_populates="libro", cascade="all, delete")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    codigo_unico = Column(String, unique=True, nullable=False)
    activo = Column(Boolean, default=True)

    reservas = relationship("Reserva", back_populates="usuario", cascade="all, delete")


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))
    isbn_libro = Column(String, ForeignKey("libros.isbn", ondelete="CASCADE"))
    fecha_reserva = Column(DateTime(timezone=True), server_default=func.now())
    fecha_entrega = Column(DateTime(timezone=True))
    estado = Column(String, default="activa")
    activo = Column(Boolean, default=True)

    nombre_usuario = Column(String, nullable=True)
    nombre_libro = Column(String, nullable=True)

    usuario = relationship("Usuario", back_populates="reservas")
    libro = relationship("Libro", back_populates="reservas")
