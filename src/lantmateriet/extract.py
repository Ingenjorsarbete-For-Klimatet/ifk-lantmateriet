"""Extract GeoJSON from GPKG files."""

import glob
import logging
from pathlib import Path
from typing import Union

import fiona
import pandas as pd
import shapely
from lantmateriet.config import Config50, config_50
from lantmateriet.line import Line
from lantmateriet.point import Point
from lantmateriet.polygon import Polygon
from lantmateriet.utils import normalise_item_names, read_first_entry, read_unique_names
from ray.util.multiprocessing import Pool

file_geometry_mapping: dict[shapely.Geometry, Union[Line, Polygon, Point]] = {
    shapely.Point: Point,
    shapely.MultiPoint: Point,
    shapely.MultiLineString: Line,
    shapely.LineString: Line,
    shapely.Polygon: Polygon,
    shapely.MultiPolygon: Polygon,
}

WORKER_INNER = 8
WORKER_OUTER = 14

logger = logging.getLogger(__name__)
config = Config50()


def save_sweden_base(target_path, processed_geo_objects):
    """Save sweden base from all dissolved ground."""
    df_sverige = (
        pd.concat([item for item in processed_geo_objects])
        .dissolve()
        .explode(index_parts=False)
    )
    df_sverige["area_m2"] = df_sverige.area
    df_sverige["length_m"] = df_sverige.length
    df_sverige = df_sverige.to_crs(config_50.epsg_4326)
    df_sverige.to_file(
        f"{target_path}/mark_sverige/mark/00_sverige" + ".geojson", driver="GeoJSON"
    )


def parallel_process(geo_object, target_path, output_name):
    """Parallel process."""
    if geo_object.df is not None:
        geo_object.process()
        geo_object.save(target_path, output_name)

        if "mark" in geo_object._file_path:
            return geo_object.df.dissolve().explode(index_parts=False)

    return None


def extract_geojson(target_path: str, file: str, layer: str):
    """Extract and save geojson files."""
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


def extract(source_path: str, target_path):
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
