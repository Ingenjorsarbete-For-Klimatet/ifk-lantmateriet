"""Config module.

Configuration taken from

- 1M: https://www.lantmateriet.se/globalassets/geodata/geodataprodukter/pb-topografi-1m-nedladdning-vektor.pdf
- 50: https://www.lantmateriet.se/globalassets/geodata/geodataprodukter/pb-topografi-50-nedladdning-vektor.pdf
"""

from typing import TypeVar
import shapely

from lantmateriet.line import Line
from lantmateriet.point import Point
from lantmateriet.polygon import Polygon

Geometry = TypeVar("Geometry", Line, Polygon, Point)


class BaseConfig:
    """Base config class."""

    espg_3006: str = "EPSG:3006"
    epsg_4326: str = "EPSG:4326"
    ground_sweden: str = "00_sverige.geojson"

    border_land: str = "Riksgräns"
    border_sea: str = "Sjöterritoriets gräns i havet"
    border_county: str = "Länsgräns"
    border_municipality: str = "Kommungräns"

    file_geometry_mapping: dict[str, Geometry] = {
        shapely.Point: Point,
        shapely.MultiPoint: Point,
        shapely.MultiLineString: Line,
        shapely.LineString: Line,
        shapely.Polygon: Polygon,
        shapely.MultiPolygon: Polygon,
    }

    def __getitem__(self, key):
        """Get item.

        Args:
            key: key

        Returns:
            value
        """
        return self.__getattribute__(key)


class Config1M(BaseConfig):
    """Topography 1M config class."""

    exclude = {"Hav", "Ej karterat område", "Sverige"}
    exteriorise = {"Skog"}
    ground_water = {
        "Hav",
        "Vattenyta",
    }


class Config50(BaseConfig):
    """Config class."""

    exclude = {"Hav", "Ej karterat område", "Sverige"}
    exteriorise = {"Barr- och blandskog"}
    ground_water = {
        "Anlagt vatten",
        "Sjö",
        "Vattendragsyta",
        "Hav",
    }


config_1m = Config1M()
config_50 = Config50()
