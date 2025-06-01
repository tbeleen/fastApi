import email
import hashlib
from fastapi import APIRouter, Body, HTTPException, Path, logger
from typing import Optional

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.database import get_conexion
import bcrypt

router = APIRouter()

ROLES_VALIDOS = ["cliente", "vendedor", "contador", "bodeguero", "administrador"]

# Encriptar contraseña
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Verificar contraseña
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# -------------------- LOGIN --------------------
from pydantic import BaseModel
from passlib.context import CryptContext
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    clave: str

@router.get("/login")
def login_usuario(email: str, clave: str):
    print(f"Login intent: email={email}, clave={clave}")
    try:
        cone = get_conexion()
        print("Conexión a DB exitosa.")
        cursor = cone.cursor()

        cursor.execute("""
            SELECT rut, nombre, email, clave, rol, requiere_cambio
            FROM usuario
            WHERE email = :email
        """, {"email": email})
        print("Consulta ejecutada.")

        row = cursor.fetchone()
        print(f"Resultado fetchone: {row}")

        cursor.close()
        cone.close()

        if not row:
            print("Usuario no encontrado.")
            raise HTTPException(status_code=401, detail="Email o clave incorrectos")

        rut, nombre, email_db, clave_hash, rol, requiere_cambio = row
        print(f"Datos del usuario: rut={rut}, nombre={nombre}, email_db={email_db}, hash={clave_hash}, rol={rol}, requiere_cambio={requiere_cambio}")

        if not pwd_context.verify(clave, clave_hash):
            print("Clave incorrecta.")
            raise HTTPException(status_code=401, detail="Email o clave incorrectos")

        print("Login exitoso.")
        return {
            "rut": rut,
            "nombre": nombre,
            "email": email_db,
            "rol": rol,
            "requiere_cambio": requiere_cambio
        }

    except Exception as ex:
        print(f"Error inesperado: {ex}")
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(ex)}")



# -------------------- CAMBIO DE CLAVE admin --------------------   
from pydantic import BaseModel

class CambioClave(BaseModel):
    email: str
    nueva_clave: str

