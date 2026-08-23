from pydantic import BaseModel, Field
from datetime import datetime

class MachineTelemetry(BaseModel):
    machine_id: int = Field(..., description="Machine ID in the system", example=1)
    status: str = Field(..., description="Machine current status (working, idle, error)", example="working")
    load_percent: int = Field(..., description="Load percent", ge=0, le=100, example=85)
    details: str | None = Field(None, description="Additional description or error text", example="Hot temperature")

class MachineResponse(BaseModel):
    id: int
    name: str
    status: str
    load_percent: int
    details: str | None = None
    current_command: str | None = None
    session_id: str | None = None
    gcode_path: str | None = None

class UpdateMachineCommand(BaseModel):
    command: str = Field(..., description="New command (STOP, RESET, PAUSE)", max_length=50, example="STOP")

class MachineCoords(BaseModel):
    machine_id: int
    x: float
    y: float
    z: float
    is_cutting: bool
    session_id: str
    timestamp: datetime

class MachineLogPayload(BaseModel):
    machine_id: int
    action_text: str

class SessionPayload(BaseModel):
    session_id: str
