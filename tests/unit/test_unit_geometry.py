"""Geometry unit tests."""
import geopandas as gpd
import pytest
from geopandas import testing
from lantmateriet.geometry import DissolveTouchingGeometry
from shapely.geometry import Point


class TestUnitDissolveTouchingGeometry:
    """Unit test of DissolveTouchingGeometry."""

    def test_integration_dissolvetouchinggeometry_init(self):
        """Unit test of DissolveTouchingGeometry init method."""
        df = gpd.GeoDataFrame()
        dtg = DissolveTouchingGeometry(df)
        testing.assert_geodataframe_equal(dtg.df, df)

    def test_integration_dissolvetouchinggeometry_get_spatial_index(self):
        """Unit test of DissolveTouchingGeometry _get_spatial_index method."""
        df = gpd.GeoDataFrame({"geometry": [Point(1, 2), Point(2, 1)]})
        sindex = DissolveTouchingGeometry(df)._get_spatial_index()
        assert sindex == df.sindex

    @pytest.mark.parametrize(
        "input_geometry, touching_geometry, expected_result",
        [
            ([], [], {}),
            (
                [0, 1],
                [1, 2],
                {
                    0: {
                        0,
                        1,
                    },
                    1: {
                        1,
                        2,
                    },
                },
            ),
            (
                [0, 1, 0],
                [1, 2, 3],
                {
                    0: {0, 1, 3},
                    1: {
                        1,
                        2,
                    },
                },
            ),
        ],
    )
    def test_integration_dissolvetouchinggeometry_format_touching_geometries(
        self, input_geometry, touching_geometry, expected_result
    ):
        """Unit test of DissolveTouchingGeometry _format_touching_geometries method.

        Args:
            input_geometry: input geometry index
            touching_geometry: touching geometry index
            expected_result: expected results
        """
        result = DissolveTouchingGeometry._format_touching_geometries(
            input_geometry, touching_geometry
        )
        assert expected_result == result

    @pytest.mark.parametrize(
        "touching_geometry, expected_result",
        [
            ({}, {}),
            (
                {
                    0: {
                        0,
                    },
                    1: {
                        1,
                    },
                },
                {
                    0: {
                        0,
                    },
                    1: {
                        1,
                    },
                },
            ),
            (
                {
                    0: {0, 1},
                    1: {1, 2},
                    2: {
                        2,
                    },
                    3: {
                        3,
                    },
                    4: {4, 0},
                },
                {
                    0: {0, 1, 2, 4},
                    1: {0, 1, 2, 4},
                    2: {0, 1, 2, 4},
                    3: {3},
                    4: {0, 1, 2, 4},
                },
            ),
        ],
    )
    def test_integration_dissolvetouchinggeometry_connect_touching_geometries(
        self, touching_geometry, expected_result
    ):
        """Unit test of DissolveTouchingGeometry _connect_touching_geometries method.

        Args:
            touching_geometry: touching geometry index
            expected_result: expected results
        """
        result = DissolveTouchingGeometry._connect_touching_geometries(
            touching_geometry
        )
        assert expected_result == result
