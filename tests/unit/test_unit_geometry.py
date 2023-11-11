"""Geometry unit tests."""
from unittest.mock import patch

import geopandas as gpd
import pytest
from geopandas import testing
from lantmateriet.geometry import DissolveTouchingGeometry, Geometry
from shapely.geometry import Point, Polygon


class TestUnitDissolveTouchingGeometry:
    """Unit tests of DissolveTouchingGeometry."""

    def test_unit_dissolvetouchinggeometry_init(self):
        """Unit test of DissolveTouchingGeometry init method."""
        df = gpd.GeoDataFrame()
        dtg = DissolveTouchingGeometry(df)
        testing.assert_geodataframe_equal(dtg.df, df)

    def test_unit_dissolvetouchinggeometry_get_spatial_index(self):
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
    def test_unit_dissolvetouchinggeometry_format_touching_geometries(
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
    def test_unit_dissolvetouchinggeometry_connect_touching_geometries(
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

    @pytest.mark.parametrize(
        "touching_geometry, expected_result",
        [
            ({}, {}),
            ({0: {0, 1}, 1: {1, 2}}, {0: [0, 1], 1: [1, 2]}),
            (
                {
                    0: {0, 1, 2, 4},
                    1: {0, 1, 2, 4},
                    2: {0, 1, 2, 4},
                    3: {3},
                    4: {0, 1, 2, 4},
                },
                {
                    3: [3],
                    4: [0, 1, 2, 4],
                },
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_remove_duplicate_geometries(
        self, touching_geometry, expected_result
    ):
        """Unit test of DissolveTouchingGeometry _remove_duplicate_geometries method.

        Args:
            touching_geometry: touching geometry index
            expected_result: expected results
        """
        result = DissolveTouchingGeometry._remove_duplicate_geometries(
            touching_geometry
        )
        assert expected_result == result

    @pytest.mark.parametrize(
        "df, expected_result",
        [
            (gpd.GeoDataFrame({"geometry": []}), {}),
            (gpd.GeoDataFrame({"geometry": [Point(1, 2), Point(1, 2)]}), {}),
            (
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, 1.0),
                                    (0.0, 1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, -1.0),
                                    (0.0, -1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 1.0),
                                    (1.0, 1.0),
                                    (1.0, 2.0),
                                    (0.0, 2.0),
                                    (0.0, 1.0),
                                )
                            ),
                        ]
                    }
                ),
                {0: [0, 1, 2]},
            ),
            (
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, 1.0),
                                    (0.0, 1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, -1.0),
                                    (0.0, -1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 2.0),
                                    (1.0, 2.0),
                                    (1.0, 3.0),
                                    (0.0, 3.0),
                                    (0.0, 2.0),
                                )
                            ),
                        ]
                    }
                ),
                {0: [0, 1]},
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_get_touching_geometries(
        self, df, expected_result
    ):
        """Unit test of DissolveTouchingGeometry _get_touching_geometries method.

        Args:
            df: df
            expected_result: expected results
        """
        dtg = DissolveTouchingGeometry(df)
        result = dtg._get_touching_geometries()
        assert expected_result == result

    @pytest.mark.parametrize(
        "df, touching_geometry, expected_result",
        [
            (gpd.GeoDataFrame({"geometry": []}), {}, ([], [])),
            (
                gpd.GeoDataFrame(
                    {"geometry": [Point(1, 2), Point(1, 2)]}, index=[1, 2]
                ),
                {},
                ([], []),
            ),
            (
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, 1.0),
                                    (0.0, 1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, -1.0),
                                    (0.0, -1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 1.0),
                                    (1.0, 1.0),
                                    (1.0, 2.0),
                                    (0.0, 2.0),
                                    (0.0, 1.0),
                                )
                            ),
                        ]
                    },
                    index=[1, 2, 3],
                ),
                {0: [0, 1, 2]},
                ([1], [2, 3]),
            ),
            (
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, 1.0),
                                    (0.0, 1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, -1.0),
                                    (0.0, -1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 2.0),
                                    (1.0, 2.0),
                                    (1.0, 3.0),
                                    (0.0, 3.0),
                                    (0.0, 2.0),
                                )
                            ),
                        ]
                    },
                    index=[1, 2, 3],
                ),
                {0: [0, 1]},
                ([1], [2]),
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_get_df_indices(
        self, df, touching_geometry, expected_result
    ):
        """Unit test of DissolveTouchingGeometry _get_df_indices method.

        Args:
            df: df
            touching_geometry: touching geometry index
            expected_result: expected results
        """
        dtg = DissolveTouchingGeometry(df)
        result = dtg._get_df_indices(touching_geometry)
        assert expected_result == result

    @pytest.mark.parametrize(
        "df, expected_result",
        [
            (gpd.GeoDataFrame({"geometry": []}), gpd.GeoDataFrame({"geometry": []})),
            (
                gpd.GeoDataFrame(
                    {"geometry": [Point(1, 2), Point(1, 2)]}, index=[1, 2]
                ),
                gpd.GeoDataFrame(
                    {"geometry": [Point(1, 2), Point(1, 2)]}, index=[1, 2]
                ),
            ),
            (
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, 1.0),
                                    (0.0, 1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, -1.0),
                                    (0.0, -1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 1.0),
                                    (1.0, 1.0),
                                    (1.0, 2.0),
                                    (0.0, 2.0),
                                    (0.0, 1.0),
                                )
                            ),
                        ]
                    },
                    index=[1, 2, 3],
                ),
                gpd.GeoDataFrame(
                    {
                        "geometry": Polygon(
                            (
                                (0.0, -1.0),
                                (1.0, -1.0),
                                (1.0, 2.0),
                                (0.0, 2.0),
                                (0.0, -1.0),
                            )
                        ),
                    },
                    index=[1],
                ),
            ),
            (
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, 1.0),
                                    (0.0, 1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (1.0, 0.0),
                                    (1.0, -1.0),
                                    (0.0, -1.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 2.0),
                                    (1.0, 2.0),
                                    (1.0, 3.0),
                                    (0.0, 3.0),
                                    (0.0, 2.0),
                                )
                            ),
                        ]
                    },
                    index=[1, 2, 3],
                ),
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                (
                                    (0.0, -1.0),
                                    (1.0, -1.0),
                                    (1.0, 1.0),
                                    (0.0, 1.0),
                                    (0.0, -1.0),
                                )
                            ),
                            Polygon(
                                (
                                    (0.0, 2.0),
                                    (1.0, 2.0),
                                    (1.0, 3.0),
                                    (0.0, 3.0),
                                    (0.0, 2.0),
                                )
                            ),
                        ]
                    },
                    index=[1, 3],
                ),
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_dissolve_and_explode(
        self, df, expected_result
    ):
        """Unit test of DissolveTouchingGeometry dissolve_and_explode method.

        Args:
            df: df
            expected_result: expected results
        """
        dtg = DissolveTouchingGeometry(df)
        result = dtg.dissolve_and_explode()
        testing.assert_geodataframe_equal(expected_result, result)

    @pytest.mark.parametrize(
        "df, expected_result",
        [
            (gpd.GeoDataFrame({"geometry": []}), gpd.GeoDataFrame({"geometry": []})),
            (
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
                                [
                                    [
                                        (0.25, 0.25),
                                        (0.75, 0.25),
                                        (0.75, 0.75),
                                        (0.25, 0.75),
                                        (0.25, 0.25),
                                    ][::-1]
                                ],
                            ),
                        ]
                    },
                    index=[1],
                ),
                gpd.GeoDataFrame(
                    {
                        "geometry": Polygon(
                            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
                        ),
                    },
                    index=[0],
                ),
            ),
            (
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                Polygon(
                                    [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
                                    [
                                        [
                                            (0.25, 0.25),
                                            (0.75, 0.25),
                                            (0.75, 0.75),
                                            (0.25, 0.75),
                                            (0.25, 0.25),
                                        ][::-1]
                                    ],
                                ),
                            ),
                            Polygon(
                                [(0, 3), (1, 3), (1, 4), (0, 4), (0, 3)],
                            ),
                        ]
                    },
                    index=[1, 2],
                ),
                gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Polygon(
                                [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
                            ),
                            Polygon(
                                [(0, 3), (1, 3), (1, 4), (0, 4), (0, 3)],
                            ),
                        ]
                    },
                    index=[0, 0],
                ),
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_dissolve_and_explode_exterior(
        self, df, expected_result
    ):
        """Unit test of DissolveTouchingGeometry dissolve_and_explode_exterior method.

        Args:
            df: df
            expected_result: expected results
        """
        dtg = DissolveTouchingGeometry(df)
        result = dtg.dissolve_and_explode_exterior()
        testing.assert_geodataframe_equal(expected_result, result)


