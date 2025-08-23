"""Height module."""

import datetime
import json
import os
import time
from pathlib import Path

from pystac import Item
from pystac_client import Client
from requests.auth import HTTPBasicAuth

from lantmateriet.utils import get_request

USER = os.environ["IFK_LANTMATERIET_USER"]
PASS = os.environ["IFK_LANTMATERIET_PASSWORD"]
HEIGHT_URL = "https://api.lantmateriet.se/stac-hojd/v1/"

BASIC_AUTH = HTTPBasicAuth(USER, PASS)
ITEM_FILE = "item.json"
CHANGE_DATE = "andringsdatum"
PROPERTIES = "properties"
HEIGHT = "height"

URL_MAP = {HEIGHT: HEIGHT_URL}


class LantmaterietCollection:
    """Collection class."""

    def __init__(self, dtype: str = HEIGHT):
        """Initialize the Collection class.

        Args:
            dtype: download type, currently only supports height
        """
        self._base_url = URL_MAP[dtype]
        client = Client.open(self._base_url)
        self._collections = {c.id: c for c in client.get_all_collections()}

    def get_items_from_collection(self, collection_id: str, num_items: int = -1) -> list[Item]:
        """Get all items from a specific collection.

        Args:
            collection_id: id of the collection to get items from
            num_items: number of items to get, -1 means all

        Returns:
            all items in collection
        """
        result = []
        for item in self._collections[collection_id].get_items(recursive=True):
            if len(result) == num_items:
                return result

            result.append(item)
            time.sleep(1)

        return result


class LantmaterietItem:
    """Item class."""

    def __init__(self, item: Item):
        """Initialize the Item class.

        Args:
            item: item to get assets from
        """
        self.item = item
        self.assets = {
            k: get_request(v.href, BASIC_AUTH).content for k, v in self.item.assets.items()
        }

    def download_assets(self, location: str | Path) -> None:
        """Download assets from item.

        Args:
            location: location to save assets to
        """
        assets = self.assets
        item_location = Path(location) / self.item.id
        item_location.mkdir(parents=True, exist_ok=True)

        for k, v in self.item.assets.items():
            file = assets[k]
            filename = Path(v.href).name

            with open(item_location / filename, "wb") as f:
                f.write(file)

        with open(item_location / ITEM_FILE, "w") as f:
            json.dump(self.item.to_dict(), f)

    def check_item_newer(self, location: str | Path) -> bool:
        """Check if item is newer than the saved one.

        Args:
            location: location of saved item

        Returns:
            True if item is newer, False otherwise
        """
        item_file_path = Path(location) / self.item.id / ITEM_FILE

        if not item_file_path.exists():
            return True

        with open(item_file_path, "r") as f:
            saved_item = json.load(f)

        new_item_date = datetime.datetime.strptime(self.item.properties[CHANGE_DATE], "%Y-%m-%d")
        saved_item_date = datetime.datetime.strptime(
            saved_item[PROPERTIES][CHANGE_DATE], "%Y-%m-%d"
        )

        return new_item_date > saved_item_date
