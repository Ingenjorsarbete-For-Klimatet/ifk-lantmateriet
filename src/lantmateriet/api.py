"""API module."""

import io
import json
import logging
import zipfile
from typing import Optional

import requests

STATUS_OK = 200

ORDER_URL = "https://api.lantmateriet.se"
DOWNLOAD_URL = "https://download-geotorget.lantmateriet.se"

logger = logging.getLogger(__name__)


def get_request(url: str) -> requests.Response:
    """Get request from url.

    Args:
        url: url to request from

    Returns:
        response

    Raises:
        ValueError
        requests.exceptions.HTTPError
    """
    logger.debug(f"Fetching from {url}.")

    response = requests.get(url, timeout=200)

    if response.status_code != STATUS_OK:
        raise requests.exceptions.HTTPError(f"Could not request from {url}.")

    logger.debug(f"Successful request from {url}.")

    return response


class Lantmateriet:
    """Lantmäteriet class."""

    def __init__(self, order_id: str, save_path: Optional[str] = None):
        """Initialise Lantmäteriet.

        Args:
            order_id: order id to fetch data from
            save_path: path to save downloaded files to
        """
        order_url = ORDER_URL + f"/geotorget/orderhanterare/v2/{order_id}"
        download_url = DOWNLOAD_URL + f"/download/{order_id}/files"
        self._save_path = save_path

        self._order = json.loads(get_request(order_url).content)
        download = json.loads(get_request(download_url).content)
        self._download = {item["title"]: item for item in download}

    @property
    def order(self) -> dict[str, str]:
        """Get order information."""
        return self._order

    @property
    def available_files(self) -> list[str]:
        """Get available files."""
        return list(self._download.keys())

    def download(self, title: str) -> io.BytesIO:
        """Download file by title.

        Args:
            title: title of file to download

        Returns:
            bytes io
        """
        logger.info(f"Started downloading {title}")
        url = self._download[title]["href"]
        content = get_request(url).content
        zip = zipfile.ZipFile(io.BytesIO(content))
        zip.extractall(self._save_path)
        logger.info(f"Downloaded and unpacked {title} to {self._save_path}")
