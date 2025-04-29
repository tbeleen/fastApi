from fastapi import APIRouter, HTTPException
from app.database import get_conexion

#vamos a crear la variable para las rutas:
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

#endpoints: GET, GET, POST, PUT, DELETE, PATCH
@router.get("/")
def obtener_usuarios():
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("SELECT rut,nombre,email FROM alumno")
        usuarios = []
        for rut, nombre, email in cursor:
            usuarios.append({
                "rut": rut,
                "nombre": nombre,
                "email": email
            })
        cursor.close()
        cone.close()
        return usuarios
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/{rut_buscar}")
def obtener_usuario(rut_buscar: int):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("SELECT nombre, email FROM alumno WHERE rut = :rut"
                       ,{"rut": rut_buscar})
        usuario = cursor.fetchone()
        cursor.close()
        cone.close()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {
            "rut": rut_buscar,
            "nombre": usuario[0],
            "email": usuario[1]
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/")
def agregar_usuario(rut:int, nombre:str, email:str):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("""
            INSERT INTO alumno
            VALUES(:rut, :nombre, :email)
        """,{"rut":rut, "nombre":nombre, "email": email})
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Alumno agregado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.put("/{rut_actualizar}")
def actualizar_usuario(rut_actualizar:int, nombre:str, email:str):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("""
                UPDATE alumno
                SET nombre = :nombre, email = :email
                WHERE rut = :rut
        """, {"nombre":nombre, "email":email, "rut":rut_actualizar})
        if cursor.rowcount==0:
            cursor.close()
            cone.close()
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Usuario actualizado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.delete("/{rut_eliminar}")
def eliminar_usuario(rut_eliminar: int):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("DELETE FROM alumno WHERE rut = :rut"
                       ,{"rut": rut_eliminar})
        if cursor.rowcount==0:
            cursor.close()
            cone.close()
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Usuario eliminado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


from typing import Optional

@router.patch("/{rut_actualizar}")
def actualizar_parcial(rut_actualizar:int, nombre:Optional[str]=None, email:Optional[str]=None):
    try:
        if not nombre and not email:
            raise HTTPException(status_code=400, detail="Debe enviar al menos 1 dato")
        cone = get_conexion()
        cursor = cone.cursor()

        campos = []
        valores = {"rut": rut_actualizar}
        if nombre:
            campos.append("nombre = :nombre")
            valores["nombre"] = nombre
        if email:
            campos.append("email = :email")
            valores["email"] = email

        cursor.execute(f"UPDATE alumno SET {', '.join(campos)} WHERE rut = :rut"
                       ,valores)
        if cursor.rowcount==0:
            cursor.close()
            cone.close()
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cone.commit()
        cursor.close()
        cone.close()        
        return {"mensaje": "Usuario actualizado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
