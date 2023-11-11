"""Ground unit tests."""
from unittest.mock import call, patch

import geopandas as gpd
import pytest
from geopandas import testing
from lantmateriet.config import config
from lantmateriet.ground import Ground
from shapely.geometry import Polygon


class TestUnitGround:
    """Unit tests of Ground."""

    @pytest.mark.parametrize(
        "file_name, detail_level, layer, use_arrow, expected_result",
        [
            ("path", "50", "mark", True, config.ground_50),
            ("path", "1m", "mark", True, config.ground_1m),
            ("path", "1", "mark", True, None),
        ],
    )
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_ground_init(
        self,
        mock_geometry_init,
        file_name,
        detail_level,
        layer,
        use_arrow,
        expected_result,
    ):
        """Unit test of Ground __init__ method.

        Args;
            mock_geometry_init: mock of Geometry init
            file_name: file_name
            detail_level: detail_level
            layer: layer
            use_arrow: arrow flag
            expected_result: expected result
        """
        if detail_level in {"50", "1m"}:
            ground = Ground(file_name, detail_level, layer, use_arrow)

            mock_geometry_init.assert_called_with(file_name, layer, use_arrow)
            assert ground.config == expected_result
        else:
            with pytest.raises(NotImplementedError):
                ground = Ground(file_name, detail_level, layer, use_arrow)

    @pytest.mark.parametrize(
        "df, expected_result",
        [
            (
                gpd.GeoDataFrame({"objekttyp": [k for k in config.ground_50.keys()]}),
                [
                    (
                        k,
                        gpd.GeoDataFrame({"objekttyp": [k]}),
                    )
                    for k in config.ground_50.keys()
                    if k not in config.exclude_ground
                ],
            )
        ],
    )
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_get_ground_items(self, mock_geometry_init, df, expected_result):
        """Unit test of Ground _get_ground_items method.

        Args:
            mock_geometry_init: mock of Geometry init
            df: dataframe
            expected_result: expected result
        """
        ground = Ground("path")
        ground.df = df
        ground.config = config.ground_50

        ground_items = ground._get_ground_items()

        assert all([x[0] == y[0] for x, y in zip(ground_items, expected_result)])
        for (_, x), (_, y) in zip(ground_items, expected_result):
            assert x.objekttyp.iloc[0] == y.objekttyp.iloc[0]

    @pytest.mark.parametrize(
        "df, set_area, set_length, key, dissolved_geometry, raise_error",
        [
            (
                gpd.GeoDataFrame({"objekttyp": [k for k in config.ground_50.keys()]}),
                False,
                False,
                "Sjö",
                [
                    (
                        "Sjö",
                        gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (1, 1), (1, 0)])]),
                    )
                ],
                False,
            ),
            (
                gpd.GeoDataFrame({"objekttyp": [k for k in config.ground_50.keys()]}),
                True,
                False,
                "Sjö",
                [
                    (
                        "Sjö",
                        gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (1, 1), (1, 0)])]),
                    )
                ],
                False,
            ),
            (
                gpd.GeoDataFrame({"objekttyp": [k for k in config.ground_50.keys()]}),
                False,
                True,
                "Sjö",
                [
                    (
                        "Sjö",
                        gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (1, 1), (1, 0)])]),
                    )
                ],
                False,
            ),
            (
                gpd.GeoDataFrame({"objekttyp": [k for k in config.ground_50.keys()]}),
                True,
                True,
                "Sjö",
                [
                    (
                        "Sjö",
                        gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (1, 1), (1, 0)])]),
                    )
                ],
                False,
            ),
            (
                gpd.GeoDataFrame(
                    {
                        "objekttyp": [
                            k
                            for k in config.ground_50.keys()
                            if k not in config.exclude_ground
                        ]
                    }
                ),
                False,
                False,
                None,
                None,
                True,
            ),
        ],
    )
    @patch("lantmateriet.ground.Pool")
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_get_ground(
        self,
        mock_geometry_init,
        mock_pool,
        df,
        set_area,
        set_length,
        key,
        dissolved_geometry,
        raise_error,
    ):
        """Unit test of Ground get_ground method.

        Args:
            mock_geometry_init: mock of Geometry init
            mock_pool: mock of Pool
            df: dataframe
            set_area: set area flag
            set_length: set length flag
            key: key
            dissolved_geometry: dissolved geometry
            raise_error: raise error flag
        """
        ground = Ground("path")
        ground.df = df
        ground.config = config.ground_50
        _ = ground._get_ground_items()

        mock_starmap = mock_pool.return_value.__enter__.return_value.starmap

        if raise_error is True:
            with pytest.raises(KeyError):
                ground.get_ground(set_area, set_length)
        else:
            mock_starmap.return_value = dissolved_geometry
            result = ground.get_ground(set_area, set_length)

            # mock_starmap.assert_called_once_with(smap, [])
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
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_save_ground(self, mock_geometry_init, mock_to_file):
        """Unit test of Ground save_ground method.

        Args:
            mock_geometry_init: mock of Geometry init
            mock_to_file: mock of GeoDataFrame to_file
        """
        ground = Ground("path")
        ground.df = gpd.GeoDataFrame({"objekttyp": ["objekttyp"]})
        ground.config = config.ground_50

        all_ground = {
            k: gpd.GeoDataFrame(
                {"objekttyp": ["objekttyp"]},
                geometry=[Polygon([(0, 0), (1, 1), (1, 0)])],
                crs=config.espg_3006,
            )
            for k in config.ground_50.keys()
            if k not in config.exclude_ground
        }

        ground.save_ground(all_ground, "path_to_save")

        mock_to_file.assert_has_calls(
            [
                call(
                    f"path_to_save/{file_name}",
                    driver="GeoJSON",
                )
                for k, file_name in config.ground_50.items()
                if k not in config.exclude_ground
            ],
            any_order=True,
        )
