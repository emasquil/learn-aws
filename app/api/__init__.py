from fastapi import APIRouter

from app.api.endpoints import predict, health_check

api_router = APIRouter()
# api_router.include_router(predict.router, prefix="/predict", tags=["predict"])
api_router.include_router(health_check.router, tags=["health check"])
