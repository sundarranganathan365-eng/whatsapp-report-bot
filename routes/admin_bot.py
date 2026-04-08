import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter
from pydantic import BaseModel

from services.config_service import config_service

router = APIRouter(prefix="/admin/bot", tags=["Admin - Bot Config"])

class BotConfigUpdate(BaseModel):
    is_active: bool
    default_reply: str

@router.get("/config")
def get_config():
    return {"status": "success", "data": config_service.get_config()}

@router.post("/config")
def update_config(config: BotConfigUpdate):
    updated = config_service.update_config(config.model_dump())
    return {"status": "success", "data": updated}
