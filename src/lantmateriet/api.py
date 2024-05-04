"""API module."""

import io
import json
import logging
import os
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

STATUS_OK = 200
BLOCK_SIZE = 1024
ORDER_URL = "https://api.lantmateriet.se"
DOWNLOAD_URL = "https://download-geotorget.lantmateriet.se"
TOKEN = os.environ["LANTMATERIET_API_TOKEN"]

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

    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers, timeout=200, stream=True)

    if response.status_code != STATUS_OK:
        raise requests.exceptions.HTTPError(f"Could not request from {url}.")

    logger.debug(f"Successful request from {url}.")

    return response


class Lantmateriet:
    """Lantmäteriet class."""

    def __init__(self, order_id: str, save_path: str):
        """Initialise Lantmäteriet.

        Args:
            order_id: order id to fetch data from
            save_path: path to save downloaded files to
        """
        order_url = ORDER_URL + f"/geotorget/orderhanterare/v2/{order_id}"
        download_url = DOWNLOAD_URL + f"/download/{order_id}/files"
        self._save_path = save_path

        Path(save_path).mkdir(exist_ok=True)
        self._order_enpoint = json.loads(get_request(order_url).content)
        download = json.loads(get_request(download_url).content)
        self._download_enpoint = {item["title"]: item for item in download}

    @property
    def order(self) -> dict[str, str]:
        """Get order information."""
        return self._order_enpoint

    @property
    def available_files(self) -> list[str]:
        """Get available files."""
        return list(self._download_enpoint.keys())

    def download(self, title: str) -> None:
        """Download file by title.

        Args:
            title: title of file to download
        """
        logger.info(f"Started downloading {title}")

        url = self._download_enpoint[title]["href"]
        response = get_request(url)
        buffer = self._download(response)

        if zipfile.is_zipfile(buffer) is True:
            self._unzip(buffer)

        logger.info(f"Downloaded and unpacked {title} to {self._save_path}")

    def _download(self, response: requests.Response) -> io.BytesIO:
        """Download file from url.

        Args:
            response: requests response object

        Returns:
            bytesio buffer
        """
        file_size = int(response.headers.get("Content-Length", 0))
        buffer = io.BytesIO()
        with tqdm.wrapattr(
            response.raw, "read", total=file_size, desc="Downloading"
        ) as r_raw:
            while True:
                chunk = buffer.write(r_raw.read(BLOCK_SIZE))
                if not chunk:
                    break

        return buffer

    def _unzip(self, buffer: io.BytesIO):
        """Extract zip and save to disk.

        Args:
            buffer: buffer of downloaded content
        """
        with zipfile.ZipFile(buffer) as zip:
            for member in tqdm(zip.infolist(), desc="Extracting"):
                try:
                    zip.extract(member, self._save_path)
                except zipfile.error:
                    logger.error("Can't unzip {member}.")
