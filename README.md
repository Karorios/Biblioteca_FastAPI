# API - Sistema de Gestión de Biblioteca

## Objetivo

El propósito de esta API es gestionar los recursos de una biblioteca de manera sencilla y eficiente, permitiendo administrar la información de autores, libros, usuarios y reservas. 
El sistema facilita el registro de usuarios, la creación y consulta de libros y autores, y la gestión de reservas, estableciendo relaciones claras entre las diferentes entidades.

## Modelos de Datos

### Autor
Representa a los escritores de los libros registrados en la biblioteca.

Campo | Tipo | Descripción
------|------|-------------
id | int | Identificador único del autor
nombre | str | Nombre completo del autor
pais_origen | str | País de origen
anio_nacimiento | int | Año de nacimiento

Relación: Un autor puede tener muchos libros (1:N).

### Libro
Contiene la información de los libros disponibles en la biblioteca.

Campo | Tipo | Descripción
------|------|-------------
isbn | str | Código único que identifica el libro
titulo | str | Título del libro
anio_publicacion | int | Año en que fue publicado
num_copias | int | Número de ejemplares disponibles
genero | str | Género literario (novela, ciencia, historia, etc.)
autor_id | int | ID del autor correspondiente

Relaciones:
- Un libro pertenece a un autor (N:1)  
- Un libro puede tener muchas reservas (1:N)

### Usuario
Representa a las personas registradas en el sistema que pueden realizar reservas.

Campo | Tipo | Descripción
------|------|-------------
id | int | Identificador único del usuario
nombre | str | Nombre del usuario
historial_reservas | relación | Conjunto de reservas asociadas al usuario

Relación: Un usuario puede realizar muchas reservas (1:N)

### Reserva
Registra las solicitudes de los usuarios para reservar un libro en una fecha determinada.

Campo | Tipo | Descripción
------|------|-------------
id_reserva | int | Identificador único de la reserva
id_usuario | int | ID del usuario que realiza la reserva
isbn_libro | str | ISBN del libro reservado
fecha_reserva | date | Fecha en la que se realiza la reserva
fecha_entrega | date | Fecha límite para devolver el libro (15 días después de la reserva)
estado | str | Estado actual de la reserva (activa, cancelada, completada)
nombre_usuario | str | Nombre del usuario que reservó
nombre_libro | str | Título del libro reservado

Relaciones:
- Una reserva pertenece a un usuario (N:1)  
- Una reserva pertenece a un libro (N:1)

## Relaciones del Sistema

Entidad | Tipo de relación | Descripción
--------|------------------|-------------
Autor → Libro | 1:N | Un autor puede tener varios libros
Libro → Reserva | 1:N | Un libro puede estar asociado a varias reservas
Usuario → Reserva | 1:N | Un usuario puede realizar múltiples reservas
Libro ↔ Usuario | M:N (implícita) | Un usuario puede reservar muchos libros, y un libro puede ser reservado por varios usuarios (a través de la tabla de reservas)

## Mapa de Endpoints

### Autores
Método | Ruta | Descripción
--------|------|-------------
POST | /autores/ | Crear un nuevo autor
GET | /autores/ | Listar todos los autores
GET | /autores/{id} | Consultar un autor por ID

### Libros
Método | Ruta | Descripción
--------|------|-------------
POST | /libros/ | Registrar un nuevo libro
GET | /libros/ | Listar todos los libros
GET | /libros/{isbn} | Consultar libro por ISBN

### Usuarios
Método | Ruta | Descripción
--------|------|-------------
POST | /usuarios/ | Registrar un nuevo usuario
GET | /usuarios/ | Listar todos los usuarios
GET | /usuarios/{id} | Consultar usuario por ID

### Reservas
Método | Ruta | Descripción
--------|------|-------------
POST | /reservas/ | Crear una reserva (usuario + libro)
GET | /reservas/ | Listar todas las reservas
GET | /reservas/{id} | Consultar reserva por ID

## Resumen General

- Los autores registran la información de los escritores disponibles en el sistema.  
- Los libros pertenecen a un autor y pueden ser reservados por los usuarios.  
- Los usuarios deben estar registrados para poder realizar reservas.  
- Las reservas asocian usuarios con libros e incluyen fechas de reserva y entrega, junto con el estado actual.  
- La relación entre usuarios y libros se establece de manera muchos a muchos (M:N) mediante el modelo Reserva.
