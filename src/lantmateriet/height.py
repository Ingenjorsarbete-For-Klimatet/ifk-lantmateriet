"""Height module."""

import json
import os
from pathlib import Path

from lantmateriet.utils import get_request
from pystac import Item
from pystac_client import Client
from pystac_client.collection_client import CollectionClient
from requests import Response
from requests.auth import HTTPBasicAuth

USER = os.environ["IFK_LANTMATERIET_USER"]
PASS = os.environ["IFK_LANTMATERIET_PASSWORD"]
BASE_URL = "https://api.lantmateriet.se/stac-hojd/v1/"

BASIC_AUTH = HTTPBasicAuth(USER, PASS)
ITEM_FILE = "item.json"
CHANGE_DATE = "andringsdatum"
PROPERTIES = "properties"


class Height:
    """Height class."""

    def __init__(self):
        """Initialize the Height class."""
        self._base_url = BASE_URL
        client = Client.open(self._base_url)
        self._collections = {c.id: c for c in client.get_all_collections()}

    @property
    def collections(self) -> dict[str, CollectionClient]:
        """Get all availabe collections."""
        return self._collections

    def get_items_from_collections(self, collection_id: str) -> list[Item]:
        """Get all items from a specific collection.

        Args:
            collection_id: id of the collection to get items from

        Returns:
            all items in collection
        """
        return list(self._collections[collection_id].get_all_items())


def get_assets_from_item(item: Item) -> dict[str, Response]:
    """Get assets from item.

    Args:
        item: item to get assets from

    Returns:
        all assets in item
    """
    return {k: get_request(v.href, BASIC_AUTH).content for k, v in item.assets.items()}


def download_assets_from_item(item: Item, location: str | Path) -> None:
    """Download assets from item.

    Args:
        item: item to download assets from
        location: location to save assets to
    """
    assets = get_assets_from_item(item)
    item_file_path = Path(location) / item.id / ITEM_FILE

    for k, v in item.assets.items():
        file = assets[k]
        filename = Path(v.href).name

        with open(Path(location) / item.id / filename, "wb") as f:
            f.write(file)

    with open(item_file_path, "w") as f:
        json.dump(item.to_dict(), f)


def check_item_newer(item: Item, location: str | Path) -> bool:
    """Check if item is newer than the saved one.

    Args:
        item: item to check
        location: location of saved item

    Returns:
        True if item is newer, False otherwise
    """
    item_file_path = Path(location) / item.id / ITEM_FILE

    if not item_file_path.exists():
        return False

    with open(Path(location) / item.id / ITEM_FILE, "r") as f:
        saved_item = json.load(f)

    return item.properties[CHANGE_DATE] > saved_item[PROPERTIES][CHANGE_DATE]
