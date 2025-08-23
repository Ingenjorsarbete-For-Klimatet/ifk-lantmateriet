"""Lantmäteriet download API integration tests."""

import datetime
import shutil
from pathlib import Path

from lantmateriet.download_api import (
    CHANGE_DATE,
    ITEM_FILE,
    LantmaterietCollection,
    LantmaterietItem,
)
from pystac import Item


class TestAdminBorder:
    """Integration tests for Lantmäteriet download API."""

    def test_integration_download_api_collections(self):
        """Integration test for download api collections."""
        collection = LantmaterietCollection()
        assert len(collection._collections) > 1

    def test_integration_download_api_collections_get_items_from_collection(self):
        """Integration test for download api collections get_items_from_collection."""
        collection = LantmaterietCollection()
        item_key = list(collection._collections.keys())[0]
        collection_item = collection.get_items_from_collection(item_key, 1)[0]
        assert type(collection_item) is Item

    def test_integration_download_api_item(self):
        """Integration test for download api."""
        collection = LantmaterietCollection()
        item_key = list(collection._collections.keys())[0]
        collection_item = collection.get_items_from_collection(item_key, 1)[0]

        item = LantmaterietItem(collection_item)
        assert item.item is collection_item
        assert all(i in item.assets for i in ["data", "metadata", "thumbnail"])

    def test_integration_download_api_item_download_assets(self):
        """Integration test for download api download_assets."""
        tmp_dir = "tmp"
        path = Path(tmp_dir)

        collection = LantmaterietCollection()
        item_key = list(collection._collections.keys())[0]
        collection_item = collection.get_items_from_collection(item_key, 1)[0]
        item = LantmaterietItem(collection_item)
        item.download_assets(tmp_dir)

        path_dir = path.is_dir()
        len_files = len(list(path.glob("**/*")))
        path_file = (path / collection_item.id / ITEM_FILE).is_file()

        shutil.rmtree(path)

        assert path_dir
        assert len_files > 1
        assert path_file

    def test_integration_download_api_item_check_item_newer(self):
        """Integration test for download api check_item_newer."""
        tmp_dir = "tmp"
        path = Path(tmp_dir)

        collection = LantmaterietCollection()
        item_key = list(collection._collections.keys())[0]
        collection_item = collection.get_items_from_collection(item_key, 1)[0]
        item = LantmaterietItem(collection_item)
        item.download_assets(tmp_dir)

        item.item.properties[CHANGE_DATE] = datetime.datetime.now().strftime("%Y-%m-%d")

        check_item_newer = item.check_item_newer(tmp_dir)

        shutil.rmtree(path)

        assert check_item_newer
