from fastapi import APIRouter, HTTPException
from typing import Optional
from app.database import get_conexion

router = APIRouter(
    prefix="/despacho",
    tags=["Despacho"]
)

# -------------------- GET TODOS LOS DESPACHOS --------------------
@router.get("/")
def obtener_despachos():
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("SELECT id, rut_usuario, tipo, direccion, sucursal FROM tipo_despacho")
        despachos = []
        for id_, rut, tipo, direccion, sucursal in cursor:
            despachos.append({
                "id": id_,
                "rut_usuario": rut,
                "tipo": tipo,
                "direccion": direccion,
                "sucursal": sucursal
            })
        cursor.close()
        cone.close()
        return despachos
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- GET POR RUT --------------------
@router.get("/usuario/{rut}")
def obtener_despachos_por_usuario(rut: str):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("""
            SELECT id, tipo, direccion, sucursal
            FROM tipo_despacho
            WHERE rut_usuario = :rut
        """, {"rut": rut})
        resultados = cursor.fetchall()
        cursor.close()
        cone.close()

        if not resultados:
            raise HTTPException(status_code=404, detail="No se encontraron despachos para este usuario")

        return [
            {
                "id": id_,
                "tipo": tipo,
                "direccion": direccion,
                "sucursal": sucursal
            } for id_, tipo, direccion, sucursal in resultados
        ]
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- POST NUEVO DESPACHO --------------------
@router.post("/")
def crear_despacho(rut_usuario: str, tipo: str, direccion: Optional[str] = None, sucursal: Optional[str] = None):
    if tipo not in ['entrega domicilio', 'retiro en tienda']:
        raise HTTPException(status_code=400, detail="Tipo de despacho inválido")

    if tipo == 'entrega domicilio' and (not direccion or sucursal):
        raise HTTPException(status_code=400, detail="Debe proporcionar solo una dirección para entrega a domicilio")

    if tipo == 'retiro en tienda' and (not sucursal or direccion):
        raise HTTPException(status_code=400, detail="Debe proporcionar solo una sucursal para retiro en tienda")

    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("""
            INSERT INTO tipo_despacho (rut_usuario, tipo, direccion, sucursal)
            VALUES (:rut, :tipo, :direccion, :sucursal)
        """, {
            "rut": rut_usuario,
            "tipo": tipo,
            "direccion": direccion,
            "sucursal": sucursal
        })
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Despacho registrado correctamente"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# -------------------- DELETE DESPACHO POR ID --------------------
@router.delete("/{id_despacho}")
def eliminar_despacho(id_despacho: int):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("DELETE FROM tipo_despacho WHERE id = :id", {"id": id_despacho})
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Despacho no encontrado")
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Despacho eliminado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
