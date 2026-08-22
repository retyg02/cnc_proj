from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncpg
from config import DB_HOST, DB_NAME, DB_PASS, DB_USER, DB_PORT, MONGO_HOST, MONGO_PORT, MONGO_DB_NAME
from routers.telemetry import router as telemetry_router
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- НАСТРОЙКА POSTGRESQL (Твой родной код) ---
    app.state.db_pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        min_size=5,
        max_size=20
    )
    
    # --- НАСТРОЙКА MONGODB (Добавляем рядышком) ---
    # Переменные MONGO_HOST, MONGO_PORT, MONGO_DB_NAME импортируй из конфига
    mongo_url = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
    app.state.mongo_client = AsyncIOMotorClient(mongo_url)
    app.state.mongo_db = app.state.mongo_client[MONGO_DB_NAME]

    await app.state.mongo_db.trajectories.create_index(
        "timestamp", 
        expireAfterSeconds=300
    )
    
    
    yield
    
    # --- ЗАКРЫТИЕ КЛИЕНТОВ ПРИ ОСТАНОВКЕ СЕРВЕРА ---
    await app.state.db_pool.close()
    app.state.mongo_client.close()

app = FastAPI(
    title='Industrial Control API',
    version='1.0.0',
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry_router)

@app.get('/')
async def read_root():
    return {
        'status': 'online',
        'system': 'Industrial Telemetry Control',
        'version': '1.0.0'
    }

