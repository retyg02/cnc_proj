from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
import asyncpg
from schemas.telemetry import MachineTelemetry, MachineResponse, UpdateMachineCommand, MachineCoords, MachineLogPayload, SessionPayload
import shutil
import os
from config import ONEC_API_KEY
from datetime import datetime
from pathlib import Path


router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"]
)

api_key_header = APIKeyHeader(name="X-1C-API-Key")

async def get_db(request: Request):
    async with request.app.state.db_pool.acquire() as connection:
        yield connection

async def get_mongo_db(request: Request):
    return request.app.state.mongo_db

@router.post("")
async def receive_telemetry(telemetry: MachineTelemetry, db: asyncpg.Connection = Depends(get_db)):
    machine = await db.fetchrow("SELECT name, status FROM machines WHERE id = $1", telemetry.machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    machine_name = machine['name']

    update_query = """
        UPDATE machines 
        SET status = $1, load_percent = $2, details = $3 
        WHERE id = $4
    """
    await db.execute(update_query, telemetry.status, telemetry.load_percent, telemetry.details, telemetry.machine_id)
    
    # if telemetry.status == 'error':
    #     log_text = f"⚙️ System failure: {machine_name} [ID: {telemetry.machine_id}]. Error: {telemetry.details} (Load: {telemetry.load_percent}%)"
    #     await db.execute(
    #         "INSERT INTO action_logs (telegram_id, action_text, created_at) VALUES (NULL, $1, NOW())", 
    #         log_text
    #     )

    return {
        'status': 'success',
        'message': f'Telemetry for {machine_name} updated successfully'
    }

@router.get("/machines", response_model=list[MachineResponse])
async def get_all_machines(db: asyncpg.Connection = Depends(get_db)):
    rows = await db.fetch("SELECT id, name, status, details, load_percent, current_command, session_id, gcode_path FROM machines ORDER BY id")
    return [dict(row) for row in rows]


@router.get("/machines/{machine_id}", response_model=MachineResponse)
async def get_single_machine(machine_id: int, db: asyncpg.Connection = Depends(get_db)):
    row = await db.fetchrow(
        "SELECT id, name, status, details, load_percent FROM machines WHERE id = $1", 
        machine_id
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"Machine with ID {machine_id} not found")
    return dict(row)

@router.post("/machines/{machine_id}/upload-gcode")
async def upload_gcode(
    machine_id: int,
    file: UploadFile = File(...),
    db: asyncpg.Connection = Depends(get_db)
):
    machine = await db.fetchrow("SELECT name FROM machines WHERE id = $1", machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    current_file = Path(__file__).resolve()
    SERVER_DIR = current_file.parent.parent
    UPLOAD_DIR = SERVER_DIR.parent / "g-code"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / f"machine_{machine_id}.nc"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    await db.execute(
        "UPDATE machines SET gcode_path = $1 WHERE id = $2",
        f'machine_{machine_id}.nc', machine_id
    )
    return {
        'status': 'success',
        'message': f"G-code file for machine {machine_id} was uploaded successfully",
        'saved_path': str(file_path.resolve())
    }

@router.get("/machines/{machine_id}/download_g-code")
async def download_gcode(
    machine_id: int,
    db: asyncpg.Connection = Depends(get_db)
):
    gcode_path = await db.fetchval(
        "SELECT gcode_path FROM machines WHERE id = $1",
        machine_id
    )
    if not gcode_path:
        raise HTTPException(status_code=404, detail="G-code program for machine {machine_id} wasn't found or uploaded yet")
    if not os.path.exists(gcode_path):
        raise HTTPException(status_code=404, detail="G-code file missing on server hard drive")
    return FileResponse(
        path=gcode_path,
        media_type="text/plain",
        filename=f"machine_{machine_id}.gcode"
    )

@router.get("/machines/{machine_id}/command")
async def get_machine_command(
    machine_id: int,
    db: asyncpg.Connection = Depends(get_db)
):
    command = await db.fetchval(
        "SELECT current_command FROM machines WHERE id = $1",
        machine_id
    )
    if command is None:
        raise HTTPException(status_code=404, detail="Machine wasn't found or it's not had a command")
    return {
        'machine_id': machine_id,
        'command': command
    }

@router.post("/machines/{machine_id}/set_command")
async def set_command(
    machine_id: int,
    payload: UpdateMachineCommand,
    db: asyncpg.Connection = Depends(get_db)
):
    print(f"[TRACE 2.2] FastAPI принял команду. Machine: {machine_id}, Command: {payload.command}")
    command = payload.command
    current_machine = await db.fetchval(
        "SELECT name FROM machines WHERE id = $1",
        machine_id
    )
    if not current_machine:
        raise HTTPException(status_code=404, detail="Current machine doesn't exist")
    await db.execute(
        "UPDATE machines SET current_command = $1 WHERE id = $2",
        command, machine_id
    )
    return {
        'machine_id': machine_id,
        'command': command,
        'status': 'success'
    }

@router.get("/analytics")
async def get_analytics(
    db: asyncpg.Connection = Depends(get_db)
):
    total_machines = await db.fetchval("SELECT count(*) FROM machines")
    status_counts = await db.fetch("SELECT status, count(*) as count FROM machines GROUP BY status")

    analytics = {
        'total': total_machines,
        'working': 0,
        'idle': 0,
        'error': 0
    }
    for record in status_counts:
        row = dict(record)
        analytics[row['status']] = row['count']
    return analytics

@router.get('/onec/reports')
async def get_onec_report(
    api_key: str = Depends(api_key_header),
    db: asyncpg.Connection = Depends(get_db)
):
    if api_key != ONEC_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid 1C Api Key. Access denied.")
    rows = await db.fetch(
        "SELECT id, created_at, telegram_id, action_text FROM action_logs ORDER BY created_at DESC LIMIT 50"
    )
    logs_report = []
    for record in rows:
        row = dict(record)
        if row['created_at']:
            row['created_at'] = row['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        logs_report.append(row)
    return {
        'system': 'Control API',
        'target': '1C',
        'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'logs_count': len(logs_report),
        'data': logs_report
    }

@router.post('/machines/coords')
async def post_coords(
    telemetry: MachineCoords,
    db = Depends(get_mongo_db) # Подтягиваем нашу зависимость
):
    coords_dict = telemetry.dict()
    
    # Вставляем данные в асинхронную коллекцию trajectories
    result = await db.trajectories.insert_one(coords_dict)
    
    return {
        "status": "COORDINATES_SAVED",
        "mongo_id": str(result.inserted_id)
    }


@router.get('/coordinates/{session_id}')
async def get_coordinates_by_session(
    session_id: str,
    db = Depends(get_mongo_db)
):
    # Ищем в Монго все документы, у которых session_id равен запрошенному
    cursor = db.trajectories.find({"session_id": session_id}).sort("timestamp", 1)
    
    # Собираем все документы из курсора в обычный Python-список (максимум 1000 точек)
    points = await cursor.to_list(length=1000)
    
    if not points:
        return []
        
    # Форматируем ответ для Vue, убирая внутренний монговский ObjectId (он не сериализуется в JSON)
    formatted_points = []
    for p in points:
        formatted_points.append({
            "machine_id": p["machine_id"],
            "x": p["x"],
            "y": p["y"],
            "z": p["z"],
            "is_cutting": p["is_cutting"],
            "timestamp": p["timestamp"].isoformat() if hasattr(p["timestamp"], "isoformat") else str(p["timestamp"])
        })
        
    return formatted_points

@router.post('/machines/log')
async def post_log(
    telemetry: MachineLogPayload,
    db: asyncpg.Connection = Depends(get_db)
):
    await db.execute(
        "INSERT INTO machine_logs (machine_id, action_text) VALUES ($1, $2)", 
        telemetry.machine_id, telemetry.action_text
    )
    
    return {
        'status': 'success',
        'machine_id': telemetry.machine_id
    }

@router.post('/machines/{machine_id}/set_session')
async def set_machine_session(
    machine_id: int, 
    payload: SessionPayload, 
    db = Depends(get_db)
):        
    print(f"[TRACE 2.1] FastAPI принял сессию. Machine: {machine_id}, Session_ID: {payload.session_id}")
    await db.execute("UPDATE machines SET session_id = $1 WHERE id = $2;", 
        payload.session_id, 
        machine_id
    )
    return {"status": "SESSION_INITIALIZED"}
