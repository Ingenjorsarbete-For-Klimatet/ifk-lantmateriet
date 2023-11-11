"""Ground module."""
from multiprocessing import Pool
from os import path

import geopandas as gpd
from lantmateriet.config import config
from lantmateriet.geometry import Geometry
from lantmateriet.utils import smap

WORKERS = 6


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
        """
        super().__init__(file_path, layer, use_arrow)

        if detail_level == "50":
            self.config = config.ground_50
        elif detail_level == "1m":
            self.config = config.ground_1m
        else:
            NotImplementedError(
                f"The level of detal {detail_level} is not implemented."
            )

    def _get_ground_items(self) -> list[tuple[str, gpd.GeoDataFrame]]:
        """Get ground items.

        Returns:
            list of file names and corresponding geodata
        """
        return [
            (object_name, self.df[self.df["objekttyp"] == object_name])
            for object_name, _ in self.config.items()
            if object_name not in config.exclude_ground
        ]

    def get_ground(
        self, set_area: bool = True, set_length: bool = True
    ) -> dict[str, gpd.GeoDataFrame]:
        """Get all ground items.

        Args:
            set_area: set area column
            set_length: set length column

        Returns:
            map of ground items including

        Raises:
            KeyError
        """
        ground_items = set(self.df["objekttyp"])
        if any([k not in ground_items for k, _ in self.config.items()]):
            raise KeyError(
                "Can't find all items in ground dict. Has the input data changed?"
            )

        ground = [
            (
                Ground._dissolve_exterior
                if object_name in config.exteriorise
                else Ground._dissolve,
                object_name,
                ground_item,
            )
            for object_name, ground_item in self._get_ground_items()
        ]

        with Pool(WORKERS) as pool:
            ground_dissolved = pool.starmap(smap, ground)

        if set_area is True:
            ground_dissolved = [(k, Geometry._set_area(v)) for k, v in ground_dissolved]

        if set_length is True:
            ground_dissolved = [
                (k, Geometry._set_length(v)) for k, v in ground_dissolved
            ]

        return {
            object_name: ground_items for object_name, ground_items in ground_dissolved
        }

    def save_ground(
        self, all_ground_items: dict[str, gpd.GeoDataFrame], save_path: str
    ):
        """Save processed ground items in EPSG:4326 as GeoJSON.

        Args:
            all_ground_items: GeoDataFrame items to save
            save_path: path to save files in
        """
        for object_name, ground_item in all_ground_items.items():
            file_name = self.config[object_name]
            ground_item = ground_item.to_crs(config.epsg_4326)
            ground_item.to_file(path.join(save_path, file_name), driver="GeoJSON")
