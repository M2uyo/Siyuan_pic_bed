# noqa: F403
from fastapi import APIRouter

from router.cloud import cloud_123

router = APIRouter()

router.include_router(cloud_123.router)
