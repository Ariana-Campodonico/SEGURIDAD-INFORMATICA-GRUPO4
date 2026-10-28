import importlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory


def _require(condition, message):
    if not condition:
        raise RuntimeError(message)


def ejecutar_pruebas():
    with TemporaryDirectory(prefix="laboratorio_sqli_") as test_directory:
        database_path = Path(test_directory) / "pruebas.db"
        previous_database_path = os.environ.get("APP_DATABASE_PATH")
        os.environ["APP_DATABASE_PATH"] = str(database_path)
        try:
            create_app = importlib.import_module("app_vulnerable").create_app
        finally:
            if previous_database_path is None:
                os.environ.pop("APP_DATABASE_PATH", None)
            else:
                os.environ["APP_DATABASE_PATH"] = previous_database_path

        app = create_app(
            database_path=database_path,
            demo_username="usuario_prueba",
            demo_password="clave_prueba_local",
        )
        app.config["TESTING"] = True
        client = app.test_client()

        acceso_valido = client.post(
            "/login",
            data={
                "username": "usuario_prueba",
                "password": "clave_prueba_local",
                "mode": "secure",
            },
        )
        _require(
            b"Acceso concedido" in acceso_valido.data,
            "Falló el inicio de sesión con credenciales válidas.",
        )

        payload = {
            "username": "' OR '1'='1' -- comentario",
            "password": "incorrecta",
        }
        resultado_vulnerable = client.post(
            "/login", data={**payload, "mode": "vulnerable"}
        )
        _require(
            b"Acceso concedido" in resultado_vulnerable.data,
            "El modo vulnerable no reprodujo el bypass esperado.",
        )

        resultado_mitigado = client.post(
            "/login", data={**payload, "mode": "secure"}
        )
        _require(
            b"Acceso denegado" in resultado_mitigado.data
            and b"Acceso concedido" not in resultado_mitigado.data,
            "La consulta parametrizada no rechazó el payload.",
        )
        _require(
            b"username = ?" in resultado_mitigado.data,
            "La respuesta de mitigación no muestra la consulta parametrizada.",
        )

        print(
            "Pruebas correctas: login válido, bypass ilustrativo en modo vulnerable "
            "y rechazo del mismo payload en modo parametrizado."
        )


if __name__ == "__main__":
    ejecutar_pruebas()
