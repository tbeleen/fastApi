from fastapi import FastAPI
from app.routers import usuarios, despacho, pago

app = FastAPI(
    title="API de gestión de usuarios",
    version="1.0.0",
    description="API para gestionar usuario usando FastAPI y Oracle"
)

#Traeremos lo de las rutas(routers):
app.include_router(usuarios.router, prefix="/usuarios")
app.include_router(pago.router)
app.include_router(despacho.router)


