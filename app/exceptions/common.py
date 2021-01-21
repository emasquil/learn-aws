"""Exception classes for the API."""


class InvalidImage(Exception):
    """
    Raised when PIL cannot load an image
    """


class ModelError(Exception):
    """
    Raised when unable to load trained model
    """


class ConfigError(Exception):
    """
    Raised when unable to load the configuration file
    """
