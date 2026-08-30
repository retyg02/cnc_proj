from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncpg
from config import DB_HOST, DB_NAME, DB_PASS, DB_USER, DB_PORT, MONGO_HOST, MONGO_PORT, MONGO_DB_NAME
from routers.telemetry import router as telemetry_router
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi.responses import JSONResponse


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
    
    
    mongo_url = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
    app.state.mongo_client = AsyncIOMotorClient(mongo_url)
    app.state.mongo_db = app.state.mongo_client[MONGO_DB_NAME]

    await app.state.mongo_db.trajectories.create_index(
        "timestamp", 
        expireAfterSeconds=300
    )
    
    
    yield
    
    
    await app.state.db_pool.close()
    app.state.mongo_client.close()

app = FastAPI(
    title='Industrial Control API',
    version='1.0.0',
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        'version': '0.9.0'
    }



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    
    print(f"[PYDANTIC VALIDATION ERROR]: {exc.errors()}")
    print(f"[RAW BODY]: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(await request.body())}
    )