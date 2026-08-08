# routers/telemetry.py
from fastapi import APIRouter, Depends, HTTPException, Request
import asyncpg
from schemas.telemetry import MachineTelemetry, MachineResponse

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"]
)

async def get_db(request: Request):
    async with request.app.state.db_pool.acquire() as connection:
        yield connection

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
    
    if telemetry.status == 'error':
        log_text = f"⚙️ System failure: {machine_name} [ID: {telemetry.machine_id}]. Error: {telemetry.details} (Load: {telemetry.load_percent}%)"
        await db.execute(
            "INSERT INTO action_logs (telegram_id, action_text, created_at) VALUES (NULL, $1, NOW())", 
            log_text
        )

    return {
        'status': 'success',
        'message': f'Telemetry for {machine_name} updated successfully'
    }

@router.get("/machines", response_model=list[MachineResponse])
async def get_all_machines(db: asyncpg.Connection = Depends(get_db)):
    rows = await db.fetch("SELECT id, name, status, details, load_percent FROM machines ORDER BY id")
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
