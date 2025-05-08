from fastapi import APIRouter, HTTPException, logger
from typing import Optional
from app.database import get_conexion
import bcrypt

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

ROLES_VALIDOS = ["cliente", "vendedor", "contador", "bodeguero", "administrador"]

# Encriptar contraseña
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Verificar contraseña
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@router.get("/login")
def login(email: str, clave: str):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        
        cursor.execute("SELECT rut, nombre, apellido, rol, clave FROM usuario WHERE email = :email", {"email": email})
        usuario = cursor.fetchone()
        cursor.close()
        cone.close()
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        if not verify_password(clave, usuario[4]):
            raise HTTPException(status_code=401, detail="Clave incorrecta")
        
        return {
            "rut": usuario[0],
            "nombre": usuario[1],
            "apellido": usuario[2],
            "rol": usuario[3]
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {ex}")

# -------------------- GET TODOS LOS USUARIOS --------------------
@router.get("/")
def obtener_usuarios():
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("SELECT rut, nombre, apellido, email, telefono, rol FROM usuario")
        usuarios = []
        for rut, nombre, apellido, email, telefono, rol in cursor:
            usuarios.append({
                "rut": rut,
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "telefono": telefono,
                "rol": rol
            })
        cursor.close()
        cone.close()
        return usuarios
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- GET POR RUT --------------------
@router.get("/{rut_buscar}")
def obtener_usuario(rut_buscar: str):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("SELECT nombre, apellido, email, telefono, rol FROM usuario WHERE rut = :rut",
                       {"rut": rut_buscar})
        usuario = cursor.fetchone()
        cursor.close()
        cone.close()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {
            "rut": rut_buscar,
            "nombre": usuario[0],
            "apellido": usuario[1],
            "email": usuario[2],
            "telefono": usuario[3],
            "rol": usuario[4]
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- POST REGISTRO CLIENTE --------------------
@router.post("/registro-cliente")
def registrar_cliente(rut: str, nombre: str, apellido: str, email: str, telefono: int, clave: str):
    if len(str(telefono)) != 9:
        raise HTTPException(status_code=400, detail="El teléfono debe tener 9 dígitos")
    try:
        cone = get_conexion()
        cursor = cone.cursor()

        # Verificar si ya existe el email
        cursor.execute("SELECT 1 FROM usuario WHERE email = :email", {"email": email})
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email ya registrado")

        clave_hash = hash_password(clave)
        cursor.execute("""
            INSERT INTO usuario (rut, nombre, apellido, email, telefono, clave, rol)
            VALUES (:rut, :nombre, :apellido, :email, :telefono, :clave, 'cliente')
        """, {
            "rut": rut, "nombre": nombre, "apellido": apellido, "email": email,
            "telefono": telefono, "clave": clave_hash
        })
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Cliente registrado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- POST REGISTRO ADMIN A TRABAJADOR --------------------
@router.post("/")
def agregar_usuario(rut: str, nombre: str, apellido: str, email: str, telefono: int, clave: str, rol: str):
    if rol.lower() not in ROLES_VALIDOS or rol.lower() == "cliente":
        raise HTTPException(status_code=400, detail="No puedes asignar rol cliente")
    if len(str(telefono)) != 9:
        raise HTTPException(status_code=400, detail="El teléfono debe tener 9 dígitos")
    try:
        cone = get_conexion()
        cursor = cone.cursor()

        # Verificar si ya existe el email
        cursor.execute("SELECT 1 FROM usuario WHERE email = :email", {"email": email})
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email ya registrado")

        clave_hash = hash_password(clave)
        cursor.execute("""
            INSERT INTO usuario
            VALUES(:rut, :nombre, :apellido, :email, :telefono, :clave, :rol)
        """, {
            "rut": rut, "nombre": nombre, "apellido": apellido, "email": email,
            "telefono": telefono, "clave": clave_hash, "rol": rol.lower()
        })
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Usuario registrado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- PUT CAMBIO DE CLAVE --------------------
@router.put("/{rut}")
def actualizar_clave(rut: str, clave_nueva: str):
    try:
        clave_hash = hash_password(clave_nueva)
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("""
            UPDATE usuario SET clave = :clave WHERE rut = :rut
        """, {"clave": clave_hash, "rut": rut})
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Clave actualizada con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- PATCH ACTUALIZACIÓN PARCIAL --------------------
@router.patch("/{rut}")
def actualizar_parcial(rut: str, nombre: Optional[str] = None, apellido: Optional[str] = None,
                       email: Optional[str] = None, telefono: Optional[int] = None):
    try:
        if not any([nombre, apellido, email, telefono]):
            raise HTTPException(status_code=400, detail="Debe enviar al menos un campo")
        campos = []
        valores = {"rut": rut}
        if nombre:
            campos.append("nombre = :nombre")
            valores["nombre"] = nombre
        if apellido:
            campos.append("apellido = :apellido")
            valores["apellido"] = apellido
        if email:
            campos.append("email = :email")
            valores["email"] = email
        if telefono:
            if len(str(telefono)) != 9:
                raise HTTPException(status_code=400, detail="El teléfono debe tener 9 dígitos")
            campos.append("telefono = :telefono")
            valores["telefono"] = telefono
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute(f"""
            UPDATE usuario SET {', '.join(campos)} WHERE rut = :rut
        """, valores)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Usuario actualizado"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- DELETE USUARIO --------------------
@router.delete("/{rut}")
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

# -------------------- LOGIN --------------------
