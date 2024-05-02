"""API module."""

import io
import json
import logging

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

    def __init__(self, order_id: str):
        """Initialise Lantmäteriet.

        Args:
            order_id: order id to fetch data from
        """
        order_url = ORDER_URL + f"/geotorget/orderhanterare/v2/{order_id}"
        download_url = DOWNLOAD_URL + f"/download/{order_id}/files"

        self.order = json.loads(get_request(order_url).content)
        download = json.loads(get_request(download_url).content)
        self.download = {item["title"]: item for item in download}

    @property
    def order_info(self) -> dict[str, str]:
        """Get order information."""
        return self.order

    @property
    def available_files(self) -> list[str]:
        """Get available files."""
        return list(self.download.keys())

    def download(self, title: str) -> io.BytesIO:
        """Download file by title.

        Args:
            title: title of file to download

        Returns:
            bytes io
        """
        url = self.download[title]["href"]
        return io.BytesIO(get_request(url).content)
