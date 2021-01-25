"""S3 integration utils"""
import boto3
from app.core.config import config
from botocore.exceptions import ClientError

aws_access_key_id = config["AWS"]["ID"]
aws_secret_access_key = config["AWS"]["SECRET"]
s3_bucket = config["S3_BUCKET"]


class ImageNotAvailableError(Exception):
    pass


def get_image_from_s3(image_path: str) -> bytes:
    """
    Gets an image from S3

    Args:
        image_path (str): Path to the image inside the bucket

    Raises:
        ImageNotAvailable: If an error occurs when trying to get the image

    Returns:
        bytes: Bytes img
    """
    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        obj = client.get_object(Bucket=s3_bucket, Key=image_path)
        return obj["Body"].read()
    except ClientError as e:
        raise ImageNotAvailableError(e)
