"""Extract GeoJSON from GPKG files."""

import glob
import logging
from pathlib import Path
from typing import Optional, Union

import fiona
import geopandas as gpd
import pandas as pd
import shapely
from ray.util.multiprocessing import Pool

from lantmateriet.config import config_50
from lantmateriet.geometry import Geometry
from lantmateriet.line import Line
from lantmateriet.point import Point
from lantmateriet.polygon import Polygon
from lantmateriet.utils import normalise_item_names, read_first_entry, read_unique_names

file_geometry_mapping: dict[shapely.Geometry, Union[Line, Polygon, Point]] = {
    shapely.Point: Point,
    shapely.MultiPoint: Point,
    shapely.MultiLineString: Line,
    shapely.LineString: Line,
    shapely.Polygon: Polygon,
    shapely.MultiPolygon: Polygon,
}

WORKER_INNER = 3
WORKER_OUTER = 6

logger = logging.getLogger(__name__)


def save_sweden_base(target_path: str, processed_geo_objects: Geometry) -> None:
    """Save sweden base from all dissolved ground.

    Args:
        target_path: save path of object
        processed_geo_objects: geometry objects
    """
    df_sverige = (
        pd.concat([item for item in processed_geo_objects]).dissolve().explode(index_parts=False)
    )
    df_sverige["area_m2"] = df_sverige.area
    df_sverige["length_m"] = df_sverige.length
    df_sverige = df_sverige.to_crs(config_50.epsg_4326)
    df_sverige.to_file(f"{target_path}/mark_sverige/mark/00_sverige" + ".geojson", driver="GeoJSON")


def parallel_process(
    geo_object: Geometry, target_path: str, output_name: str
) -> Optional[gpd.GeoDataFrame]:
    """Parallel process.

    Args:
        geo_object: geometry object
        target_path: save path of object
        output_name: name of object to save

    Returns:
        processed geodataframe
    """
    if geo_object.df is not None:
        geo_object.process()
        geo_object.save(target_path, output_name)

        if "mark" in geo_object._file_path:
            return geo_object.df.dissolve().explode(index_parts=False)

    return None


def extract_geojson(target_path: str, file: str, layer: str) -> None:
    """Extract and save geojson files.

    Args:
        target_path: path to load from
        file: file to load
        layer: layer to load from file
    """
    logger.info(f"Working on {file} - {layer}")
    field = "objekttyp"

    if "text" in file or "text" in layer:
        field = "texttyp"

    file_names = read_unique_names(file, layer, field)
    normalised_names = normalise_item_names(file_names)
    geometry_type = type(read_first_entry(file, layer).geometry[0])
    geometry_object = file_geometry_mapping[geometry_type]

    with Pool(WORKER_INNER) as pool:
        all_geo = [
            (geometry_object(file, "50", layer, name, field), target_path, output_name)
            for name, output_name in normalised_names.items()
            if name not in config_50.exclude
        ]
        processed_geo_objects = pool.starmap(parallel_process, all_geo)

    if "mark" in file:
        save_sweden_base(target_path, processed_geo_objects)

    logger.info(f"Saved {file} - {layer}")


def extract(source_path: str, target_path: str) -> None:
    """Run extraction of gkpg to geojson.

    Args:
        source_path: path to search for files
        target_path: path to save extracted files to
    """
    file_pattern = str(Path(source_path) / "*.gpkg")
    files = glob.glob(file_pattern)

    all_files = []
    for file in files:
        available_layers = fiona.listlayers(file)
        for layer in available_layers:
            all_files.append((target_path, file, layer))

    with Pool(WORKER_OUTER) as pool:
        pool.starmap(extract_geojson, all_files)
