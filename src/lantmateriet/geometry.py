"""Geometry module."""
import geopandas as gpd
from lantmateriet.utils import timeit

TOUCHING_MAX_DIST = 1e-5
BUFFER_DIST = 1e-8


class DissolveTouchingGeometry:
    """Dissolve touching geometry class.

    Args:
        df: GeoPandas dataframe
    """

    def __init__(self, df: gpd.GeoDataFrame):
        """Initialise object.

        Args:
            df: dataframe
        """
        self.df = df

    def _get_spatial_index(self):
        """Get spatial index of GeoPandas dataframe.

        Returns:
            spatial index
        """
        return self.df.sindex

    def _format_touching_geometries(
        self, input_geometry_index: list, touching_geometry_index: list
    ) -> dict:
        """Put touching geometries into a dictionary.

        Args:
            input_geometry_index: index of input geometry
            touching_geometry_index: index of touching geometry

        Returns:
            touching geometries
        """
        touching_geometries = {}
        for i, input_index in enumerate(input_geometry_index):
            if input_index not in touching_geometries:
                touching_geometries[input_index] = {input_index}

            touching_geometries[input_index].add(touching_geometry_index[i])

        return touching_geometries

    def _connect_touching_geometries(self, touching_geometries: dict) -> dict:
        """Connect all touching geometries, including duplicates.

        Args:
            touching_geometries: map of touching geometries

        Returns:
            connected touching geometries
        """
        return {
            primary_index: self._find_connected_geometries(
                touching_geometries, secondary_indices
            )
            for primary_index, secondary_indices in list(touching_geometries.items())
        }

    def _find_connected_geometries(
        self, touching_geometries: dict, subset_touching_geometries: set
    ) -> set:
        """Recursive function finding connected geometries.

        Args:
            touching_geometries: map of all touching geometries
            subset_touching_geometries: list of geometries touching

        Returns:
            list of all connected geometries
        """
        connected_touching_geometries = subset_touching_geometries.copy()

        for index in subset_touching_geometries:
            if index in touching_geometries:
                connected_touching_geometries.update(touching_geometries[index])

        if connected_touching_geometries - subset_touching_geometries:
            connected_touching_geometries.update(
                self._find_connected_geometries(
                    touching_geometries, connected_touching_geometries
                )
            )

        return connected_touching_geometries

    def _remove_duplicate_geometries(self, touching_geometries: dict) -> dict:
        """Remove duplicate geometries.

        Args:
            touching_geometries: map of conneced touching geometries

        Returns:
            unique connected touching geometries
        """
        all_primary_index = set()
        all_secondary_indices: set = set()

        for primary_index, secondary_indices in touching_geometries.items():
            if len(all_secondary_indices) == 0:
                all_primary_index.add(primary_index)
                all_secondary_indices.update(secondary_indices)
                continue

            if all_secondary_indices - secondary_indices:
                all_primary_index.difference_update(secondary_indices)
                all_primary_index.add(primary_index)
                all_secondary_indices.update(secondary_indices)

        return {
            primary_index: list(secondary_indices)
            for primary_index, secondary_indices in touching_geometries.items()
            if primary_index in all_primary_index
        }

    def _get_touching_geometries(self) -> dict:
        """Get touching geometries indices.

        Returns:
            indices of unique connected touching geometries
        """
        spatial_index = self._get_spatial_index()
        input_geometry_index, touching_geometry_index = spatial_index.nearest(
            self.df["geometry"], exclusive=True, max_distance=TOUCHING_MAX_DIST
        )

        disconnected_touching_geometries = self._format_touching_geometries(
            input_geometry_index, touching_geometry_index
        )
        connected_touching_geometries = self._connect_touching_geometries(
            disconnected_touching_geometries
        )

        return self._remove_duplicate_geometries(connected_touching_geometries)

    def _get_df_indices(self, touching_geometries: dict) -> tuple[list, list]:
        """Get df index to keep and drop.

        Args:
            touching_geometries: indices of unique connected touching geometries

        Returns:
            keep and drop index lists
        """
        keep_geometry_indices = set(touching_geometries.keys())
        drop_geometry_indices = {
            index for subset in touching_geometries.values() for index in subset
        }
        drop_geometry_indices = drop_geometry_indices - keep_geometry_indices

        keep_indices = self.df.iloc[list(keep_geometry_indices)].index.tolist()
        drop_indices = self.df.iloc[list(drop_geometry_indices), :].index.tolist()

        return keep_indices, drop_indices

    def dissolve_and_explode(self) -> gpd.GeoDataFrame:
        """Dissolve and explode touching geometries.

        Returns:
            GeoPandas dataframe with dissolved, touching geometries, and exploded geometry objects
        """
        touching_geometries = self._get_touching_geometries()
        keep_indices, drop_indices = self._get_df_indices(touching_geometries)

        dissolved_geometry = [
            self.df.iloc[list(tgi)].dissolve() for _, tgi in touching_geometries.items()
        ]

        self.df.loc[keep_indices, "geometry"] = [x.geometry for x in dissolved_geometry]
        self.df.drop(index=drop_indices, inplace=True)

        return self.df.explode(index_parts=False)

    def dissolve_and_explode_exterior(self) -> gpd.GeoDataFrame:
        """Dissolve and explode exterior geometry.

        Returns:
            GeoPandas dataframe with dissolved and exploded exterior geometry objects
        """
        exploded_geometry = self.df.explode(index_parts=False)
        exploded_geometry.geometry = exploded_geometry.exterior
        return exploded_geometry.dissolve()


class Geometry:
    """Geometry class."""

    def __init__(self, file_path: str, layer: str, use_arrow: bool):
        """Initialise Geometry object.

        Args:
            file_path: path to border data
            layer: layer to load
            use_arrow: use arrow to load file
        """
        self.df = gpd.read_file(file_path, layer, use_arrow)

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
    def _dissolve(
        object_name: str, df: gpd.GeoDataFrame
    ) -> tuple[str, gpd.GeoDataFrame]:
        """Dissolve geometry.

        Args:
            object_name: object name
            df: geopandas GeoDataFrame

        Returns:
            object name and dissolved geopandas GeoDataFrame
        """
        df_dissolved = DissolveTouchingGeometry(df).dissolve_and_explode()

        return (object_name, df_dissolved)

    @timeit(True)
    @staticmethod
    def _dissolve_exterior(
        object_name: str, df: gpd.GeoDataFrame
    ) -> tuple[str, gpd.GeoDataFrame]:
        """Dissolve exterior geometry.

        Args:
            object_name: object name
            df: geopandas GeoDataFrame

        Returns:
            object name and dissolved geopandas GeoDataFrame
        """
        df_dissolved = DissolveTouchingGeometry(df).dissolve_and_explode_exterior()
        return (object_name, df_dissolved)
