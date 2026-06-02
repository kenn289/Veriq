from fastapi import APIRouter

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/ping")
async def ping():
    return {"status": "ok", "service": "agents"}
