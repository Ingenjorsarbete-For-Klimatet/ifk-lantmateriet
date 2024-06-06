"""Line module."""

from lantmateriet.geometry import Geometry


class Line(Geometry):
    """Line class."""

    def __init__(
        self,
        file_path: str,
        detail_level: str = "50",
        layer: str = "vaglinje",
        name: str = "mark",
        field: str = "objekttyp",
    ):
        """Initialise Line object.

        Args:
            file_path: path to border data
            detail_level: level of detail of data
            layer: layer to load
            name: name of data
            field: geopandas field
        """
        super().__init__(file_path, detail_level, layer, name, field)
        self.dissolve = False

    def process(self, set_length: bool = True) -> None:
        """Process all communication data items.

        Args:
            set_length: set length column
        """
        self._process(self.dissolve, False, set_length)

    def save(self, save_path: str, file: str) -> None:
        """Save processed communication items in EPSG:4326 as GeoJSON.

        Args:
            save_path: path to save files in
            file: name of saved file
        """
        self._save(save_path, file)
