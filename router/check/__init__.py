# noqa: F403
from fastapi import APIRouter

from router.check import local, remote

router = APIRouter()

router.include_router(local.router, prefix="/local")
router.include_router(remote.router, prefix="/remote")