class TestUnitGeometry:
    """Unit tests of Geometry."""

    @patch("lantmateriet.geometry.gpd.read_file")
    def test_unit_init(self, mock_read_file):
        """Unit test of Geometry __init__ method.

        Args:
            mock_read_file: mock of read_file
        """
        _ = Geometry("filename", layer="mask", use_arrow=True)
        mock_read_file.assert_called_with("filename", layer="mask", use_arrow=True)

    @pytest.mark.parametrize(
        "input_df",
        [
            gpd.GeoDataFrame(
                {
                    "geometry": [
                        Polygon(
                            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
                        ),
                    ]
                },
            ),
        ],
    )
    def test_unit_set_area(self, input_df):
        """Unit test of Geometry _set_area method.

        Args:
            input_df: input_df
        """
        result = Geometry._set_area(input_df)
        assert "area_m2" in result

    @pytest.mark.parametrize(
        "input_df",
        [
            gpd.GeoDataFrame(
                {
                    "geometry": [
                        Polygon(
                            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
                        ),
                    ]
                },
            ),
        ],
    )
    def test_unit_set_length(self, input_df):
        """Unit test of Geometry _set_length method.

        Args:
            input_df: input_df
        """
        result = Geometry._set_length(input_df)
        assert "length_m" in result

    @patch("lantmateriet.geometry.DissolveTouchingGeometry")
    def test_unit_dissolve(self, mock_DissolveTouchingGeometry):
        """Unit test of Geometry _dissolve method.

        Args:
            mock_DissolveTouchingGeometry: mock of mock_DissolveTouchingGeometry
        """
        object_name, df = "object_name", gpd.GeoDataFrame()
        result = Geometry._dissolve(object_name, df)
        assert object_name == result[0]
        assert (
            mock_DissolveTouchingGeometry.return_value.dissolve_and_explode.return_value
            == result[1]
        )
        mock_DissolveTouchingGeometry.assert_called_with(df)
        mock_DissolveTouchingGeometry.return_value.dissolve_and_explode.assert_called()

    @patch("lantmateriet.geometry.DissolveTouchingGeometry")
    def test_unit_dissolve_exterior(self, mock_DissolveTouchingGeometry):
        """Unit test of Geometry _dissolve_exterior method.

        Args:
            mock_DissolveTouchingGeometry: mock of mock_DissolveTouchingGeometry
        """
        object_name, df = "object_name", gpd.GeoDataFrame()
        result = Geometry._dissolve_exterior(object_name, df)
        assert object_name == result[0]
        assert (
            mock_DissolveTouchingGeometry.return_value.dissolve_and_explode_exterior.return_value
            == result[1]
        )
        mock_DissolveTouchingGeometry.assert_called_with(df)
        mock_DissolveTouchingGeometry.return_value.dissolve_and_explode_exterior.assert_called()
