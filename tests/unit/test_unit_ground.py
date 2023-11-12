"""Ground unit tests."""
from unittest.mock import patch

import geopandas as gpd
import pytest
from lantmateriet import config
from lantmateriet.ground import Ground


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

    @patch("lantmateriet.ground.Ground._process")
    @patch("lantmateriet.ground.Ground.__init__", return_value=None)
    def test_unit_ground_process(self, mock_geometry_init, mock_ground_process):
        """Unit test of Ground process method.

        Args:
            mock_geometry_init: mock of Geometry __init__
            mock_ground_process: mock of Ground _process
        """
        ground = Ground("path")
        ground.process("ground")
        mock_ground_process.assert_called_once_with("ground", True, True)

    @patch("lantmateriet.ground.Ground._save")
    @patch("lantmateriet.ground.Ground.__init__", return_value=None)
    def test_unit_ground_save(self, mock_geometry_init, mock_ground_save):
        """Unit test of Ground save method.

        Args:
            mock_geometry_init: mock of Geometry __init__
            mock_ground_save: mock of Ground _save
        """
        ground = Ground("path")
        ground.save("ground", {}, "path")
        mock_ground_save.assert_called_once_with("ground", {}, "path")
