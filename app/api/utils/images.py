import base64
import io

import torch
import torchvision.transforms.functional as TF
from app.exceptions import InvalidImage
from PIL import Image, UnidentifiedImageError
from torchvision.transforms import ToTensor

_to_tensor = ToTensor()


def bytes_to_image(b: bytes) -> Image:
    """
    Transforms the bytes from an image into a PIL Image.

    Arguments:
        b {bytes} -- image bytes

    Raises:
        InvalidImage: Exception raised when PIL cannot load the bytes into an Image

    Returns:
            PIL.Image -- Resulting PIL Image from loading the image bytes
    """
    b = io.BytesIO(b)
    try:
        return Image.open(b, mode="r")
    except UnidentifiedImageError:
        raise InvalidImage("Invalid image format")


def preprocess_image(image: Image) -> torch.Tensor:
    """
    Transforms an image for being processed through the ML model.

    Arguments:
        image {PIL.Image} -- PIL Image to be transformed.

    Returns:
        torch.Tensor -- Tensor of dimensions (H, W, C) representing the transformed
            image.
    """
    image = TF.resize(image, 512)
    return _to_tensor(image)


def base64_to_image(base64_image: str) -> Image:
    """
    Converts an image encoded in base64 format to a PIL Image.

    Arguments:
        base64_image {str} -- The image encoded in base64 format.

    Returns:
        PIL.Image -- The resulting PIL Image
    """
    decoded = base64.b64decode(base64_image)
    stream = io.BytesIO(decoded)
    image = Image.open(stream)
    return image


def image_to_base64(image: Image, output_format="PNG") -> str:
    """
    Encodes a PIL Image using base64 encoding following the specified output format.

    Arguments:
        image {PIL.Image} -- The PIL Image to be converted.

    Keyword Arguments:
        output_format {str} -- Image format to be used as output. (default: {"PNG"})

    Returns:
        str -- The encoded image in base64 format.
    """
    stream = io.BytesIO()
    image.save(stream, format=output_format)
    encoded = base64.b64encode(stream.getvalue()).decode("ascii")
    return encoded
