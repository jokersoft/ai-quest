from fastapi import APIRouter

from .endpoints import init
from .endpoints import action
from .endpoints import messages

router = APIRouter()
router.include_router(init.router, prefix="/init", tags=["Init"])
router.include_router(action.router, prefix="/action", tags=["Action"])
router.include_router(messages.router, prefix="/messages", tags=["Message"])
