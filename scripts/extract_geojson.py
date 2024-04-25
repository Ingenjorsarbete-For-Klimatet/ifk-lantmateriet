"""Extract GEOJson from GPKG files."""

import glob
import logging
from multiprocessing import Pool, set_start_method

import fiona
import geopandas as gpd
import pandas as pd
from lantmateriet.config import Config50
from unidecode import unidecode

WORKERS = 8

set_start_method("fork")
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


def extract_geojson(file: str, layer: str):
    """Extract and save geojson files."""
    print(f"Working on {file} - {layer}")
    field = "objekttyp"

    if "text" in file or "text" in layer:
        field = "texttyp"

    file_names = read_unique_names(file, layer, field)
    normalised_names = normalise_item_names(file_names)
    geometry_type = type(read_first_entry(file, layer).geometry[0])
    geometry_object = config.file_geometry_mapping[geometry_type]

    if "mark" in file:
        df_sverige = None

    for name, output_name in normalised_names.items():
        geo_object = geometry_object(file, "50", layer, name, field)
        if geo_object.df is not None:
            geo_object.process()
            geo_object.save("tmp", output_name)

        if "mark" in file:
            if df_sverige is None:
                df_sverige = geo_object.df.dissolve().explode(index_parts=False)
            else:
                df_sverige = (
                    pd.concat([df_sverige, geo_object.df])
                    .dissolve()
                    .explode(index_parts=False)
                )

    if "mark" in file:
        df_sverige["area_m2"] = df_sverige.area
        df_sverige["length_m"] = df_sverige.length
        df_sverige = df_sverige.df.to_crs(geo_object.config.epsg_4326)
        df_sverige.to_file(
            "tmp/mark_sverige/mark/00_sverige" + ".geojson", driver="GeoJSON"
        )

    print(f"Saved {file} - {layer}")


files = glob.glob("topografi_50/*.gpkg")

all_files = []
for file in files:
    available_layers = fiona.listlayers(file)
    for layer in available_layers:
        all_files.append((file, layer))

with Pool(WORKERS) as pool:
    pool.starmap(extract_geojson, all_files)
