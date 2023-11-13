"""Communication module."""

import geopandas as gpd
from lantmateriet.geometry import Geometry


class Communication(Geometry):
    """Communication class."""

    def __init__(
        self,
        file_path: str,
        detail_level: str = "50",
        layer: str = "mark",
        use_arrow: bool = True,
    ):
        """Initialise Communication object.

        Args:
            file_path: path to border data
            detail_level: level of detail of data
            layer: layer to load
            use_arrow: use arrow for file-loading

        Raises:
            NotImplementedError: if detail level not implemented
            KeyError: if data objekttyp not equal to ground dict
        """
        super().__init__(file_path, detail_level, layer, use_arrow)
        self.layer = layer
        self.item_type = "communication"

        if set(self.df["objekttyp"]) != set(self.config.communication.keys()):
            raise KeyError(
                "Data objekttyp not equal to communication dict. Has the input data changed?"
            )

    def process(self, set_length: bool = True) -> dict[str, gpd.GeoDataFrame]:
        """Process all communication data items.

        Args:
            set_length: set length column

        Returns:
            map of ground items including
        """
        return self._process(self.item_type, self.layer, False, set_length)

    def save(self, all_items: dict[str, gpd.GeoDataFrame], save_path: str):
        """Save processed communication items in EPSG:4326 as GeoJSON.

        Args:
            all_items: GeoDataFrame items to save
            save_path: path to save files in
        """
        self._save(self.item_type, self.layer, all_items, save_path)
