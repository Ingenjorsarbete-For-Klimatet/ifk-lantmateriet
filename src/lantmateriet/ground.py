"""Ground module."""
import geopandas as gpd
from lantmateriet.geometry import Geometry


class Ground(Geometry):
    """Ground class."""

    def __init__(
        self,
        file_path: str,
        detail_level: str = "50",
        layer: str = "mark",
        use_arrow: bool = True,
    ):
        """Initialise Ground object.

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
        self.items = set(self.df["objekttyp"])

        if self.items != set(self.config.ground.keys()):
            raise KeyError(
                "Data objekttyp not equal to ground dict. Has the input data changed?"
            )

    def process(
        self, item_type, set_area: bool = True, set_length: bool = True
    ) -> dict[str, gpd.GeoDataFrame]:
        """Process all data items.

        Args:
            item_type: item type
            set_area: set area column
            set_length: set length column

        Returns:
            map of ground items including
        """
        return self._process(item_type, set_area, set_length)

    def save(self, item_type, all_items: dict[str, gpd.GeoDataFrame], save_path: str):
        """Save processed ground items in EPSG:4326 as GeoJSON.

        Args:
            item_type: item type
            all_items: GeoDataFrame items to save
            save_path: path to save files in
        """
        self._save(item_type, all_items, save_path)
