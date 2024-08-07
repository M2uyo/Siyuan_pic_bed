# noqa: F403
from fastapi import APIRouter

from route.cloud import cloud_123

router = APIRouter()

router.include_router(cloud_123.router)
