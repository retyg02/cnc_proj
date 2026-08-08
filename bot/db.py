import asyncpg
import datetime
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS


async def get_machines_telemetry() -> list:
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    try:
        rows = await conn.fetch("SELECT id, name, status, details, load_percent FROM machines ORDER BY id")
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def get_user_from_db(telegram_id: int) -> dict | None:    
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )    
    try:
        row = await conn.fetchrow(
            "SELECT name, role, alerts_enabled FROM users WHERE telegram_id = $1", 
            telegram_id
        )
        return dict(row) if row else None
    finally:
        await conn.close()

async def register_guest(telegram_id: int, name: str, phone: str) -> bool:
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    try:
        await conn.execute(
            "INSERT INTO users (telegram_id, name, role, phone) VALUES ($1, $2, 'guest', $3) ON CONFLICT (telegram_id) DO NOTHING",
            telegram_id, name, phone
        )
        return True
    finally:
        await conn.close()

async def update_user_role(telegram_id: int, new_role: str) -> bool:
    conn = await asyncpg.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
    )
    try:
        await conn.execute(
            "UPDATE users SET role = $1 WHERE telegram_id = $2",
            new_role, telegram_id
        )
        return True
    finally:
        await conn.close()

async def toggle_user_alert(telegram_id: int) -> bool:
    conn = await asyncpg.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME
        )
    try:
        current = await conn.fetchval("SELECT alerts_enabled FROM users WHERE telegram_id = $1", telegram_id)        
        new_status = not current if current is not None else False        
        await conn.execute("UPDATE users SET alerts_enabled = $1 WHERE telegram_id = $2", new_status, telegram_id)
        return new_status
    finally:
        await conn.close()

async def get_broken_machines_to_alert() -> list:
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    try:
        errors = await conn.fetch("SELECT id, name, details FROM machines WHERE status = 'error'")
        machines_to_alert = []
        for m in errors:
            m_id = m['id']
            last_sent = await conn.fetchval("SELECT last_sent_at FROM sent_alerts WHERE machine_id = $1", m_id)
            if last_sent:
                time_passed = datetime.datetime.now() - last_sent.replace(tzinfo=None)
                if time_passed < datetime.timedelta(minutes=4):
                    continue
            machines_to_alert.append(dict(m))
            await conn.execute(
                "INSERT INTO sent_alerts (machine_id, last_sent_at) VALUES ($1, NOW()) ON CONFLICT (machine_id) DO UPDATE SET last_sent_at = NOW()", m_id
            )
        return machines_to_alert
    finally:
        await conn.close()

async def get_active_admins() -> list:
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    try:
        rows = await conn.fetch("SELECT telegram_id FROM users WHERE role = 'admin' AND alerts_enabled = TRUE")
        return [r['telegram_id'] for r in rows]
    finally:
        await conn.close()


async def get_system_action_logs() -> list:
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    try:
        rows = await conn.fetch("SELECT created_at, telegram_id, action_text FROM action_logs ORDER BY created_at DESC")
        return [dict(row) for row in rows]
    finally:
        await conn.close()
