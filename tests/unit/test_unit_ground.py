"""Ground unit tests."""
from unittest.mock import call, patch

import geopandas as gpd
import pytest
from geopandas import testing
from lantmateriet import config
from lantmateriet.ground import Ground
from shapely.geometry import Polygon


class TestUnitGround:
    """Unit tests of Ground."""

    @pytest.mark.parametrize(
        "file_name, detail_level, layer, use_arrow, df, expected_result",
        [
            (
                "path",
                "50",
                "mark",
                True,
                gpd.GeoDataFrame(
                    {"objekttyp": [k for k in config.config_50.ground.keys()]}
                ),
                config.config_50,
            ),
            (
                "path",
                "1m",
                "mark",
                True,
                gpd.GeoDataFrame(
                    {"objekttyp": [k for k in config.config_1m.ground.keys()]}
                ),
                config.config_1m,
            ),
            (
                "path",
                "50",
                "mark",
                True,
                gpd.GeoDataFrame(
                    {
                        "objekttyp": [
                            k
                            for k in config.config_50.ground.keys()
                            if k not in config.config_50.exclude
                        ]
                    }
                ),
                None,
            ),
            (
                "path",
                "1",
                "mark",
                True,
                gpd.GeoDataFrame(
                    {"objekttyp": [k for k in config.config_50.ground.keys()]}
                ),
                None,
            ),
        ],
    )
    @patch("lantmateriet.geometry.gpd.read_file")
    def test_unit_ground_init(
        self,
        mcck_gpd_read_file,
        file_name,
        detail_level,
        layer,
        use_arrow,
        df,
        expected_result,
    ):
        """Unit test of Ground __init__ method.

        Args;
            mcck_gpd_read_file: mock of gpd read_file
            file_name: file_name
            detail_level: detail_level
            layer: layer
            use_arrow: arrow flag
            df: dataframe
            expected_result: expected result
        """
        mcck_gpd_read_file.return_value = df
        if detail_level in {"50", "1m"}:
            if expected_result is None:
                with pytest.raises(KeyError):
                    ground = Ground(file_name, detail_level, layer, use_arrow)
            else:
                ground = Ground(file_name, detail_level, layer, use_arrow)
                mcck_gpd_read_file.assert_called_with(
                    file_name, layer=layer, use_arrow=use_arrow
                )
                assert ground.config == expected_result
        else:
            with pytest.raises(NotImplementedError):
                ground = Ground(file_name, detail_level, layer, use_arrow)

    @pytest.mark.parametrize(
        "set_area, set_length, key, dissolved_geometry",
        [
            (
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
    @patch("lantmateriet.ground.Ground._get_items")
    @patch("lantmateriet.ground.Ground._execute_dissolve_parallel")
    @patch("lantmateriet.ground.Ground.__init__", return_value=None)
    def test_unit_get_ground(
        self,
        mock_ground_init,
        mock_execute_dissolve_parallel,
        mock_get_items,
        set_area,
        set_length,
        key,
        dissolved_geometry,
    ):
        """Unit test of Ground get_ground method.

        Args:
            mock_ground_init: mock of Ground init
            mock_execute_dissolve_parallel: mock of Ground _execute_dissolve_parallel
            mock_get_items: mock of Ground _get_items
            set_area: set area flag
            set_length: set length flag
            key: key
            dissolved_geometry: dissolved geometry
        """
        mock_execute_dissolve_parallel.return_value = dissolved_geometry
        ground = Ground("path")

        result = ground.get_ground(set_area, set_length)

        mock_get_items.assert_called_once_with("ground")
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
    @patch("lantmateriet.ground.Ground.__init__", return_value=None)
    def test_unit_save_ground(self, mock_geometry_init, mock_to_file):
        """Unit test of Ground save_ground method.

        Args:
            mock_geometry_init: mock of Geometry init
            mock_to_file: mock of GeoDataFrame to_file
        """
        ground = Ground("path")
        ground.df = gpd.GeoDataFrame({"objekttyp": ["objekttyp"]})
        ground.config = config.config_50

        all_ground = {
            k: gpd.GeoDataFrame(
                {"objekttyp": ["objekttyp"]},
                geometry=[Polygon([(0, 0), (1, 1), (1, 0)])],
                crs=config.config_50.espg_3006,
            )
            for k in config.config_50.ground.keys()
            if k not in config.config_50.exclude
        }

        ground.save_ground(all_ground, "path_to_save")

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
