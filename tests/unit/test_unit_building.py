"""Building unit tests."""
from unittest.mock import patch

import geopandas as gpd
import pytest
from lantmateriet import config
from lantmateriet.building import Building


class TestUnitBuilding:
    """Unit tests of Building."""

    @pytest.mark.parametrize(
        "file_name, detail_level, layer, use_arrow, df, expected_result",
        [
            (
                "path",
                "50",
                "mark",
                True,
                gpd.GeoDataFrame(
                    {"objekttyp": [k for k in config.config_50.building.keys()]}
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
                            for k in config.config_50.building.keys()
                            if k not in {"Bostad"}
                        ]
                    }
                ),
                None,
            ),
        ],
    )
    @patch("lantmateriet.geometry.gpd.read_file")
    def test_unit_building_init(
        self,
        mcck_gpd_read_file,
        file_name,
        detail_level,
        layer,
        use_arrow,
        df,
        expected_result,
    ):
        """Unit test of Building __init__ method.

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
                building = Building(file_name, detail_level, layer, use_arrow)
        else:
            building = Building(file_name, detail_level, layer, use_arrow)
            mcck_gpd_read_file.assert_called_with(
                file_name, layer=layer, use_arrow=use_arrow
            )
            assert building.config == expected_result

    @patch("lantmateriet.building.Building._process")
    @patch("lantmateriet.building.Building.__init__", return_value=None)
    def test_unit_building_process(self, mock_building_init, mock_building_process):
        """Unit test of Building process method.

        Args:
            mock_building_init: mock of Geometry __init__
            mock_building_process: mock of Building _process
        """
        building = Building("path")
        building.process()
        mock_building_process.assert_called_once_with("building", True, True)

    @patch("lantmateriet.building.Building._save")
    @patch("lantmateriet.building.Building.__init__", return_value=None)
    def test_unit_building_save(self, mock_building_init, mock_building_save):
        """Unit test of Building save method.

        Args:
            mock_building_init: mock of Geometry __init__
            mock_building_save: mock of Building _save
        """
        building = Building("path")
        building.save({}, "path")
        mock_building_save.assert_called_once_with("building", {}, "path")
