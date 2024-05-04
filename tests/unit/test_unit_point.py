"""Point unit tests."""

from unittest.mock import patch

import geopandas as gpd
import pytest
from lantmateriet import config
from lantmateriet.point import Point


class TestUnitPoint:
    """Unit tests of Point."""

    @pytest.mark.parametrize(
        "file_name, detail_level, layer, use_arrow, df, expected_result",
        [
            (
                "path",
                "50",
                "byggnad",
                True,
                gpd.GeoDataFrame(
                    {
                        "objekttyp": [
                            k for k in config.config_50.construction["byggnad"].keys()
                        ]
                    }
                ),
                config.config_50,
            ),
            (
                "path",
                "50",
                "byggnad",
                True,
                gpd.GeoDataFrame(
                    {
                        "objekttyp": [
                            k
                            for k in config.config_50.construction["byggnad"].keys()
                            if k not in {"Bostad"}
                        ]
                    }
                ),
                None,
            ),
        ],
    )
    @patch("lantmateriet.geometry.gpd.read_file")
    def test_unit_construction_init(
        self,
        mock_gpd_read_file,
        file_name,
        detail_level,
        layer,
        use_arrow,
        df,
        expected_result,
    ):
        """Unit test of Point __init__ method.

        Args;
            mock_gpd_read_file: mock of gpd read_file
            file_name: file_name
            detail_level: detail_level
            layer: layer
            use_arrow: arrow flag
            df: dataframe
            expected_result: expected result
        """
        mock_gpd_read_file.return_value = df
        if expected_result is None:
            with pytest.raises(KeyError):
                construction = Point(file_name, detail_level, layer, use_arrow)
        else:
            construction = Point(file_name, detail_level, layer, use_arrow)
            mock_gpd_read_file.assert_called_with(
                file_name, layer=layer, use_arrow=use_arrow
            )
            assert construction.config == expected_result

    @patch("lantmateriet.construction.Point._process")
    @patch("lantmateriet.construction.Point.__init__", return_value=None)
    def test_unit_construction_process(
        self, mock_construction_init, mock_construction_process
    ):
        """Unit test of Point process method.

        Args:
            mock_construction_init: mock of Point __init__
            mock_construction_process: mock of Point _process
        """
        construction = Point("path")
        construction.item_type = "construction"
        construction.layer = "byggnad"
        construction.dissolve = True

        construction.process()
        mock_construction_process.assert_called_once_with(
            "construction", "byggnad", True, True, True
        )

    @patch("lantmateriet.construction.Point._save")
    @patch("lantmateriet.construction.Point.__init__", return_value=None)
    def test_unit_construction_save(
        self, mock_construction_init, mock_construction_save
    ):
        """Unit test of construction save method.

        Args:
            mock_construction_init: mock of Point __init__
            mock_construction_save: mock of Point _save
        """
        construction = Point("path")
        construction.item_type = "construction"
        construction.layer = "byggnad"

        construction.save({}, "path")
        mock_construction_save.assert_called_once_with(
            "construction", "byggnad", {}, "path"
        )
