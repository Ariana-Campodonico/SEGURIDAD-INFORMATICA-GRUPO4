from contextlib import closing
import os
import sqlite3
from pathlib import Path

from flask import Flask, render_template_string, request


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = BASE_DIR / "laboratorio_sqli.db"
DEFAULT_DEMO_USERNAME = "demo"
DEFAULT_DEMO_PASSWORD = "Demo1234!"

HTML_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Laboratorio local de SQL Injection</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }
        main { max-width: 760px; margin: 24px auto; padding: 24px; background: #1e293b; border-radius: 12px; }
        h1, h2 { color: #38bdf8; }
        .warning { padding: 12px; background: #713f12; border-radius: 6px; }
        label { display: block; margin-top: 14px; }
        input[type=text], input[type=password] { box-sizing: border-box; width: 100%; padding: 10px; margin-top: 6px; }
        button { margin-top: 18px; padding: 10px 16px; }
        .result { margin-top: 18px; padding: 12px; border-radius: 6px; background: #334155; overflow-wrap: anywhere; }
        pre { white-space: pre-wrap; overflow-wrap: anywhere; }
    </style>
</head>
<body>
<main>
    <h1>Laboratorio educativo de SQL Injection</h1>
    <p class="warning">
        Solo para pruebas en tu propio equipo. El modo vulnerable es intencional y
        no debe exponerse a Internet ni usarse con datos reales.
    </p>
    <p>Cuenta de demostración: <code>{{ demo_username }}</code> / <code>{{ demo_password }}</code></p>
    <form method="post" action="/login">
        <label for="username">Usuario</label>
        <input id="username" type="text" name="username" maxlength="128" required>
        <label for="password">Contraseña</label>
        <input id="password" type="password" name="password" maxlength="256" required>
        <fieldset>
            <legend>Modo de consulta</legend>
            <label>
                <input type="radio" name="mode" value="secure" checked>
                Mitigado: consulta parametrizada
            </label>
            <label>
                <input type="radio" name="mode" value="vulnerable">
                Vulnerable: concatenación (solo demostración local)
            </label>
        </fieldset>
        <button type="submit">Probar inicio de sesión</button>
    </form>
    {% if message %}
    <section class="result" aria-live="polite">
        <h2>{{ message }}</h2>
        <p>Modo probado: {{ mode_label }}</p>
        {% if query %}
        <p>Consulta de demostración:</p>
        <pre>{{ query }}</pre>
        {% endif %}
    </section>
    {% endif %}
</main>
</body>
</html>
"""


def create_app(database_path=None, demo_username=None, demo_password=None):
    """Create the local teaching app and initialize its isolated demo database."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    app.config["DATABASE"] = str(
        database_path
        or os.environ.get("APP_DATABASE_PATH", DEFAULT_DATABASE)
    )
    app.config["DEMO_USERNAME"] = (
        demo_username
        or os.environ.get("APP_DEMO_USERNAME", DEFAULT_DEMO_USERNAME)
    )
    app.config["DEMO_PASSWORD"] = (
        demo_password
        or os.environ.get("APP_DEMO_PASSWORD", DEFAULT_DEMO_PASSWORD)
    )

    def initialize_database():
        database = Path(app.config["DATABASE"])
        database.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(database)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS demo_users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    INSERT INTO demo_users (username, password, role)
                    VALUES (?, ?, ?)
                    ON CONFLICT(username) DO UPDATE SET
                        password = excluded.password,
                        role = excluded.role
                    """,
                    (
                        app.config["DEMO_USERNAME"],
                        app.config["DEMO_PASSWORD"],
                        "Demostración",
                    ),
                )

    initialize_database()

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def home():
        return render_template_string(
            HTML_TEMPLATE,
            demo_username=app.config["DEMO_USERNAME"],
            demo_password=app.config["DEMO_PASSWORD"],
            message=None,
            mode_label=None,
            query=None,
        )

    @app.post("/login")
    def login():
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        mode = request.form.get("mode", "secure")
        vulnerable_mode = mode == "vulnerable"

        if mode not in {"secure", "vulnerable"}:
            return "Modo de prueba no válido.", 400
        if len(username) > 128 or len(password) > 256:
            return "Los datos ingresados superan el límite permitido.", 400

        try:
            with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
                if vulnerable_mode:
                    query = (
                        "SELECT username, role FROM demo_users "
                        f"WHERE username = '{username}' AND password = '{password}'"
                    )
                    user = connection.execute(query).fetchone()
                    displayed_query = query
                else:
                    query = (
                        "SELECT username, role FROM demo_users "
                        "WHERE username = ? AND password = ?"
                    )
                    user = connection.execute(query, (username, password)).fetchone()
                    displayed_query = (
                        "SELECT username, role FROM demo_users "
                        "WHERE username = ? AND password = ? "
                        "(los valores se envían como parámetros separados)"
                    )
        except sqlite3.Error:
            app.logger.exception("Error SQL en el laboratorio local.")
            user = None
            displayed_query = (
                "La consulta produjo un error; no se muestran detalles internos."
            )

        if user:
            message = f"Acceso concedido: {user[0]} (rol: {user[1]})."
        else:
            message = "Acceso denegado: credenciales incorrectas o consulta inválida."

        return render_template_string(
            HTML_TEMPLATE,
            demo_username=app.config["DEMO_USERNAME"],
            demo_password=app.config["DEMO_PASSWORD"],
            message=message,
            mode_label="Vulnerable (concatenación)" if vulnerable_mode else "Mitigado (parametrizado)",
            query=displayed_query,
        )

    return app


app = create_app()


if __name__ == "__main__":
    print("Laboratorio local: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
