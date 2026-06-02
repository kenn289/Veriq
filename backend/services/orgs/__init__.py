from fastapi import APIRouter

router = APIRouter(prefix="/orgs", tags=["orgs"])


@router.get("/ping")
async def ping():
    return {"status": "ok", "service": "orgs"}
