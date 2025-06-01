# 🚀 API de Usuarios - FastAPI (FERREMAS)
Este proyecto corresponde a un microservicio desarrollado con **FastAPI**, encargado de la **gestión de usuarios** para la distribuidora de productos de ferretería y construcción **FERREMAS**. Forma parte de un sistema distribuido donde el frontend está construido con Django y los productos son gestionados mediante una API Express.

# 🚀 Características

* Registro y autenticación de usuarios.
* Manejo de contraseñas seguras con `bcrypt`.
* Validación y login con JWT (tokens).
* Integración con base de datos Oracle (Oracle XE / Cloud / 19c).
* Despliegue local mediante `uvicorn`.

# 📦 Requisitos de instalación

Antes de ejecutar el proyecto, asegúrate de tener instalado:

* Python 3.8 o superior
* Oracle Database (local o cloud)
* pip

Instala las dependencias con:

```bash
pip install -r requirements.txt
```
Contenido de requirements.txt:
txt
```
oracledb
bcrypt
passlib[bcrypt]
fastapi[all]
uvicorn

# ⚙️ Configuración de base de datos
Modifica el archivo database.py con tus credenciales Oracle:
``` python
 import oracledb

``` connection = oracledb.connect(
    user="tu_usuario",
    password="tu_contraseña",
    dsn="localhost/XEPDB1"  # o tu configuración en Oracle Cloud
)
# ▶️ Ejecución
Para correr el servidor de desarrollo:
``` bash
 uvicorn app.main:app --reload
```
# 🔒 Seguridad
* 	Las contraseñas se almacenan en la base de datos con hash bcrypt.
*	Se utilizan tokens JWT para autenticación en endpoints protegidos.
# 🧑‍💻 Equipo de desarrollo

Este proyecto fue desarrollado como parte del sistema de digitalización para FERREMAS, por el equipo de desarrollo web contratado para modernizar los procesos post-pandemia.
