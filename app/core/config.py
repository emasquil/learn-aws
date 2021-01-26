import logging
import os
from copy import deepcopy
from typing import Dict

import boto3
import yaml
from app import exceptions
from botocore.exceptions import ClientError
from fastapi.logger import logger

BASE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "base_config.yml")
USER_CONFIG_PATH = "config.yml"

ENVIRONMENT = os.getenv("ENVIRONMENT", "DEV")

AWS_ENV_PATH = "/prod"

# Logging settings
if ENVIRONMENT == "PROD":
    # When running the api with Gunicorn
    gunicorn_logger = logging.getLogger("gunicorn.error")
    logger.handlers = gunicorn_logger.handlers
    logger.setLevel(gunicorn_logger.level)
else:
    # When running the API with Uvicorn
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")


def get_aws_env(key):
    client = boto3.client("ssm")
    try:
        if key == "DATABASE_PASSWORD":
            response = client.get_parameter(
                Name=os.path.join(AWS_ENV_PATH, key), WithDecryption=True
            )
        else:
            response = client.get_parameter(Name=os.path.join(AWS_ENV_PATH, key))
        parameter = response.get("Parameter")
        return parameter.get("Value")
    except ClientError as e:
        logger.error(f"Parameter {key} not found: {e}")


def parse_env(value, key):
    if type(value) is str and value.startswith("$"):
        if ENVIRONMENT == "DEV":
            value = os.getenv(value[1:])
        elif ENVIRONMENT == "PROD":
            value = get_aws_env(value[1:])
        else:
            raise ValueError("Environment must be one of [PROD, DEV]")
    elif type(value) is dict:
        value.update({k: parse_env(v, k) for k, v in value.items()})
    return value


def merge_configs(
    base_config: Dict[str, object], override_config: Dict[str, object]
) -> Dict[str, object]:
    """
    Combines two configuration dictionaries overriding the keys of the first one when
    they are present on the second one. The override is made in depth.

    Arguments:
        base_config {Dict[str, object]} -- Configuration dict to be override.
        override_config {Dict[str, object]} -- Configuration dict to override the base
            dictionary with.

    Raises:
        exceptions.ConfigEerror: When there is a type missmatche while trying to
            override the base dictionary.

    Returns:
        Dict[str, object] -- The resulting dictionary.
    """
    merged_config = deepcopy(base_config)
    for key, override_value in override_config.items():
        # Parse env variables in the config.yml
        override_value = parse_env(override_value, key)
        if key in merged_config:
            base_value = merged_config[key]
            if type(base_value) != type(override_value):
                raise exceptions.ConfigEerror(
                    f"Tried to assign a {type(override_value)} value when expecting "
                    f"type {type(base_value)} for key {key}"
                )
            if isinstance(base_value, dict):
                merged_config[key] = merge_configs(merged_config[key], override_value)
                continue
        merged_config[key] = deepcopy(override_value)
    return merged_config


def postprocess_config(config: Dict[str, object]):
    """
    Modifies certain configuration keys and runs integrity controls when needed.

    Arguments:
        config {Dict[str, object]} -- The configuration dictionary.
    """
    if not config["API_PREFIX"].startswith("/"):
        config["API_PREFIX"] = "/" + config["API_PREFIX"]


# Load the configuration files
with open(BASE_CONFIG_PATH, "r") as config_file:
    base_config = yaml.safe_load(config_file)
with open(USER_CONFIG_PATH, "r") as config_file:
    user_config = yaml.safe_load(config_file)

config = merge_configs(base_config, user_config)
postprocess_config(config)
config["ENVIRONMENT"] = ENVIRONMENT
logger.info(config)
