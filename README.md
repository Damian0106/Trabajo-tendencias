# Trabajo Tendencias: Flask + MariaDB con Docker

Aplicación web en **Python + Flask** con un formulario (nombre y edad) que guarda los datos en una base de datos **MariaDB**. Cada parte corre en su propio contenedor Docker. Los contenedores se comunican mediante una **red** y los datos se guardan en un **volumen**.

Taller de Tendencias Actuales de Programación, Yavirac.

## Arquitectura

```
Navegador ──▶ localhost:5000
                  │  (ports 5000:5000)
   ┌──────────────┼──────── red: damian-red ───────────────┐
   │              ▼                                         │
   │   ┌──────────────────┐   host "db":3306   ┌──────────┐ │
   │   │ web (Flask)      │ ─────────────────▶ │ db       │ │
   │   │ damian-web       │                    │ MariaDB  │ │
   │   └──────────────────┘                    └────┬─────┘ │
   └─────────────────────────────────────────────────┼──────┘
                                                     │ /var/lib/mysql
                                           volumen: damian-datos
```

- **Red `damian-red`**: los contenedores se encuentran por su nombre (`db`) gracias al DNS interno de Docker.
- **Volumen `damian-datos`**: los archivos de MariaDB se guardan fuera del contenedor, así que los datos persisten aunque se borre o recree el contenedor.
- La base de datos **no** publica puertos: solo es accesible desde la red interna.

## Archivos

| Archivo | Descripción |
|---|---|
| `app.py` | Aplicación Flask: formulario, `INSERT` y `SELECT` en la tabla `registros` |
| `requirements.txt` | Dependencias: `flask`, `PyMySQL` |
| `Dockerfile` | Construye la imagen de la app |
| `docker-compose.yml` | Define los servicios `web`, `db` y `adminer`, la red y el volumen |

## Cómo ejecutarlo

Requisito: Docker Desktop (o Docker con Compose).

```bash
docker compose up -d --build
```

- App: http://localhost:5000
- Adminer (panel de la BD): http://localhost:8080 (servidor `db`, usuario `damian`, contraseña `damian123`, base `registro`)

Ver los datos guardados desde la terminal:

```bash
docker exec -it damian-db mariadb -u damian -pdamian123 registro -e "SELECT * FROM registros;"
```

Detener todo (los datos se conservan en el volumen):

```bash
docker compose down
```

## Sin Docker Compose (comandos manuales)

```bash
docker network create damian-red
docker volume create damian-datos

docker run -d --name damian-db --network damian-red \
  -v damian-datos:/var/lib/mysql \
  -e MARIADB_ROOT_PASSWORD=root123 -e MARIADB_DATABASE=registro \
  -e MARIADB_USER=damian -e MARIADB_PASSWORD=damian123 \
  mariadb:11

docker build -t damian-app .

docker run -d --name damian-web --network damian-red -p 5000:5000 \
  -e DB_HOST=damian-db -e DB_USER=damian -e DB_PASSWORD=damian123 -e DB_NAME=registro \
  damian-app
```

> Las contraseñas de este proyecto son de ejemplo para uso académico. No las uses en producción.
