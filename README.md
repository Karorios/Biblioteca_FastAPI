# API - Sistema de Gestión de Biblioteca

## Objetivo

El propósito de esta API es gestionar los recursos de una biblioteca de manera sencilla y eficiente, permitiendo administrar la información de autores, libros, usuarios y reservas.  
El sistema facilita el registro de usuarios, la creación y consulta de libros y autores, y la gestión de reservas, estableciendo relaciones claras entre las diferentes entidades.

---

## Modelos de Datos

### Autor
Representa a los escritores de los libros registrados en la biblioteca.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | int | Identificador único del autor |
| nombre | str | Nombre completo del autor |
| pais | str | País de origen |
| anio_nacimiento | int | Año de nacimiento |
| activo | bool | Estado activo/inactivo del autor |

**Relación:** Un autor puede tener muchos libros (1:N).

---

### Libro
Contiene la información de los libros disponibles en la biblioteca.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | int | Identificador único del libro |
| isbn | str | Código único que identifica el libro |
| titulo | str | Título del libro |
| anio_publicacion | int | Año de publicación |
| copias_disponibles | int | Número de ejemplares disponibles |
| activo | bool | Estado activo/inactivo del libro |
| autores | relación | Lista de autores asociados |

**Relaciones:**  
- Un libro pertenece a uno o varios autores (N:1 o N:M)  
- Un libro puede tener muchas reservas (1:N)

---

### Usuario
Representa a las personas registradas en el sistema que pueden realizar reservas.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | int | Identificador único del usuario |
| nombre | str | Nombre del usuario |
| codigo_unico | str | Código único de identificación |
| activo | bool | Estado activo/inactivo del usuario |

**Relación:** Un usuario puede realizar muchas reservas (1:N)

---

### Reserva
Registra las solicitudes de los usuarios para reservar un libro en una fecha determinada.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | int | Identificador único de la reserva |
| id_usuario | int | ID del usuario que realiza la reserva |
| isbn_libro | str | ISBN del libro reservado |
| fecha_reserva | datetime | Fecha de la reserva |
| fecha_entrega | datetime | Fecha límite para devolver el libro (15 días después) |
| estado | str | Estado actual de la reserva (activa, finalizada, cancelada) |
| activo | bool | Estado activo/inactivo de la reserva |

**Relaciones:**  
- Una reserva pertenece a un usuario (N:1)  
- Una reserva pertenece a un libro (N:1)

---

## Relaciones del Sistema

| Entidad | Tipo de relación | Descripción |
|---------|-----------------|------------|
| Autor → Libro | 1:N | Un autor puede tener varios libros |
| Libro → Reserva | 1:N | Un libro puede estar asociado a varias reservas |
| Usuario → Reserva | 1:N | Un usuario puede realizar múltiples reservas |
| Libro ↔ Usuario | M:N (implícita) | Un usuario puede reservar muchos libros, y un libro puede ser reservado por varios usuarios (a través de la tabla de reservas) |

---

## Mapa de Endpoints

### Autores

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /autores/ | Crear un nuevo autor |
| GET | /autores/ | Listar todos los autores (opcional filtrar por país) |
| GET | /autores/{autor_id}/libros | Consultar los libros de un autor |
| PUT | /autores/{autor_id} | Actualizar un autor |
| DELETE | /autores/{autor_id} | Eliminar un autor (lógicamente) |

### Libros

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /libros/ | Crear un nuevo libro |
| GET | /libros/ | Listar todos los libros (opcional filtrar por año) |
| GET | /libros/{libro_id} | Consultar libro por ID |
| PUT | /libros/{libro_id} | Actualizar libro |
| DELETE | /libros/{libro_id} | Eliminar libro (lógicamente) |

### Usuarios

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /usuarios/ | Crear un nuevo usuario |
| GET | /usuarios/ | Listar todos los usuarios |
| GET | /usuarios/{usuario_id} | Consultar usuario por ID |
| PUT | /usuarios/{usuario_id} | Actualizar usuario |
| DELETE | /usuarios/{usuario_id} | Eliminar usuario (lógicamente) |

### Reservas

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /reservas/ | Crear una reserva (usuario + libro) |
| GET | /reservas/ | Listar todas las reservas |
| GET | /reservas/{id_reserva} | Consultar reserva por ID |
| PUT | /reservas/{id_reserva} | Actualizar estado de reserva |
| DELETE | /reservas/{id_reserva} | Eliminar reserva (lógicamente) |

### Otros Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | / | Ruta raíz de prueba |
| GET | /endpoints | Listar todos los endpoints disponibles |

