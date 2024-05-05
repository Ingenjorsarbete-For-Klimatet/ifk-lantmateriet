"""Choropleth module."""

from pathlib import Path

import geopandas as gpd
from shapely import geometry, ops, polygonize


def extract_choropleth(path: str):
    """Extract Choropleth polygons for regions and municipalities."""
    path = Path(path)

    riksgrans = gpd.read_file(
        path / "04_riksgrans.geojson", use_arrow=True, engine="pyogrio"
    )
    sjograns = gpd.read_file(
        path / "05_sjoterritoriets_grans_i_havet.geojson",
        use_arrow=True,
        engine="pyogrio",
    )
    lansgrans = gpd.read_file(
        path / "02_lansgrans.geojson", use_arrow=True, engine="pyogrio"
    )
    kommungrans = gpd.read_file(
        path / "01_kommungrans.geojson", use_arrow=True, engine="pyogrio"
    )

    lans = ops.linemerge(
        geometry.MultiLineString(
            sjograns.geometry.to_list()
            + riksgrans.geometry.to_list()
            + lansgrans.geometry.to_list()
        )
    )

    kommuns = ops.linemerge(
        geometry.MultiLineString(
            sjograns.geometry.to_list()
            + riksgrans.geometry.to_list()
            + lansgrans.geometry.to_list()
            + kommungrans.geometry.to_list()
        )
    )

    return lans, kommuns