@router.put("/cambiar-clave")
def cambiar_clave(data: CambioClave):
    try:
        clave_hash = hash_password(data.nueva_clave)
        cone = get_conexion()
        cursor = cone.cursor()

        cursor.execute("""
            UPDATE usuario
            SET clave = :clave, requiere_cambio = 0
            WHERE email = :email
        """, {"clave": clave_hash, "email": data.email})

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        cone.commit()
        cursor.close()
        cone.close()

        return {"mensaje": "Clave actualizada con éxito"}

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- GET TODOS LOS USUARIOS --------------------
@router.get("/usuarios")
def obtener_usuarios():
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("SELECT u.rut," \
        "                      u.nombre, " \
        "                      u.apellido, " \
        "                      u.email, " \
        "                      u.telefono, " \
        "                      u.rol, " \
        "                      c.descripcion " \
        "               FROM usuario u" \
        "               JOIN comuna c ON u.id_comuna = c.id_comuna")
        usuarios = []
        for rut, nombre, apellido, email, telefono, rol, comuna in cursor:
            usuarios.append({
                "rut": rut,
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "telefono": telefono,
                "rol": rol,
                "comuna": comuna
            })
        cursor.close()
        cone.close()
        return usuarios
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- GET POR RUT --------------------
@router.get("/comuna")
def obtener_comunas():
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("SELECT id_comuna, descripcion FROM comuna")
        comunas = []
        for id_comuna, descripcion in cursor:
            comunas.append({
                "id_comuna": id_comuna,
                "descripcion": descripcion
            })
        cursor.close()
        cone.close()
        return comunas
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
# -------------------- GET ADMINISTRADORES --------------------
@router.get("/administrador")
def obtener_administradores():
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("""
            SELECT rut, nombre, email, rol
            FROM usuario
            WHERE LOWER(rol) = 'administrador'
        """)
        admins = []
        for rut, nombre, email, rol in cursor:
            admins.append({
                "rut": rut,  # Asumiendo que rut es el primer campo
                "nombre": nombre,
                "email": email,
                "rol": rol
            })
        cursor.close()
        cone.close()
        return admins
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
# -------------------- GET POR RUT --------------------
@router.get("/usuario/{rut_buscar}")
def obtener_usuario(rut_buscar: str):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute(
            "SELECT u.rut, u.nombre, u.apellido, u.email, u.telefono, u.rol, u.id_comuna, c.descripcion "
            "FROM usuario u "
            "JOIN comuna c ON u.id_comuna = c.id_comuna "
            "WHERE u.rut = :rut",
            {"rut": rut_buscar}
        )
        usuario = cursor.fetchone()
        cursor.close()
        cone.close()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {
            "rut": usuario[0],
            "nombre": usuario[1],
            "apellido": usuario[2],
            "email": usuario[3],
            "telefono": usuario[4],
            "rol": usuario[5],
            "id_comuna": usuario[6],    # <-- agregamos el ID
            "comuna": usuario[7]        # <-- el nombre para mostrar si quieres
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- POST REGISTRO CLIENTE --------------------
@router.post("/registro-cliente")
def registrar_cliente(rut: str, nombre: str, apellido: str, email: str, telefono: int, clave: str, id_comuna: int):
    if len(str(telefono)) != 9:
        raise HTTPException(status_code=400, detail="El teléfono debe tener 9 dígitos")
    try:
        cone = get_conexion()
        cursor = cone.cursor()

        # Verificar si ya existe el email
        cursor.execute("SELECT 1 FROM usuario WHERE email = :email", {"email": email})
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email ya registrado")

        # Verificar si ya existe el RUT
        cursor.execute("SELECT 1 FROM usuario WHERE rut = :rut", {"rut": rut})
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="RUT ya registrado")

        clave_hash = hash_password(clave)
        cursor.execute("""
            INSERT INTO usuario (rut, nombre, apellido, email, telefono, clave, rol, id_comuna)
            VALUES (:rut, :nombre, :apellido, :email, :telefono, :clave, 'cliente', :id_comuna)
        """, {
            "rut": rut, "nombre": nombre, "apellido": apellido, "email": email,
            "telefono": telefono, "clave": clave_hash, "id_comuna": id_comuna
        })
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Cliente registrado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))



# -------------------- POST REGISTRO ADMIN A TRABAJADOR --------------------
from pydantic import BaseModel

class TrabajadorRequest(BaseModel):
    rut: str
    nombre: str
    apellido: str
    email: str
    telefono: int
    clave: str
    rol: str
    id_comuna: int

