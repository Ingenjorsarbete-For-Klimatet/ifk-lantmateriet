"""Geometry module."""

import os
from os import path
from typing import Union

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from shapely.ops import polygonize

from lantmateriet import config
from lantmateriet.utils import timeit

TOUCHING_MAX_DIST = 1e-5
FILE_ENDING_DRIVERS_MAP = {"geojson": "GeoJson", "fgb": "FlatGeobuf"}


class DissolveTouchingGeometry:
    """Dissolve touching geometry class.

    Args:
        df: GeoPandas dataframe
        merge_key: column that must hold the same value for two touching
            geometries to merge, None to merge all touching geometries
    """

    def __init__(self, df: gpd.GeoDataFrame, merge_key: str | None = None):
        """Initialise object.

        Args:
            df: dataframe
            merge_key: merge key column name
        """
        self.df = df
        self.merge_key = merge_key

    def _get_component_labels(self) -> np.ndarray:
        """Get connected component label of each geometry.

        Geometries within TOUCHING_MAX_DIST of each other are connected,
        directly or via other geometries, and share a component label.
        With a merge key, only pairs whose key values are equal are connected,
        and null counts as equal on both sides.
        Touching pairs with a missing key column never merge.

        Returns:
            array of component labels, one per geometry
        """
        left, right = self.df.sindex.query(
            self.df.geometry, predicate="dwithin", distance=TOUCHING_MAX_DIST
        )
        mask = left != right
        if self.merge_key is not None:
            key = self.df.get(self.merge_key)
            if key is None:
                mask = np.zeros_like(mask)
            else:
                values = key.to_numpy()
                left_values = values[left]
                right_values = values[right]
                both_null = pd.isna(left_values) & pd.isna(right_values)
                mask = mask & ((left_values == right_values) | both_null)
        graph = coo_matrix(
            (np.ones(int(mask.sum())), (left[mask], right[mask])),
            shape=(len(self.df), len(self.df)),
        )
        _, labels = connected_components(graph, directed=False)
        return labels

    def dissolve_and_explode(self) -> gpd.GeoDataFrame:
        """Dissolve and explode touching geometries.

        Geometries in the same connected component of touching geometries are
        dissolved into a single geometry, keeping the attributes of the first
        geometry of the component. Geometries in components of their own pass
        through unchanged.

        Returns:
            GeoPandas dataframe with dissolved, touching geometries, and exploded geometry objects
        """
        labels = self._get_component_labels()

        return (
            self.df.assign(grp=labels)
            .dissolve(by="grp", aggfunc="first")
            .explode(ignore_index=True)
            .reset_index(drop=True)
        )

    def dissolve_and_explode_exterior(self) -> gpd.GeoDataFrame:
        """Dissolve and explode exterior geometry.

        This function doesn't keep any other data apart from geometry.

        Returns:
            GeoPandas dataframe with dissolved and exploded exterior geometry objects
        """
        exploded_geometry = self.df.explode(ignore_index=True)
        exterior_geometry = exploded_geometry
        exterior_geometry.geometry = exterior_geometry.exterior
        dissolved_geometry = exterior_geometry.dissolve()
        exploded_geometry = dissolved_geometry.explode(ignore_index=True)
        return gpd.GeoDataFrame(
            {
                "geometry": [x for x in polygonize(exploded_geometry.geometry)],
                "objekttyp": []
                if len(set(self.df["objekttyp"])) < 1
                else self.df["objekttyp"].iloc[0],
            },
            crs=self.df.crs,
        )


class Geometry:
    """Geometry class."""

    def __init__(self, file_path: str, detail_level: str, layer: str, name: str, field: str):
        """Initialise Geometry object.

        Args:
            file_path: path to border data
            detail_level: level of detail of data
            layer: layer to load
            name: name of data
            field: geopandas field
        """
        if detail_level == "10":
            self.config: Union[config.Config1M, config.Config50, config.Config10] = config.config_10
        elif detail_level == "50":
            self.config = config.config_50
        elif detail_level == "1m":
            self.config = config.config_1m
        else:
            raise NotImplementedError(f"The level of detail: {detail_level} is not implemented.")

        self._file_path = file_path
        self._layer = layer
        self._name = name
        self._field = field

        self.df = gpd.read_file(
            file_path,
            layer=layer,
            where=f"{field}='{name}'",
            engine="pyogrio",
            use_arrow=True,
        )

    @staticmethod
    def _set_area(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Set area for each geometry.

        Args:
            df: geopandas GeoDataFrame

        Returns:
            geopandas GeoDataFrame with area columns
        """
        df["area_m2"] = df.area
        return df

    @staticmethod
    def _set_length(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Set length for each geometry.

        Args:
            df: geopandas GeoDataFrame

        Returns:
            geopandas GeoDataFrame with length columns
        """
        df["length_m"] = df.length
        return df

    @timeit(True)
    @staticmethod
    def _dissolve(df: gpd.GeoDataFrame, merge_key: str | None = None) -> gpd.GeoDataFrame:
        """Dissolve geometry.

        Args:
            object_name: object name
            df: geopandas GeoDataFrame
            merge_key: merge key column name

        Returns:
            dissolved geopandas GeoDataFrame
        """
        return DissolveTouchingGeometry(df, merge_key=merge_key).dissolve_and_explode()

    @timeit(True)
    @staticmethod
    def _dissolve_exterior(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Dissolve exterior geometry.

        Args:
            object_name: object name
            df: geopandas GeoDataFrame

        Returns:
            dissolved geopandas GeoDataFrame
        """
        return DissolveTouchingGeometry(df).dissolve_and_explode_exterior()

    def _process(
        self,
        dissolve: bool = False,
        set_area: bool = True,
        set_length: bool = True,
    ) -> None:
        """Process all data items.

        Args:
            dissolve: dissolve touching geometries
            set_area: set area column
            set_length: set length column
        """
        if dissolve is True:
            merge_key = "vattenytaid" if self._name in self.config.ground_water else None
            if self._name in self.config.exteriorise:
                self.df = Geometry._dissolve_exterior(self.df)
            else:
                self.df = Geometry._dissolve(self.df, merge_key)
        else:
            self.df = self.df.explode(ignore_index=True)

        if set_area is True:
            self.df = Geometry._set_area(self.df)

        if set_length is True:
            self.df = Geometry._set_length(self.df)

    def _save(self, save_path: str, file: str, file_ending: str = "fgb") -> None:
        """Save processed geometry items in EPSG:4326.

        Args:
            save_path: path to save files in
            file: name of saved file
            file_ending: what file type to save
        """
        file_ending_driver = FILE_ENDING_DRIVERS_MAP[file_ending]
        folder_path = path.join(
            save_path, self._file_path.split("/")[-1].split(".")[0], self._layer
        )
        os.makedirs(folder_path, exist_ok=True)

        df = self.df.to_crs(self.config.epsg_4326)
        df.to_file(path.join(folder_path, file) + f".{file_ending}", driver=file_ending_driver)
