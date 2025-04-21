"""Choropleth module."""

from pathlib import Path

import geopandas as gpd
from shapely import geometry, ops, polygonize


def read_data(path: str) -> gpd.GeoDataFrame:
    """Read SCB defined regions."""
    return gpd.read_file(path, use_arrow=True, engine="pyogrio")


def extract_choropleth_polygons(all_files: list[Path]):
    """Extract Choropleth polygons from list of LineStrings."""
    all_data = [geo for file in all_files for geo in read_data(file).geometry.to_list()]

    return polygonize(ops.linemerge(geometry.MultiLineString(all_data)).geoms)


def get_choropleth(scb_path: str, all_files: list[str]):
    """Get municipalities choropleth."""
    all_polygons = extract_choropleth_polygons(all_files)
    scb_df = read_data(scb_path)

    for row in scb_df.iterrows():
        for polygon in all_polygons:
            if polygon.contains(row.centroid):
                row.geometry = polygon

    return scb_df


def get_municipality(admin_folder: str, scb_folder: str):
    """Get municipalities."""
    admin = Path(admin_folder)
    scb = Path(scb_folder) / "Kommun_Sweref99TM.geojson"
    all_files = [
        admin / "04_riksgrans.geojson",
        admin / "05_sjoterritoriets_grans_i_havet.geojson",
        admin / "01_kommungrans.geojson",
        admin / "02_lansgrans.geojson",
    ]

    return get_choropleth(scb, all_files)


def get_regions(admin_folder: str, scb_folder: str):
    """Get regions."""
    admin = Path(admin_folder)
    scb = Path(scb_folder) / "Lan_Sweref99TM_region.geojson"
    all_files = [
        admin / "04_riksgrans.geojson",
        admin / "05_sjoterritoriets_grans_i_havet.geojson",
        admin / "02_lansgrans.geojson",
    ]

    return get_choropleth(scb, all_files)