@router.post("/registro-trabajador")
def agregar_usuario(data: TrabajadorRequest):
    if data.rol.lower() not in ROLES_VALIDOS or data.rol.lower() == "cliente":
        raise HTTPException(status_code=400, detail="No puedes asignar rol cliente")
    if len(str(data.telefono)) != 9:
        raise HTTPException(status_code=400, detail="El teléfono debe tener 9 dígitos")
    try:
        cone = get_conexion()
        cursor = cone.cursor()

        cursor.execute("SELECT 1 FROM usuario WHERE email = :email", {"email": data.email})
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email ya registrado")

        clave_hash = hash_password(data.clave)

        cursor.execute("""
            INSERT INTO usuario (
                rut, nombre, apellido, email, telefono, clave, rol, id_comuna, requiere_cambio
            ) VALUES (
                :rut, :nombre, :apellido, :email, :telefono, :clave, :rol, :id_comuna, 1
            )
        """, {
            "rut": data.rut,
            "nombre": data.nombre,
            "apellido": data.apellido,
            "email": data.email,
            "telefono": data.telefono,
            "clave": clave_hash,
            "rol": data.rol.lower(),
            "id_comuna": data.id_comuna
        })

        cone.commit()
        return {"mensaje": "Usuario registrado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        cone.close()
    # -------------------- POST REGISTRO ADMIN --------------------
from pydantic import BaseModel

class AdminRequest(BaseModel):
    rut: str
    nombre: str
    email: str
    clave: str
@router.post("/registro-administrador")
def registrar_administrador(admin: AdminRequest):
    try:
        cone = get_conexion()
        cursor = cone.cursor()

        # Validar que no exista el email
        cursor.execute("SELECT 1 FROM usuario WHERE email = :email", {"email": admin.email})
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email ya registrado")

        clave_hash = hash_password(admin.clave)

        cursor.execute("""
            INSERT INTO usuario (
                rut, nombre, apellido, email, telefono, clave, rol, id_comuna, requiere_cambio
            ) VALUES (
                :rut, :nombre, :apellido, :email, :telefono, :clave, 'administrador', :id_comuna, 1
            )
        """, {
            "rut": admin.rut,
            "nombre": admin.nombre,
            "apellido": "-",  # Valor requerido
            "email": admin.email,
            "telefono": None,       # Aceptable solo si la columna permite NULL
            "clave": clave_hash,
            "id_comuna": None       # Aceptable solo si la columna permite NULL
        })

        cone.commit()
        return {"mensaje": "Administrador registrado con éxito"}
    
    except Exception as ex:
        print("", str(ex))
        raise HTTPException(status_code=500, detail="Error interno: " + str(ex))
    
    finally:
        try:
            cursor.close()
            cone.close()
        except:
            pass


# -------------------- PATCH ACTUALIZACIÓN PARCIAL --------------------
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    rol: Optional[str] = None
    id_comuna: Optional[int] = None

@router.patch("/modificar/{rut}")
async def modificar_usuario(rut: str = Path(...), usuario: UsuarioUpdate = Body(...)):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        
        # Verificar si el usuario existe
        cursor.execute("SELECT rut FROM usuario WHERE rut = :rut", {"rut": rut})
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Construir query dinámicamente
        campos = []
        valores = {}
        for field, value in usuario.dict(exclude_unset=True).items():
            campos.append(f"{field} = :{field}")
            valores[field] = value

        if not campos:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

        valores["rut"] = rut
        sql = f"UPDATE usuario SET {', '.join(campos)} WHERE rut = :rut"
        cursor.execute(sql, valores)
        cone.commit()
        
        return {"detail": "Usuario actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(ex)}")
    finally:
        cursor.close()
        cone.close()

# -------------------- DELETE USUARIO --------------------
@router.delete("/eliminar/{rut}")
def eliminar_usuario(rut: str):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("DELETE FROM usuario WHERE rut = :rut", {"rut": rut})
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Usuario eliminado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    
class PasswordUpdate(BaseModel):
    clave: str

@router.get("/buscar-usuario-por-email/")
def buscar_usuario_por_email(email: str):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute(
            "SELECT u.rut, u.nombre, u.apellido, u.email, u.telefono, u.rol, u.id_comuna, c.descripcion "
            "FROM usuario u "
            "JOIN comuna c ON u.id_comuna = c.id_comuna "
            "WHERE LOWER(u.email) = LOWER(:email)",
            {"email": email}
        )
        usuario = cursor.fetchone()
        cursor.close()
        cone.close()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {
            "rut": usuario[0],
            "nombre": usuario[1],
            "apellido": usuario[2],
            "email": usuario[3],
            "telefono": usuario[4],
            "rol": usuario[5],
            "id_comuna": usuario[6],
            "comuna": usuario[7]
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.patch("/modificar-clave/{rut}")
def modificar_clave_usuario(rut: str, datos: PasswordUpdate):
    try:
        conn = get_conexion()
        cursor = conn.cursor()

        # Verificar usuario
        cursor.execute("SELECT rut FROM usuario WHERE rut = :rut", {"rut": rut})
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Hashear con bcrypt (igual que en login)
        clave_hash = pwd_context.hash(datos.clave)
        
        # Actualizar en BD
        cursor.execute(
            "UPDATE usuario SET clave = :clave WHERE rut = :rut",
            {"clave": clave_hash, "rut": rut}
        )
        conn.commit()
        
        return {"message": "Contraseña actualizada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

class PasswordUpdate(BaseModel):
    nueva_contrasena: str
