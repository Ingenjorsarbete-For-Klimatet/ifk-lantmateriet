"""Utils module."""

import logging
import time
from functools import wraps
from typing import Callable, Optional

import geopandas as gpd
from unidecode import unidecode

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

STATUS_OK = 200
OUT_OF_BOUNDS = "out of bounds"


def timeit(has_key: bool = False):
    """Time decorator.

    Args:
        has_key: if firt argument is a key (from a dict), use in logging

    Returns:
        decorated function
    """

    def timeit_decorator(fun: Callable):
        @wraps(fun)
        def wrap(*args, **kw):
            t0 = time.perf_counter()
            result = fun(*args, **kw)
            t1 = time.perf_counter()

            if has_key is True:
                logging.info(f"{args[0]} took: {t1 - t0} s.")
            else:
                logging.info(f"Took: {t1 - t0} s.")
            return result

        return wrap

    return timeit_decorator


def read_unique_names(file: str, layer: str, field: str) -> list[str]:
    """Read unique names from specified field in file."""
    return sorted(
        list(
            set(
                gpd.read_file(
                    file,
                    use_arrow=True,
                    include_fields=[field],
                    ignore_geometry=True,
                    layer=layer,
                )[field]
            )
        )
    )


def read_first_entry(file: str, layer: str) -> gpd.GeoDataFrame:
    """Read info from file."""
    return gpd.read_file(file, use_arrow=True, layer=layer, rows=1)


def normalise_item_names(item_names: list[str]) -> dict[str, str]:
    """Normalise item names to save format."""
    return {
        x: "{:02d}_".format(i + 1)
        + unidecode(x.lower())
        .replace(" ", "_")
        .replace("-", "")
        .replace(",", "")
        .replace("/", "_")
        for i, x in enumerate(item_names)
    }


logger = logging.getLogger(__name__)


def get_request(url: str, auth: Optional[HTTPBasicAuth] = None) -> requests.Response:
    """Get request from url.

    Args:
        url: url to request from
        auth: authentication

    Returns:
        response

    Raises:
        ValueError
        requests.exceptions.HTTPError
    """
    logger.debug(f"Fetching from {url}.")

    response = requests.get(url, timeout=200, auth=auth)

    if response.status_code != STATUS_OK:
        if OUT_OF_BOUNDS in response.text.lower():
            raise ValueError("Request is out of bounds.")

        raise requests.exceptions.HTTPError(f"Could not request from {url}.")

    logger.debug(f"Successful request from {url}.")

    return response
