"""Polygon unit tests."""

from unittest.mock import patch

import geopandas as gpd
import pytest
from lantmateriet import config
from lantmateriet.polygon import Polygon
from shapely.geometry import Point


class TestUnitPolygon:
    """Unit tests of Polygon."""

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
        """Unit test of Polygon __init__ method.

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
                ground = Polygon(file_name, detail_level, layer, use_arrow)
        else:
            ground = Polygon(file_name, detail_level, layer, use_arrow)
            mcck_gpd_read_file.assert_called_with(
                file_name, layer=layer, use_arrow=use_arrow
            )
            assert ground.config == expected_result

    @patch(
        "lantmateriet.ground.Polygon._process",
        return_value={
            "Sverige": gpd.GeoDataFrame(
                {"geometry": [Point(0, 0), Point(0, 1)], "objekttyp": "Sverige"}
            )
        },
    )
    @patch("lantmateriet.ground.Polygon.__init__", return_value=None)
    def test_unit_ground_process(self, mock_ground_init, mock_ground_process):
        """Unit test of Polygon process method.

        Args:
            mock_ground_init: mock of Polygon __init__
            mock_ground_process: mock of Polygon _process
        """
        ground = Polygon("path")
        ground.item_type = "ground"
        ground.layer = "mark"
        ground.dissolve = True
        ground.config = config.config_50

        ground.process()
        mock_ground_process.assert_called_once_with("ground", "mark", True, True, True)

    @patch("lantmateriet.ground.Polygon._save")
    @patch("lantmateriet.ground.Polygon.__init__", return_value=None)
    def test_unit_ground_save(self, mock_ground_init, mock_ground_save):
        """Unit test of Polygon save method.

        Args:
            mock_ground_init: mock of Polygon __init__
            mock_ground_save: mock of Polygon _save
        """
        ground = Polygon("path")
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
