from pydantic import BaseModel, Field

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

class UpdateMachineCommand(BaseModel):
    command: str = Field(..., description="New command (STOP, RESET, PAUSE)", max_length=50, example="STOP")