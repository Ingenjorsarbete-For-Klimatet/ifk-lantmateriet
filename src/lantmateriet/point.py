"""Point module."""

from lantmateriet.geometry import Geometry


class Point(Geometry):
    """Point class."""

    def __init__(
        self,
        file_path: str,
        detail_level: str = "50",
        layer: str = "textpunkt",
        name: str = "mark",
        field: str = "texttyp",
    ):
        """Initialise Point object.

        Args:
            file_path: path to border data
            detail_level: level of detail of data
            layer: layer to load
            name: name of data
            field: geopandas field
        """
        super().__init__(file_path, detail_level, layer, name, field)
        self.dissolve = False

    def process(self) -> None:
        """Process all communication data items."""
        self._process(self.dissolve, False, False)

    def save(self, save_path: str, file: str) -> None:
        """Save processed communication items in EPSG:4326 as GeoJSON.

        Args:
            save_path: path to save files in
            file: name of saved file
        """
        self._save(save_path, file)
