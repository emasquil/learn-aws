from typing import Dict, Union

import PIL
import torch
from app.api import db_integration
from app.api import models as api_models
from app.api import s3_integrations
from app.api.utils import evaluation as evaluation_utils
from app.api.utils import images as image_utils
from fastapi import APIRouter, File, HTTPException, Request
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()


def classify(
    image: PIL.Image, model: torch.nn.Module, image_id: str = "Unknown"
) -> Dict[str, Union[str, float]]:
    """
    Classifies the input `image` using the specified `model`.

    Arguments:
        image {PIL.Image} -- Input image to be classified.
        model {torch.nn.Module} -- PyTorch model used to classify the image.

    Returns:
        Dict[str, Union[str, float]] -- Dictionary with the classification result.
    """
    image = image_utils.preprocess_image(image)
    with torch.no_grad():
        logits = model(image.unsqueeze(0))
    classification_result = evaluation_utils.to_result_dict(logits)
    db_integration.insert_prediction(image_id, classification_result["label"])
    return evaluation_utils.to_result_dict(logits)


@router.post("/file", response_model=api_models.ClassificationResult)
async def classify_file(request: Request, image: bytes = File(...)):
    """
    Clasifies an image as dog or cat. The input image is received as a stream of bytes.

    Arguments:
        request {Request} -- The user request.

    Keyword Arguments:
        image {bytes} -- Input image (as bytes) to be classified.

    Raises:
        HTTPException: When the input image could not be loaded.

    Returns:
        models.ClassificationResult -- JSON object with the classification result.
    """
    try:
        image = image_utils.bytes_to_image(image)
    except Exception:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Error loading input image",
        )
    return classify(image, request.app.state.model)


@router.post("/s3", response_model=api_models.ClassificationResult)
async def classify_s3(request: Request, data: api_models.InputImage):
    """
    Clasifies an image as dog or cat. The input image is hosted in S3.

    Arguments:
        request {Request} -- The user request.

    Keyword Arguments:
        image {str} -- Path to the image in S3.

    Raises:
        HTTPException: When the input image could not be loaded.

    Returns:
        models.ClassificationResult-- JSON object with the classification result.
    """
    s3_path = data.image
    try:
        image = s3_integrations.get_image_from_s3(s3_path)
    except s3_integrations.ImageNotAvailableError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Image not found in S3",
        )
    try:
        image = image_utils.bytes_to_image(image)
    except Exception:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Error decoding input image",
        )
    return classify(image, request.app.state.model, s3_path)
