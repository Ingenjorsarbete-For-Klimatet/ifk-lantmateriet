"""Polygon module."""

from lantmateriet.geometry import Geometry


class Polygon(Geometry):
    """Polygon class."""

    def __init__(
        self,
        file_path: str,
        detail_level: str = "50",
        layer: str = "mark",
        name: str = "mark",
        field: str = "objekttyp",
    ):
        """Initialise Polygon object.

        Args:
            file_path: path to border data
            detail_level: level of detail of data
            layer: layer to load
            name: name of data
            field: geopandas field
        """
        super().__init__(file_path, detail_level, layer, name, field)
        self.dissolve = True

    def process(self, set_area: bool = True, set_length: bool = True) -> None:
        """Process all data items.

        Args:
            set_area: set area column
            set_length: set length column
        """
        self._process(self.dissolve, set_area, set_length)

    def save(self, save_path: str, file: str, file_ending: str = "fgb"):
        """Save processed ground items in EPSG:4326.

        Args:
            save_path: path to save files in
            file: name of saved file
            file_ending: what file type to save
        """
        self._save(save_path, file, file_ending)
