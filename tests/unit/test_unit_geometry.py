"""Geometry unit tests."""

from unittest.mock import MagicMock, call, patch

import geopandas as gpd
import numpy as np
import pytest
from geopandas import testing
from shapely.geometry import Point, Polygon

from lantmateriet import config
from lantmateriet.geometry import DissolveTouchingGeometry, Geometry


def square(x: float, y: float) -> Polygon:
    """Unit square with its lower left corner at (x, y)."""
    return Polygon([(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1), (x, y)])


class TestUnitDissolveTouchingGeometry:
    """Unit tests of DissolveTouchingGeometry."""

    def test_unit_dissolvetouchinggeometry_init(self):
        """Unit test of DissolveTouchingGeometry init method."""
        df = gpd.GeoDataFrame()
        dtg = DissolveTouchingGeometry(df)
        testing.assert_geodataframe_equal(dtg.df, df)

    @pytest.mark.parametrize(
        "df, expected_result",
        [
            (gpd.GeoDataFrame({"geometry": []}), []),
            (
                gpd.GeoDataFrame({"geometry": [Point(1, 2), Point(1, 2)]}),
                [0, 0],
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
                    }
                ),
                [0, 0, 0],
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
                [0, 0, 1],
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_get_component_labels(self, df, expected_result):
        """Unit test of DissolveTouchingGeometry _get_component_labels method.

        Args:
            df: df
            expected_result: expected component labels
        """
        dtg = DissolveTouchingGeometry(df)
        result = dtg._get_component_labels()
        np.testing.assert_array_equal(result, expected_result)

    @pytest.mark.parametrize(
        "df, merge_key, expected_result",
        [
            (
                gpd.GeoDataFrame(
                    {"vattenytaid": ["a", "a"], "geometry": [square(0, 0), square(1, 0)]}
                ),
                "vattenytaid",
                [0, 0],
            ),
            (
                gpd.GeoDataFrame(
                    {"vattenytaid": ["a", "b"], "geometry": [square(0, 0), square(1, 0)]}
                ),
                "vattenytaid",
                [0, 1],
            ),
            (
                gpd.GeoDataFrame(
                    {"vattenytaid": ["a", None], "geometry": [square(0, 0), square(1, 0)]}
                ),
                "vattenytaid",
                [0, 1],
            ),
            (
                gpd.GeoDataFrame(
                    {"vattenytaid": [None, None], "geometry": [square(0, 0), square(1, 0)]}
                ),
                "vattenytaid",
                [0, 0],
            ),
            (
                gpd.GeoDataFrame({"geometry": [square(0, 0), square(1, 0)]}),
                "vattenytaid",
                [0, 1],
            ),
            (
                gpd.GeoDataFrame(
                    {"vattenytaid": ["a", "b"], "geometry": [square(0, 0), square(1, 0)]}
                ),
                None,
                [0, 0],
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_get_component_labels_merge_key(
        self, df, merge_key, expected_result
    ):
        """Unit test of DissolveTouchingGeometry _get_component_labels merge key.

        Args:
            df: df
            merge_key: merge key column name
            expected_result: expected component labels
        """
        dtg = DissolveTouchingGeometry(df, merge_key=merge_key)
        result = dtg._get_component_labels()
        np.testing.assert_array_equal(result, expected_result)

    @pytest.mark.parametrize(
        "df, merge_key, expected_result",
        [
            (
                gpd.GeoDataFrame(
                    {
                        "objekttyp": ["Sjö", "Sjö"],
                        "vattenytaid": ["a", "a"],
                        "geometry": [square(0, 0), square(1, 0)],
                    }
                ),
                "vattenytaid",
                gpd.GeoDataFrame(
                    {
                        "objekttyp": ["Sjö"],
                        "vattenytaid": ["a"],
                        "geometry": [Polygon([(0, 0), (2, 0), (2, 1), (0, 1), (0, 0)])],
                    },
                    index=[0],
                ),
            ),
            (
                gpd.GeoDataFrame(
                    {
                        "objekttyp": ["Sjö", "Sjö"],
                        "vattenytaid": ["a", "b"],
                        "geometry": [square(0, 0), square(1, 0)],
                    }
                ),
                "vattenytaid",
                gpd.GeoDataFrame(
                    {
                        "objekttyp": ["Sjö", "Sjö"],
                        "vattenytaid": ["a", "b"],
                        "geometry": [square(0, 0), square(1, 0)],
                    },
                    index=[0, 1],
                ),
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_dissolve_and_explode_merge_key(
        self, df, merge_key, expected_result
    ):
        """Unit test of DissolveTouchingGeometry dissolve_and_explode merge key.

        Args:
            df: df
            merge_key: merge key column name
            expected_result: expected results
        """
        dtg = DissolveTouchingGeometry(df, merge_key=merge_key)
        result = dtg.dissolve_and_explode()
        testing.assert_geodataframe_equal(expected_result, result)

    @pytest.mark.parametrize(
        "df, expected_result",
        [
            (gpd.GeoDataFrame({"geometry": []}), gpd.GeoDataFrame({"geometry": []})),
            (
                gpd.GeoDataFrame({"geometry": [Point(1, 2), Point(1, 2)]}),
                gpd.GeoDataFrame({"geometry": [Point(1, 2)]}),
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
            (
                gpd.GeoDataFrame(
                    {
                        "objekttyp": ["Sjö", "Sjö", "Sjö", "Åker"],
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
                                    (1.0, 0.0),
                                    (2.0, 0.0),
                                    (2.0, 1.0),
                                    (1.0, 1.0),
                                    (1.0, 0.0),
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
                            Polygon(
                                (
                                    (10.0, 0.0),
                                    (11.0, 0.0),
                                    (11.0, 1.0),
                                    (10.0, 1.0),
                                    (10.0, 0.0),
                                )
                            ),
                        ],
                    }
                ),
                gpd.GeoDataFrame(
                    {
                        "objekttyp": ["Sjö", "Åker"],
                        "geometry": [
                            Polygon(
                                (
                                    (0.0, 0.0),
                                    (2.0, 0.0),
                                    (2.0, 1.0),
                                    (1.0, 1.0),
                                    (1.0, 2.0),
                                    (0.0, 2.0),
                                    (0.0, 0.0),
                                )
                            ),
                            Polygon(
                                (
                                    (10.0, 0.0),
                                    (11.0, 0.0),
                                    (11.0, 1.0),
                                    (10.0, 1.0),
                                    (10.0, 0.0),
                                )
                            ),
                        ],
                    },
                    index=[0, 1],
                ),
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_dissolve_and_explode(self, df, expected_result):
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
            (
                gpd.GeoDataFrame({"geometry": [], "objekttyp": []}, crs=config.config_50.espg_3006),
                gpd.GeoDataFrame({"geometry": [], "objekttyp": []}, crs=config.config_50.espg_3006),
            ),
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
                        ],
                        "objekttyp": ["Sjö"],
                    },
                    index=[1],
                    crs=config.config_50.espg_3006,
                ),
                gpd.GeoDataFrame(
                    {
                        "geometry": Polygon(
                            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
                        ),
                        "objekttyp": ["Sjö"],
                    },
                    index=[0],
                    crs=config.config_50.espg_3006,
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
                        ],
                        "objekttyp": ["Sjö"],
                    },
                    index=[1, 2],
                    crs=config.config_50.espg_3006,
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
                        ],
                        "objekttyp": ["Sjö"],
                    },
                    index=[0, 1],
                    crs=config.config_50.espg_3006,
                ),
            ),
        ],
    )
    def test_unit_dissolvetouchinggeometry_dissolve_and_explode_exterior(self, df, expected_result):
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
        "file_name, detail_level, layer, name, field, expected_result",
        [
            ("path", "50", "mark", "name", "field", config.config_50),
            ("path", "1m", "mark", "name", "field", config.config_1m),
            ("path", "50", "mark", "name", "field", config.config_50),
            ("path", "1", "mark", "name", "field", None),
        ],
    )
    @patch("lantmateriet.geometry.gpd.read_file")
    def test_unit_init(
        self,
        mock_read_file,
        file_name,
        detail_level,
        layer,
        name,
        field,
        expected_result,
    ):
        """Unit test of Geometry __init__ method."""
        if detail_level not in {"50", "1m"}:
            with pytest.raises(NotImplementedError):
                _ = Geometry(file_name, detail_level, layer, name, field)
        else:
            geometry = Geometry(file_name, detail_level, layer, name, field)
            # mock_read_file.assert_called_once_with(file_name, layer)
            assert geometry.config == expected_result
            assert geometry._file_path == file_name
            assert geometry._layer == layer
            assert geometry._name == name
            assert geometry._field == field

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
        """Unit test of Geometry _set_area method."""
        result = Geometry._set_area(input_df)
        assert "area_m2" in result

    @pytest.mark.parametrize(
        "input_df",
        [
            gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])]}),
        ],
    )
    def test_unit_set_length(self, input_df):
        """Unit test of Geometry _set_length method."""
        result = Geometry._set_length(input_df)
        assert "length_m" in result

    @patch("lantmateriet.geometry.DissolveTouchingGeometry")
    def test_unit_dissolve(self, mock_DissolveTouchingGeometry):
        """Unit test of Geometry _dissolve method."""
        df = gpd.GeoDataFrame()
        result = Geometry._dissolve(df, "vattenytaid")

        assert (
            mock_DissolveTouchingGeometry.return_value.dissolve_and_explode.return_value == result
        )
        mock_DissolveTouchingGeometry.assert_called_with(df, merge_key="vattenytaid")
        mock_DissolveTouchingGeometry.return_value.dissolve_and_explode.assert_called()

    @patch("lantmateriet.geometry.DissolveTouchingGeometry")
    def test_unit_dissolve_exterior(self, mock_DissolveTouchingGeometry):
        """Unit test of Geometry _dissolve_exterior method.

        Args:
            mock_DissolveTouchingGeometry: mock of mock_DissolveTouchingGeometry
        """
        df = gpd.GeoDataFrame()
        result = Geometry._dissolve_exterior(df)

        assert (
            mock_DissolveTouchingGeometry.return_value.dissolve_and_explode_exterior.return_value
            == result
        )
        mock_DissolveTouchingGeometry.assert_called_with(df)
        mock_DissolveTouchingGeometry.return_value.dissolve_and_explode_exterior.assert_called()

    @pytest.mark.parametrize(
        "name, dissolve, set_area, set_length, input_geometry, dissolved_geometry",
        [
            (
                "Barr- och blandskog",
                True,
                False,
                False,
                gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])]}),
                gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])]}),
            ),
            (
                "name",
                True,
                False,
                False,
                gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])]}),
                gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])]}),
            ),
            (
                "name",
                True,
                True,
                False,
                gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])]}),
                gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])], "area_m2": 0.5}),
            ),
            (
                "name",
                True,
                False,
                True,
                gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])]}),
                gpd.GeoDataFrame(
                    {
                        "geometry": [Polygon([(0, 0), (1, 1), (1, 0)])],
                        "length_m": 2 + np.sqrt(2),
                    }
                ),
            ),
            (
                "name",
                True,
                True,
                True,
                gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])]}),
                gpd.GeoDataFrame(
                    {
                        "geometry": [Polygon([(0, 0), (1, 1), (1, 0)])],
                        "area_m2": 0.5,
                        "length_m": 2 + np.sqrt(2),
                    }
                ),
            ),
            (
                "name",
                False,
                True,
                True,
                gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])]}),
                gpd.GeoDataFrame(
                    {
                        "geometry": [Polygon([(0, 0), (1, 1), (1, 0)])],
                        "area_m2": 0.5,
                        "length_m": 2 + np.sqrt(2),
                    }
                ),
            ),
        ],
    )
    @patch("lantmateriet.geometry.gpd.read_file")
    @patch("lantmateriet.geometry.Geometry._dissolve_exterior")
    @patch("lantmateriet.geometry.Geometry._dissolve")
    def test_unit_process(
        self,
        mock_dissolve,
        mock_dissolve_exterior,
        mock_df_read_file,
        name,
        dissolve,
        set_area,
        set_length,
        input_geometry,
        dissolved_geometry,
    ):
        """Unit test of Geometry _process method."""
        if dissolve:
            if name == "name":
                mock_dissolve.return_value = input_geometry
            else:
                mock_dissolve_exterior.return_value = input_geometry

        geometry = Geometry("path", "50", "layer", name, "field")
        geometry.df = input_geometry

        geometry._process(dissolve, set_area, set_length)

        testing.assert_geodataframe_equal(geometry.df, dissolved_geometry)

        if set_area is True:
            assert "area_m2" in geometry.df

        if set_area is False:
            assert "area_m2" not in geometry.df

        if set_length is True:
            assert "length_m" in geometry.df

        if set_length is False:
            assert "length_m" not in geometry.df

    @patch("lantmateriet.geometry.os.makedirs")
    @patch("lantmateriet.geometry.gpd.read_file")
    def test_unit_save(self, mock_df_read_file, mock_makedirs):
        """Unit test of Geometry _save method."""
        geometry = Geometry("path", "50", "layer", "name", "field")
        geometry.df = MagicMock()

        path = "path_to_save"
        file_name = "file"
        geometry._save(path, file_name)

        mock_makedirs.assert_called_once()
        geometry.df.to_crs.assert_has_calls(
            [
                call("EPSG:4326"),
                call().to_file("path_to_save/path/layer/file.fgb", driver="FlatGeobuf"),
            ]
        )
