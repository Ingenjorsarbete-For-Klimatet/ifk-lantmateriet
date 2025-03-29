"""Polygon integration tests."""

import geopandas as gpd
from geopandas import testing

from lantmateriet.polygon import Polygon

test_mark_geojson = gpd.read_file(
    "tests/fixtures/test_integration_ground_mark.geojson", layer="mark", use_arrow=True
)
test_mark_geojson.to_file(
    "tests/fixtures/test_integration_ground_mark.gpkg", layer="mark", driver="GPKG"
)

test_mark_result = gpd.read_file(
    "tests/fixtures/test_integration_ground_mark_result.geojson",
    layer="mark",
    where="objekttyp='Sjö'",
    engine="pyogrio",
    use_arrow=True,
)


class TestIntegrationPolygon:
    """Integration test of Polygon."""

    def test_integration_get_ground_items(self):
        """Integration test of Polygon processd."""
        polygon = Polygon(
            "tests/fixtures/test_integration_ground_mark.gpkg",
            "50",
            "mark",
            "Sjö",
            "objekttyp",
        )
        polygon.process()

        testing.assert_geodataframe_equal(
            polygon.df,
            test_mark_result,
            check_like=True,
            check_dtype=False,
        )
