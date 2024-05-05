"""Choropleth module."""

import geopandas as gpd
from shapely import geometry, ops, polygonize

riksgrans = gpd.read_file("04_riksgrans.geojson", use_arrow=True, engine="pyogrio")
sjograns = gpd.read_file(
    "05_sjoterritoriets_grans_i_havet.geojson", use_arrow=True, engine="pyogrio"
)
lansgrans = gpd.read_file("02_lansgrans.geojson", use_arrow=True, engine="pyogrio")
kommungrans = gpd.read_file("01_kommungrans.geojson", use_arrow=True, engine="pyogrio")

# 21 regions
lans = ops.linemerge(
    geometry.MultiLineString(
        sjograns.geometry.to_list()
        + riksgrans.geometry.to_list()
        + lansgrans.geometry.to_list()
    )
)

# 290 municipalities
kommuns = ops.linemerge(
    geometry.MultiLineString(
        sjograns.geometry.to_list()
        + riksgrans.geometry.to_list()
        + lansgrans.geometry.to_list()
        + kommungrans.geometry.to_list()
    )
)

len(polygonize(lans.geoms).geoms)
