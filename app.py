import os
import time

import pymysql
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# Datos de conexión: llegan por variables de entorno (docker run -e ...)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "damian-db"),   # nombre del contenedor de la BD
    "user": os.getenv("DB_USER", "damian"),
    "password": os.getenv("DB_PASSWORD", "damian123"),
    "database": os.getenv("DB_NAME", "registro"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def conectar():
    return pymysql.connect(**DB_CONFIG)


def crear_tabla():
    """La BD tarda unos segundos en arrancar, por eso reintentamos."""
    for intento in range(1, 31):
        try:
            con = conectar()
            try:
                with con.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS registros (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            nombre VARCHAR(100) NOT NULL,
                            edad INT NOT NULL,
                            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                con.commit()
            finally:
                con.close()
            print("Conectado a la base de datos y tabla lista.", flush=True)
            return
        except pymysql.err.OperationalError as e:
            print(f"Intento {intento}: la BD aún no responde ({e}). Reintentando...", flush=True)
            time.sleep(2)
    raise RuntimeError("No se pudo conectar a la base de datos.")


PLANTILLA = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DockerLab | Registro</title>
  <style>
    * { box-sizing: border-box; }
    body { margin:0; font-family:'Segoe UI',sans-serif; background:#101827; color:#e5edf7;
           min-height:100vh; display:flex; justify-content:center; padding:20px; }
    .container { width:100%; max-width:650px; background:#1c293b; border:1px solid #34445b;
                 border-radius:18px; padding:40px; box-shadow:0 15px 40px rgba(0,0,0,.25); }
    .tag { color:#42c8ed; font-size:12px; text-transform:uppercase; letter-spacing:2px; }
    h1 { color:white; margin:10px 0 20px; }
    label { display:block; color:#a9b8ca; font-size:14px; margin:14px 0 6px; }
    input { width:100%; padding:12px; border-radius:9px; border:1px solid #34445b;
            background:#101827; color:white; font-size:15px; }
    button { margin-top:20px; padding:12px 20px; background:#159bc4; color:white; border:none;
             border-radius:9px; font-weight:600; cursor:pointer; }
    button:hover { background:#087da4; }
    .error { color:#fca5a5; margin-top:12px; }
    table { width:100%; border-collapse:collapse; margin-top:15px; font-size:14px; }
    th, td { text-align:left; padding:10px; border-bottom:1px solid #34445b; }
    th { color:#42c8ed; }
    .divider { height:1px; background:#34445b; margin:30px 0; }
    .footer { margin-top:30px; text-align:center; color:#718198; font-size:12px; }
    @media (max-width: 480px) { .container { padding:25px; } }
  </style>
</head>
<body>
  <main class="container">
    <div class="tag">🐳 Docker Lab · Flask + MariaDB</div>
    <h1>¡Yo estudio en el Yavirac!</h1>

    <form method="POST" action="/guardar">
      <label for="nombre">Nombre</label>
      <input id="nombre" name="nombre" required maxlength="100" placeholder="Ej: Damián">

      <label for="edad">Edad</label>
      <input id="edad" name="edad" type="number" min="1" max="120" required placeholder="Ej: 21">

      <button type="submit">Guardar en la base de datos</button>
      {% if error %}<p class="error">{{ error }}</p>{% endif %}
    </form>

    <div class="divider"></div>

    <div class="tag">Datos guardados ({{ registros|length }})</div>
    <table>
      <tr><th>#</th><th>Nombre</th><th>Edad</th><th>Fecha</th></tr>
      {% for r in registros %}
        <tr><td>{{ r.id }}</td><td>{{ r.nombre }}</td><td>{{ r.edad }}</td><td>{{ r.fecha }}</td></tr>
      {% else %}
        <tr><td colspan="4">Aún no hay registros.</td></tr>
      {% endfor %}
    </table>

    <footer class="footer">
      Taller de Tendencias Actuales de Programación
      <br><br>
      Desarrollado con Python + Flask + MariaDB + Docker
    </footer>
  </main>
</body>
</html>
"""


def obtener_registros():
    con = conectar()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT id, nombre, edad, fecha FROM registros ORDER BY id DESC")
            return cur.fetchall()
    finally:
        con.close()


@app.route("/")
def inicio():
    return render_template_string(PLANTILLA, registros=obtener_registros(), error=None)


@app.route("/guardar", methods=["POST"])
def guardar():
    nombre = request.form.get("nombre", "").strip()
    edad = request.form.get("edad", "").strip()

    if not nombre or not edad.isdigit():
        return render_template_string(PLANTILLA, registros=obtener_registros(),
                                      error="Escribe un nombre y una edad válida.")

    con = conectar()
    try:
        with con.cursor() as cur:
            # %s = consulta parametrizada (evita inyección SQL)
            cur.execute("INSERT INTO registros (nombre, edad) VALUES (%s, %s)",
                        (nombre, int(edad)))
        con.commit()
    finally:
        con.close()

    return redirect("/")   # patrón POST -> redirect -> GET


if __name__ == "__main__":
    crear_tabla()
    app.run(host="0.0.0.0", port=5000)
