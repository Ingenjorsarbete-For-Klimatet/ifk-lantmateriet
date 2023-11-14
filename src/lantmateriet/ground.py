"""Ground module."""
import geopandas as gpd
import pandas as pd
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
            layer: layer to load, must be present in config.ground dict
            use_arrow: use arrow for file-loading

        Raises:
            NotImplementedError: if detail level not implemented
            KeyError: if data objekttyp not equal to ground dict
        """
        super().__init__(file_path, detail_level, layer, use_arrow)
        self.layer = layer
        self.item_type = "ground"
        self.dissolve = True

        if set(self.df["objekttyp"]) | self.config.exclude != (
            set(self.config.ground[layer].keys()) | self.config.exclude
        ):
            raise KeyError(
                "Data objekttyp not equal to ground dict. Has the input data changed?"
            )

    def process(
        self, set_area: bool = True, set_length: bool = True
    ) -> dict[str, gpd.GeoDataFrame]:
        """Process all data items.

        Args:
            set_area: set area column
            set_length: set length column

        Returns:
            map of ground items including
        """
        df_processed = self._process(
            self.item_type, self.layer, self.dissolve, set_area, set_length
        )
        df_processed["Sverige"] = (
            pd.concat(
                [
                    v  # v[~v["objekttyp"].isin(self.config.ground_water)]
                    for _, v in df_processed.items()
                ]
            )
            .dissolve()
            .explode(index_parts=False)
        )
        df_processed["Sverige"] = self._set_area(df_processed["Sverige"])
        df_processed["Sverige"] = self._set_length(df_processed["Sverige"])
        df_processed["Sverige"]["objekttyp"] = "Sverige"

        return df_processed

    def save(self, all_items: dict[str, gpd.GeoDataFrame], save_path: str):
        """Save processed ground items in EPSG:4326 as GeoJSON.

        Args:
            all_items: GeoDataFrame items to save
            save_path: path to save files in
        """
        all_items_exclude = {
            k: v for k, v in all_items.items() if k not in self.config.exteriorise
        }
        self._save(self.item_type, self.layer, all_items_exclude, save_path)
