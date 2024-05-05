"""Choropleth module."""

from pathlib import Path

import geopandas as gpd
from shapely import geometry, ops, polygonize


def extract_choropleth(all_files: list[Path]):
    """Extract Choropleth polygons from list of LineStrings."""
    all_data = [
        geo
        for file in all_files
        for geo in gpd.read_file(
            file, use_arrow=True, engine="pyogrio"
        ).geometry.to_list()
    ]

    return polygonize(ops.linemerge(geometry.MultiLineString(all_data)).geoms)


def get_municipalities_choropleth(administrative_path: str, scb_path: str):
    """Get municipalities choropleth."""
    admin = Path(administrative_path)
    _ = Path(scb_path)

    all_files = [
        admin / "04_riksgrans.geojson",
        admin / "05_sjoterritoriets_grans_i_havet.geojson",
        admin / "01_kommungrans.geojson",
        admin / "02_lansgrans.geojson",
    ]

    return extract_choropleth(all_files)


def get_regions_choropleth(administrative_path: str, scb_path: str):
    """Get regions choropleth."""
    admin = Path(administrative_path)
    _ = Path(scb_path)

    all_files = [
        admin / "04_riksgrans.geojson",
        admin / "05_sjoterritoriets_grans_i_havet.geojson",
        admin / "02_lansgrans.geojson",
    ]

    return extract_choropleth(all_files)
