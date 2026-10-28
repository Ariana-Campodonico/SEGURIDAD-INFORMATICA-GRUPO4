# Manual de uso

## 1. Preparar el entorno

Requiere Python 3.10 o posterior. En PowerShell, abre la carpeta del proyecto y
ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell impide activar el entorno virtual, puedes invocar directamente
`.\.venv\Scripts\python.exe` en los comandos siguientes.

## 2. Iniciar la aplicación

Opcionalmente, define una cuenta sintética distinta para la demostración:

```powershell
$env:APP_DEMO_USERNAME = "demo"
$env:APP_DEMO_PASSWORD = "Demo1234!"
```

Inicia Flask:

```powershell
python .\app_vulnerable.py
```

Visita <http://127.0.0.1:5000>. La aplicación solo escucha en loopback. La
cuenta de demostración se muestra en la página, ya que el propósito del proyecto
es académico y local; no uses una contraseña real.

La aplicación crea `laboratorio_sqli.db` en la carpeta del proyecto. Para usar
otra ruta, define `APP_DATABASE_PATH` antes de iniciar. El archivo de base se
ignora en Git para evitar publicar datos generados localmente.

## 3. Comparar SQL Injection y mitigación

1. En el formulario, elige el modo **Vulnerable: concatenación**.
2. Escribe el siguiente valor como usuario y cualquier texto como contraseña:

   ```text
   ' OR '1'='1' -- comentario
   ```

3. Envía el formulario. La consulta vulnerable se construye concatenando los
   campos y el comentario SQL descarta la comprobación de la contraseña. El
   laboratorio debe mostrar acceso concedido y la consulta construida.
4. Repite con **Mitigado: consulta parametrizada**. El mismo valor debe ser
   rechazado; la página muestra los marcadores `?`, no incorpora el dato a la
   instrucción SQL.
5. Prueba la cuenta sintética correcta en modo mitigado. Debe iniciar sesión
   correctamente.

El modo vulnerable solo existe para reproducir el problema en este ejercicio.
No reutilices esa técnica en sistemas ajenos; realiza pruebas únicamente en el
laboratorio local.

## 4. Ejecutar las pruebas automatizadas

Con el entorno virtual activo:

```powershell
python .\ataque_sql_i.py
```

La prueba usa el cliente de Flask y una base temporal: no necesita que el
servidor esté iniciado ni contacta otros equipos. Comprueba:

- que un inicio de sesión válido sea aceptado;
- que el payload didáctico obtenga acceso en el modo vulnerable;
- que el mismo payload sea rechazado en el modo parametrizado.

La salida esperada es similar a:

```text
Pruebas correctas: login válido, bypass ilustrativo en modo vulnerable y rechazo del mismo payload en modo parametrizado.
```

## 5. Verificar puertos locales

En otra terminal, ejecuta:

```powershell
python .\escaneo_red.py
```

El programa comprueba una lista fija de puertos TCP en `127.0.0.1`, entre ellos
el puerto 5000 de Flask. Para limitar el ejercicio, la función rechaza
direcciones que no sean IP de loopback y puertos fuera del intervalo válido.
Un puerto que aparece como “CERRADO / FILTRADO” simplemente no aceptó la
conexión dentro del tiempo límite.

## 6. Detener y limpiar

Detén el servidor con `Ctrl+C`. La base local se puede conservar para el
siguiente inicio o eliminar manualmente si ya no la necesitas; no la subas al
repositorio. El escáner no instala servicios ni modifica la configuración de
red.

## Solución de problemas

- **`ModuleNotFoundError: No module named 'flask'`:** activa `.venv` e instala
  las dependencias con `python -m pip install -r requirements.txt`.
- **El puerto 5000 ya está ocupado:** detén la otra aplicación que lo usa antes
  de iniciar este laboratorio.
- **El login de demostración no funciona:** comprueba que las credenciales
  introducidas coincidan con las que muestra la página. Si cambiaste variables
  de entorno, reinicia el servidor.
- **La prueba no inicia:** ejecútala desde la carpeta del proyecto y confirma
  que las dependencias estén instaladas.

## Alcance de seguridad

Este proyecto no es un sistema de autenticación de producción. En particular,
el modo vulnerable y la cuenta sintética simplificada solo sirven para
demostrar el efecto de concatenar SQL. Mantén el servidor en loopback y no
almacenes información personal o secretos reales en esta aplicación.
