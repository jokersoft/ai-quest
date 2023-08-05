from fastapi import APIRouter

from .endpoints import action

router = APIRouter()
router.include_router(action.router, prefix="/action", tags=["Action"])
