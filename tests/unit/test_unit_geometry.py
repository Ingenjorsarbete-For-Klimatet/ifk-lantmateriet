"""Geometry unit tests."""
from copy import deepcopy
from unittest.mock import call, patch

import geopandas as gpd
import pytest
from geopandas import testing
from lantmateriet import config
from lantmateriet.geometry import DissolveTouchingGeometry, Geometry
from lantmateriet.utils import smap
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
                    index=[0],
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
                    index=[0, 1],
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
                    index=[0, 1],
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

    @pytest.mark.parametrize(
        "file_name, detail_level, layer, use_arrow, expected_result",
        [
            (
                "path",
                "50",
                "mark",
                True,
                config.config_50,
            ),
            (
                "path",
                "1m",
                "mark",
                True,
                config.config_1m,
            ),
            (
                "path",
                "50",
                "mark",
                False,
                config.config_50,
            ),
            (
                "path",
                "1",
                "mark",
                True,
                None,
            ),
        ],
    )
    @patch("lantmateriet.geometry.gpd.read_file")
    def test_unit_init(
        self, mock_read_file, file_name, detail_level, layer, use_arrow, expected_result
    ):
        """Unit test of Geometry __init__ method.

        Args:
            mock_read_file: mock of read_file
            file_name: file_name
            detail_level: detail_level
            layer: layer
            use_arrow: use_arrow
            expected_result: expected result
        """
        if detail_level not in {"50", "1m"}:
            with pytest.raises(NotImplementedError):
                _ = Geometry(
                    file_name,
                    detail_level=detail_level,
                    layer=layer,
                    use_arrow=use_arrow,
                )
        else:
            geometry = Geometry(
                file_name, detail_level=detail_level, layer=layer, use_arrow=use_arrow
            )
            mock_read_file.assert_called_once_with(
                file_name, layer=layer, use_arrow=use_arrow
            )
            assert geometry.config == expected_result

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

    @pytest.mark.parametrize(
        "df, item_type, config_ground, expected_result",
        [
            (
                gpd.GeoDataFrame({"objekttyp": ["Hav", "Sjö"]}),
                "ground",
                {"Hav": "hav", "Sjö": "sjö"},
                [("Sjö", gpd.GeoDataFrame({"objekttyp": ["Sjö"]}, index=[1]))],
            )
        ],
    )
    @patch("lantmateriet.geometry.Geometry.__init__", return_value=None)
    def test_unit_get_items(
        self, mock_geometry_init, df, item_type, config_ground, expected_result
    ):
        """Unit test of Geometry _get_items method.

        Args:
            mock_geometry_init: mock of Geometry init
            df: test dataframe
            item_type: item type
            config_ground: test config ground
            expected_result: expected result
        """
        test_config = deepcopy(config.config_50)
        test_config.ground = config_ground
        geometry = Geometry("path")
        geometry.df = df
        geometry.config = test_config

        geometry_items = geometry._get_items(item_type)

        assert all([x[0] == y[0] for x, y in zip(geometry_items, expected_result)])
        for (_, x), (_, y) in zip(geometry_items, expected_result):
            assert all(x.objekttyp == y.objekttyp)

    @pytest.mark.parametrize(
        "input, expected_result",
        [
            (
                [("Sjö", 1), ("Barr- och blandskog", 2)],
                [
                    (Geometry._dissolve, "Sjö", 1),
                    (Geometry._dissolve_exterior, "Barr- och blandskog", 2),
                ],
            )
        ],
    )
    @patch("lantmateriet.geometry.Geometry.__init__", return_value=None)
    def test_unit_prepare_parallel_list(self, mock_ground_init, input, expected_result):
        """Unit test of Geometry _prepare_parallel_list method.

        Args:
            mock_ground_init: mock of Ground init
            input: input
            expected_result: expected result
        """
        geometry = Geometry("path")
        geometry.config = config.config_50

        geometry_items = geometry._prepare_parallel_list(input)

        for x, y in zip(geometry_items, expected_result):
            assert x[0] == y[0]
            assert x[1] == y[1]
            assert x[2] == y[2]

    @patch("lantmateriet.geometry.Pool")
    @patch("lantmateriet.geometry.Geometry._prepare_parallel_list")
    @patch("lantmateriet.ground.Geometry.__init__", return_value=None)
    def test_unit_execute_disolve_parallel(
        self, mock_geometry_init, mock_prepare_list, mock_pool
    ):
        """Unit test of Geometry _execute_dissolve_parallel method.

        Args:
            mock_geometry_init: mock of Geometry init
            mock_prepare_list: mock of Geometry _prepare_parallel_list
            mock_pool: mock of Pool
        """
        input_list = []
        geometry = Geometry("path")
        dissolved_geometry = geometry._execute_dissolve_parallel(input_list)
        mock_prepare_list.assert_called_once_with(input_list)
        mock_pool.return_value.__enter__.return_value.starmap.assert_called_once_with(
            smap, mock_prepare_list.return_value
        )

        assert (
            dissolved_geometry
            == mock_pool.return_value.__enter__.return_value.starmap.return_value
        )

    @pytest.mark.parametrize(
        "item_type, set_area, set_length, key, dissolved_geometry",
        [
            (
                "ground",
                False,
                False,
                "Sjö",
                [
                    (
                        "Sjö",
                        gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (1, 1), (1, 0)])]),
                    )
                ],
            ),
            (
                "ground",
                True,
                False,
                "Sjö",
                [
                    (
                        "Sjö",
                        gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (1, 1), (1, 0)])]),
                    )
                ],
            ),
            (
                "ground",
                False,
                True,
                "Sjö",
                [
                    (
                        "Sjö",
                        gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (1, 1), (1, 0)])]),
                    )
                ],
            ),
            (
                "ground",
                True,
                True,
                "Sjö",
                [
                    (
                        "Sjö",
                        gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (1, 1), (1, 0)])]),
                    )
                ],
            ),
        ],
    )
    @patch("lantmateriet.geometry.Geometry._get_items")
    @patch("lantmateriet.geometry.Geometry._execute_dissolve_parallel")
    @patch("lantmateriet.geometry.Geometry.__init__", return_value=None)
    def test_unit_process(
        self,
        mock_geometry_init,
        mock_execute_dissolve_parallel,
        mock_get_items,
        item_type,
        set_area,
        set_length,
        key,
        dissolved_geometry,
    ):
        """Unit test of Geometry _process method.

        Args:
            mock_geometry_init: mock of Geometry init
            mock_execute_dissolve_parallel: mock of Geometry _execute_dissolve_parallel
            mock_get_items: mock of Geometry _get_items
            item_type: item type
            set_area: set area flag
            set_length: set length flag
            key: key
            dissolved_geometry: dissolved geometry
        """
        mock_execute_dissolve_parallel.return_value = dissolved_geometry
        geometry = Geometry("path")

        result = geometry._process(item_type, set_area, set_length)

        mock_get_items.assert_called_once_with(item_type)
        assert set(result.keys()) == set([x[0] for x in dissolved_geometry])
        testing.assert_geodataframe_equal(result[key], dissolved_geometry[0][1])

        if set_area is True:
            assert "area_m2" in result[key]

        if set_area is False:
            assert "area_m2" not in result[key]

        if set_length is True:
            assert "length_m" in result[key]

        if set_length is False:
            assert "length_m" not in result[key]

    @patch.object(gpd.GeoDataFrame, "to_file")
    @patch("lantmateriet.geometry.Geometry.__init__", return_value=None)
    def test_unit_save(self, mock_geometry_init, mock_to_file):
        """Unit test of Geometry _save method.

        Args:
            mock_geometry_init: mock of Geometry init
            mock_to_file: mock of GeoDataFrame to_file
        """
        geometry = Geometry("path")
        geometry.df = gpd.GeoDataFrame({"objekttyp": ["objekttyp"]})
        geometry.config = config.config_50

        item_type = "ground"
        all_geometry = {
            k: gpd.GeoDataFrame(
                {"objekttyp": ["objekttyp"]},
                geometry=[Polygon([(0, 0), (1, 1), (1, 0)])],
                crs=config.config_50.espg_3006,
            )
            for k in config.config_50[item_type].keys()
            if k not in config.config_50.exclude
        }

        geometry._save(item_type, all_geometry, "path_to_save")

        mock_to_file.assert_has_calls(
            [
                call(
                    f"path_to_save/{file_name}",
                    driver="GeoJSON",
                )
                for k, file_name in config.config_50.ground.items()
                if k not in config.config_50.exclude
            ],
            any_order=True,
        )
