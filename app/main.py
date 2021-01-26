"""Main module for the REST API"""
import logging

from fastapi import FastAPI

from app import exceptions
from app.api import api_router
from app.api import db_integration
from app.core import utils
from app.core.config import config

# Instantiate the FastAPI app with a project name and the endpoint for serving the API
# specification following OpenAPI format
app = FastAPI(
    title=config["PROJECT_NAME"], openapi_url=f"{config['API_PREFIX']}/openapi.json"
)

app.include_router(api_router, prefix=config["API_PREFIX"])


@app.on_event("startup")  # Hook a function to the startup event
async def startup_function():
    """
    Load the PyTorch model at the startup event of the API and assign it to the FastAPI
    instance to be accesible from all workers.

    Raises:
        exceptions.ModelError: When the model cannot be instantiated or the model's
            checkpoint cannot be loaded.
    """
    logging.getLogger().setLevel(logging.INFO)
    try:
        model = utils.load_model(
            config["MODEL"]["PATH"], device=config["MODEL"]["DEVICE"]
        )
    except Exception as e:
        raise exceptions.ModelError(f"Error loading model: {e}")

    app.state.model = model

    db_integration.create_table()
