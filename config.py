""" config.py
    
    Main file for any kind of configuration regarding env variables. Prefer
    using the pre-defined variables found in here rather than getting them
    manually with `os.getenv`.

    You can read more about the environment variables in the `.env.example`
    file.

    Author: João Iacillo <john@iacillo.dev.br>
"""

from os import getenv as os_getenv
from typing import Callable, Union

from dotenv import load_dotenv

load_dotenv()


def getenv(
        key: str,
        default: any = None,
        nullable: Union[bool, str] = False,
        checks: list[Callable[[str], Union[bool, str]]] = [],
        transforms: list[Callable[[any], any]] = []
):
    """
    Wrapper for getting an environment variable and applying the required
    checks and transformations before returning the value.

    Each string returned by the check callable is formatted with some keys
    that can be used:
     - key: str -> Env. var key
     - val: str -> Env. var value

    :param key: Env. var key
    :param default: Default fallback value
    :param nullable: If the value can be None. Defaults to False. If is
    string, uses it as error message
    :param checks: List of functions that receive the key value and must
    return True or a string with the error message
    :param transforms: List of functions to transform the key value
    consecutively
    :return: The transformed key value
    """

    value = os_getenv(key)

    if value is None:
        if not nullable:
            raise ValueError(f'{key} requires a value, but none was provided')
        elif isinstance(nullable, str):
            raise ValueError(nullable)

        value = default

    for check in checks:
        res = check(value)
        if isinstance(res, str):
            raise ValueError(res.format(key=key, val=value))

    for transform in transforms:
        value = transform(value)

    return value


# Bot Environment Variables

BOT_DEBUG_MODE: bool = getenv(
        'BOT_DEBUG_MODE',
        'false',
        True
) == 'true'

BOT_THRESHOLD: int = getenv(
        'BOT_THRESHOLD',
        '80',
        nullable=True,
        checks=[lambda val: val.isnumeric() or '{key} expected to receive a '
                                               'numeric value, but received:'
                                               ' "{val}"'],
        transforms=[int]
)

BOT_SKIP_ON_INPUT: bool = getenv(
        'BOT_SKIP_ON_INPUT',
        'false',
        nullable=True,
) == 'true'

# Database Environment Variables

DB_FILE: str = getenv(
        'DB_FILE',
        'bmg.db',
        nullable=True,
        transforms=[str.strip]
)

# TMDB Environment Variables

TMDB_API_ACCESS_TOKEN = getenv('TMDB_API_ACCESS_TOKEN')

TMDB_IMAGE_QUALITY: int = getenv(
        'TMDB_IMAGE_QUALITY',
        '75',
        nullable=True,
        checks=[lambda val: val.isnumeric() or '{key} expected to receive a '
                                               'numeric value, but received:'
                                               ' "{val}"'],
        transforms=[int]
)

# Bsky Environment Variables

BSKY_HANDLE = getenv('BSKY_HANDLE')
BSKY_PASSWORD = getenv('BSKY_PASSWORD')
