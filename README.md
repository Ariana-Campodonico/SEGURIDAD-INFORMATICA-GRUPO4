# Laboratorio educativo de seguridad web

Proyecto académico local para observar una vulnerabilidad de SQL Injection en
un formulario de autenticación, comparar la mitigación con consultas
parametrizadas y comprobar puertos de loopback.

> **Advertencia:** `app_vulnerable.py` incluye intencionalmente un modo
> vulnerable para aprendizaje. La aplicación se enlaza únicamente a
> `127.0.0.1`. No la expongas a Internet, no la despliegues en producción y no
> uses datos personales ni contraseñas reales.

## Requisitos

- Python 3.10 o posterior.
- pip.

## Instalación en Windows

Desde PowerShell, en la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python .\app_vulnerable.py
```

Abre <http://127.0.0.1:5000>. La cuenta sintética inicial es `demo` /
`Demo1234!`. Puedes definir `APP_DEMO_USERNAME` y `APP_DEMO_PASSWORD` antes de
iniciar el servidor para usar otros valores. No guardes credenciales reales en
el código ni en Git.

## Pruebas y demostración

Ejecuta la prueba local, que utiliza una base temporal y no envía tráfico a la
red:

```powershell
python .\ataque_sql_i.py
```

En el navegador, selecciona el modo **Vulnerable** y prueba este usuario con
cualquier contraseña:

```text
' OR '1'='1' -- comentario
```

La aplicación de laboratorio mostrará el acceso concedido. Repite el intento
seleccionando **Mitigado**: el inicio de sesión debe ser rechazado porque el
contenido se trata como un valor y no como parte de la consulta SQL. Luego
prueba el usuario y contraseña de demostración en modo mitigado para confirmar
que un acceso válido sigue funcionando.

El script automatizado valida tanto el bypass del laboratorio vulnerable como
el rechazo del mismo dato por la consulta parametrizada.

## Escáner local

```powershell
python .\escaneo_red.py
```

El escáner solo admite direcciones IP de loopback y tiene una lista de puertos
locales predeterminada. No acepta nombres de host ni direcciones de otros
equipos. Un resultado “CERRADO / FILTRADO” significa que no se pudo establecer
la conexión; el script no determina cuál de esas causas aplica.

## Archivos

- `app_vulnerable.py`: aplicación Flask, base SQLite aislada y los dos modos de
  consulta para comparación académica.
- `ataque_sql_i.py`: prueba automatizada local con cliente de pruebas Flask y
  una base temporal.
- `escaneo_red.py`: verificador educativo de puertos limitado a loopback.
- `MANUAL_USO.md`: instrucciones paso a paso, resultados esperados y solución
  de problemas.
- `requirements.txt`: dependencias de Python.

La base de datos `laboratorio_sqli.db` se crea al iniciar la aplicación. La
configuración de `.gitignore` evita subir bases de datos, entornos virtuales,
archivos de claves y secretos.
