"""Ground unit tests."""
from unittest.mock import patch

import geopandas as gpd
import pytest
from lantmateriet import config
from lantmateriet.ground import Ground
from shapely.geometry import Point


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
                    {"objekttyp": [k for k in config.config_50.ground["mark"].keys()]}
                ),
                config.config_50,
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
                            for k in config.config_50.ground["mark"].keys()
                            if k not in {"Sjö"}
                        ]
                    }
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
        if expected_result is None:
            with pytest.raises(KeyError):
                ground = Ground(file_name, detail_level, layer, use_arrow)
        else:
            ground = Ground(file_name, detail_level, layer, use_arrow)
            mcck_gpd_read_file.assert_called_with(
                file_name, layer=layer, use_arrow=use_arrow
            )
            assert ground.config == expected_result

    @patch(
        "lantmateriet.ground.Ground._process",
        return_value={
            "Sverige": gpd.GeoDataFrame(
                {"geometry": [Point(0, 0), Point(0, 1)], "objekttyp": "Sverige"}
            )
        },
    )
    @patch("lantmateriet.ground.Ground.__init__", return_value=None)
    def test_unit_ground_process(self, mock_ground_init, mock_ground_process):
        """Unit test of Ground process method.

        Args:
            mock_ground_init: mock of Ground __init__
            mock_ground_process: mock of Ground _process
        """
        ground = Ground("path")
        ground.item_type = "ground"
        ground.layer = "mark"
        ground.dissolve = True
        ground.config = config.config_50

        ground.process()
        mock_ground_process.assert_called_once_with("ground", "mark", True, True, True)

    @patch("lantmateriet.ground.Ground._save")
    @patch("lantmateriet.ground.Ground.__init__", return_value=None)
    def test_unit_ground_save(self, mock_ground_init, mock_ground_save):
        """Unit test of Ground save method.

        Args:
            mock_ground_init: mock of Ground __init__
            mock_ground_save: mock of Ground _save
        """
        ground = Ground("path")
        ground.item_type = "ground"
        ground.layer = "mark"
        ground.config = config.config_50
        expected_data = {
            k: v
            for k, v in config.config_50.ground["mark"].items()
            if k not in config.config_50.exteriorise
        }

        ground.save(config.config_50.ground["mark"], "path")

        mock_ground_save.assert_called_once_with(
            "ground", "mark", expected_data, "path"
        )
