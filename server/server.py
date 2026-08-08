from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncpg
from config import DB_HOST, DB_NAME, DB_PASS, DB_USER, DB_PORT
from routers.telemetry import router as telemetry_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        min_size=5,
        max_size=20
    )
    yield
    await app.state.db_pool.close()

app = FastAPI(
    title='Industrial Control API', 
    version='1.0.0',
    lifespan=lifespan
)

app.include_router(telemetry_router)

@app.get('/')
async def read_root():
    return {
        'status': 'online',
        'system': 'Industrial Telemetry Control',
        'version': '1.0.0'
    }
