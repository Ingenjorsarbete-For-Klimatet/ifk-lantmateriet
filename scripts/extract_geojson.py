"""Extract GeoJSON from GPKG files."""

import glob
import logging
from typing import TypeVar

import fiona
import geopandas as gpd
import pandas as pd
import shapely
from lantmateriet.config import Config50, config_50
from lantmateriet.line import Line
from lantmateriet.point import Point
from lantmateriet.polygon import Polygon
from ray.util.multiprocessing import Pool
from unidecode import unidecode

Geometry = TypeVar("Geometry", Line, Polygon, Point)

file_geometry_mapping: dict[str, Geometry] = {
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


def read_unique_names(file: str, layer: str, field: str) -> list[str]:
    """Read unique names from specified field in file."""
    return sorted(
        list(
            set(
                gpd.read_file(
                    file,
                    use_arrow=True,
                    include_fields=[field],
                    ignore_geometry=True,
                    layer=layer,
                )[field]
            )
        )
    )


def read_first_entry(file: str, layer: str) -> gpd.GeoDataFrame:
    """Read info from file."""
    return gpd.read_file(file, use_arrow=True, layer=layer, rows=1)


def normalise_item_names(item_names: list[str]) -> dict[str, str]:
    """Normalise item names to save format."""
    return {
        x: "{:02d}_".format(i + 1)
        + unidecode(x.lower())
        .replace(" ", "_")
        .replace("-", "")
        .replace(",", "")
        .replace("/", "_")
        for i, x in enumerate(item_names)
    }


def save_sweden_base(processed_geo_objects):
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
        "tmp/mark_sverige/mark/00_sverige" + ".geojson", driver="GeoJSON"
    )


def parallel_process(geo_object, output_name):
    """Parallel process."""
    if geo_object.df is not None:
        geo_object.process()
        geo_object.save("tmp", output_name)

        if "mark" in geo_object._file_path:
            return geo_object.df.dissolve().explode(index_parts=False)

    return None


def extract_geojson(file: str, layer: str):
    """Extract and save geojson files."""
    print(f"Working on {file} - {layer}")
    field = "objekttyp"

    if "text" in file or "text" in layer:
        field = "texttyp"

    file_names = read_unique_names(file, layer, field)
    normalised_names = normalise_item_names(file_names)
    geometry_type = type(read_first_entry(file, layer).geometry[0])
    geometry_object = file_geometry_mapping[geometry_type]

    with Pool(WORKER_INNER) as pool:
        all_geo = [
            (geometry_object(file, "50", layer, name, field), output_name)
            for name, output_name in normalised_names.items()
        ]
        processed_geo_objects = pool.starmap(parallel_process, all_geo)

    if "mark" in file:
        save_sweden_base(processed_geo_objects)

    print(f"Saved {file} - {layer}")


def run():
    """Run extraction."""
    files = glob.glob("topografi_50/*.gpkg")

    all_files = []
    for file in files:
        available_layers = fiona.listlayers(file)
        for layer in available_layers:
            all_files.append((file, layer))

    with Pool(WORKER_OUTER) as pool:
        pool.starmap(extract_geojson, all_files)


if __name__ == "__main__":
    run()
