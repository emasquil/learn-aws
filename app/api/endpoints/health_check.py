from fastapi import APIRouter, Request

from app.api import models

router = APIRouter()


@router.get("/", response_model=models.HealthCheck)
async def health_check(request: Request):
    """
    Health check of the API.

    Keyword Arguments:
        request {Request} -- The FastAPI Request object associated with the current call

    Returns:
        models.HealthCheck -- JSON dict HealthCheck
    """
    response = {"statusCode": 200}
    return response
