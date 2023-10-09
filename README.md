# ComicShop
Prueba técnica de microservicios en Python 3.11.0 con FastAPI y Arquitectura Hexagonal.

## Contenido

- [Comic Shop Microservices](#comicshop)
	- [Contenido](#contenido)
	- [Microservicios](#microservicios)
		- [Microservicio: Comic Details](#microservicio-comic-details)
		- [Microservicio: User Auth](#microservicio-user-auth)
		- [Microservicio: Layaway](#microservicio-layaway)
	- [Docker](#docker)

---

## Microservicios

El proyecto cuenta con 3 microservicios los cuales son API REST:
* Microservicio: comicDetails (Puerto 8002)
* Microservicio: userAuth (Puerto 8000)
* Microservicio: layaway (Puerto 8001)

---

### Microservicio: Comic Details

Este microservicio está enfocado en la búsqueda de cómics. Es alimentado por la API de Marvel y consta de 5 funcionalidades:
* Listado Completo de Personajes.
* Búsqueda por palabra (Cómics y Personajes).
* Búsqueda por nombre de personaje.
* Búsqueda de cómic por título, fecha y número.
* Búsqueda por ID (Cómics y Personajes).

Detalles de cada punto:

1\. Listado de todos los *Personajes* de Marvel (de la A a la Z):
* GET: **/catalogs/api/v1/records?page={page}**

Al no tener ningún criterio de búsqueda, se obtienen los personajes existentes.

Al tener tantos registros es posible utilizar el query param `page` para indicar un número de página a obtener, cada página contiene un máximo de 100 registros.

Resultados en `data` (200 OK):
```json
{
    "page": 0,
    "count": 100,
	"characters": [
        {
            "id": 1011334,
            "name": "3-D Man",
            "image": "http://i.annihil.us/u/prod/marvel/i/mg/c/e0/535fecbbb9784.jpg",
            "appearances": 12
        },
        {
            "id": 1017100,
            "name": "A-Bomb (HAS)",
            "image": "http://i.annihil.us/u/prod/marvel/i/mg/3/20/5232158de5b16.jpg",
            "appearances": 4
        },
        ...
    ]
}
```

2\. Búsqueda por alguna Palabra coincidente:
* GET: **/catalogs/api/v1/records?contains={word}&page={page}**

Entrega todos los *Cómics* y *Personajes* que comiencen por esa palabra.

Ejemplo:
* GET: **/catalogs/api/v1/records?contains=deadpool&page=0**

Resultados en `data` (200 OK):
```json
{
    "page": 0,
    "count": 104,
    "count_comics": 100,
    "count_characters": 4,
    "comics": [
        {
            "id": 48611,
            "title": "Deadpool (2012) #23",
            "image": "http://i.annihil.us/u/prod/marvel/i/mg/9/03/5286584b0490c.jpg",
            "on_sale_date": "2014-02-12T00:00:00-0500"
        },
        ...
	],
    "characters": [
        {
            "id": 1009268,
            "name": "Deadpool",
            "image": "http://i.annihil.us/u/prod/marvel/i/mg/9/90/5261a86cacb99.jpg",
            "appearances": 910
        },
		...
	]
}
```

Se entrega los Personajes y los Cómics por separado y contadores de elementos.

3\. Filtro por Nombre de Personaje (nombre específico):
* GET: **/catalogs/api/v1/records?character={word}**

Ejemplo:
* GET: **/catalogs/api/v1/records?character=peter parker**

Resultados en `data` (200 OK):
```json
{
    "character": {
        "id": 1009491,
        "name": "Peter Parker",
        "image": "http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available.jpg",
        "appearances": 198
    }
}
```

4\. Filtro por *Título* (título, fecha y número de Cómic):
* GET: **/catalogs/api/v1/records?comic={title}&date={date}&number={number}**

Ejemplo:
* GET: **/catalogs/api/v1/records?comic=spider-man&date=2022&number=1**

Resultados en `data` (200 OK):
```json
{
    "title": "spider-man",
    "number": 1,
    "year": 2022,
    "comic": {
        "id": 99743,
        "title": "Spider-Man (2022) #1",
        "image": "http://i.annihil.us/u/prod/marvel/i/mg/c/10/633cefa06d1f4.jpg",
        "on_sale_date": "2022-10-05T00:00:00-0400"
    }
}
```

5\. Filtro por *ID* (título, fecha y número de Cómic):
* GET: **/catalogs/api/v1/records/{id}**

Ejemplo:
* GET: **/catalogs/api/v1/records/99743**

Entrega un *Cómic* o *Personaje* con el *ID*.

Resultados en `data` (200 OK):
```json
{
    "comic": {
        "id": 99743,
        "title": "Spider-Man (2022) #1",
        "image": "http://i.annihil.us/u/prod/marvel/i/mg/c/10/633cefa06d1f4.jpg",
        "on_sale_date": "2022-10-05T00:00:00-0400"
    }
}
```

---

### Microservicio: User Auth

Este microservicio está enfocado en la administración de usuarios y consta de 3 funcionalidades:

* Crear un Usuario.
* Login: Obtiene un Token de Usuario.
* Validar un Token.

Detalles de cada punto:

1\. Creación de un Usuario sin requisitos. Esta funcionalidad permite que cualquier usuario se registre en la base de datos:
* POST: **/users/api/v1/singup**

Ejemplo (Body):
```json
{
    "name": "kevin",
    "age": 27,
    "username": "kev14",
    "password": "Toypelon1."
}
```

Resultados en `data` (201 CREATED):
```json
{
    "message": "Usuario kev14 creado con éxito"
}
```

2\. Para obtener una sesión de usuario, debe hacerse login y se obtendrá un Token:
* POST: **/users/api/v1/login**

Ejemplo (Body):
```json
{
    "username": "kev14",
    "password": "Toypelon1."
}
```

Resultados en `data` (200 OK):
```json
{
    "message": "Usuario kev14 logueado con éxito"
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOnsiaWQiOiI5NWM0MDM0M2NhMjE0M2I0YTBmMzYyMzdk"
}
```

3\. Obtener un listado detallado de la información del usuario utilizando un token:
* GET: **/users/api/v1/keys**
* Headers:
    * **Authorization: Bearer {Token}**

Resultados de `data` (200 OK):
```json
{
    "id": "95c40343ca2143b4a0f36237d4a533be",
    "username": "kev14"
}
```

---

### Microservicio: Layaway

Este microservicio está enfocado en agregar Cómics a la lista de Apartados del Usuario y cuenta con 1 funcionalidad:

* Agregar un Cómic a la Lista de Apartados.
* Listado de todos los Apartados por el Usuario en orden de inserción.
* Listado con ordenamiento por Orden alfabético o fecha.

Requiere un Token y un body que contenga el ID del cómic que se desea agregar. El ID lo podemos obtener con el microservicio de búsqueda (Search Cómics) y el token con el microservicio de usuarios (Users).

Ejemplo:

Agregaré el Cómic de Spider-Man #1 con ID '10767' (obtenido en el ejemplo de búsqueda de un cómic en específico).

* POST: **/orders/api/v1/layaway**
* Headers:
    * **Authorization: Bearer {Token}**

```json
{
	"comic_id": 10767
}
```

Resultados de `data` (201 CREATED):
```json
{
    "message": "El usuario {username} tiene el comic {comic_id} en su apartado"
}
```

Este microservicio está enfocado en la obtención de todos los Cómics Apartados por el Usuario y consta de 2 Funcionalidades:

2\. El listado mostrará todos los apartados en el orden de inserción de los datos.

Ejemplo:

* GET: **/orders/api/v1/layaway**
* Headers:
    * **Authorization: Bearer \<Token\>**

Resultados de `data` (200 OK):
```json
{
    "user_id": "51ad703d72a5496396eddd4c6c51a1ec",
      "comics": [
        {
          "id": 2,
          "title": "X-Man 1",
          "image": "http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available.jpg",
          "on_sale_date": "2010-10-30T00:00:00-0500"
        },
        {
          "id": 3,
          "title": "Spider man 2",
          "image": "http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available.jpg",
          "on_sale_date": "2020-10-30T00:00:00-0500"
        },
        {
          "id": 82967,
          "title": "Marvel Previews (2017)",
          "image": "http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available.jpg",
          "on_sale_date": "2099-10-30T00:00:00-0500"
        }
      ]
}
```

3\. El listado con filtro se puede utilizar de la siguiente manera:

Filtros:
* `alphabetically`
* `date`

GET: **/orders/api/v1/layaway?date=bool**

Ejemplo:

Filtrar por orden alfabético (title):

* GET: **/orders/api/v1/layaway?alphabetically=true**
* Headers:
    * **Authorization: Bearer \<Token\>**

Resultados de `data` (200 OK):
```json
{
    "user_id": "51ad703d72a5496396eddd4c6c51a1ec",
      "comics": [
        {
          "id": 82967,
          "title": "Marvel Previews (2017)",
          "image": "http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available.jpg",
          "on_sale_date": "2099-10-30T00:00:00-0500"
        },
        {
          "id": 3,
          "title": "Spider man 2",
          "image": "http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available.jpg",
          "on_sale_date": "2020-10-30T00:00:00-0500"
        },
        {
          "id": 2,
          "title": "X-Man 1",
          "image": "http://i.annihil.us/u/prod/marvel/i/mg/b/40/image_not_available.jpg",
          "on_sale_date": "2010-10-30T00:00:00-0500"
        }
      ]
}
```

---

## Docker

Para correr todas las imagenes:

Docker Compose:

    docker-compose up
