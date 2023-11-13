"""Construction unit tests."""
from unittest.mock import patch

import geopandas as gpd
import pytest
from lantmateriet import config
from lantmateriet.construction import Construction


class TestUnitConstruction:
    """Unit tests of Construction."""

    @pytest.mark.parametrize(
        "file_name, detail_level, layer, use_arrow, df, expected_result",
        [
            (
                "path",
                "50",
                "mark",
                True,
                gpd.GeoDataFrame(
                    {"objekttyp": [k for k in config.config_50.construction.keys()]}
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
                            for k in config.config_50.construction.keys()
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
        mcck_gpd_read_file,
        file_name,
        detail_level,
        layer,
        use_arrow,
        df,
        expected_result,
    ):
        """Unit test of Construction __init__ method.

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
                construction = Construction(file_name, detail_level, layer, use_arrow)
        else:
            construction = Construction(file_name, detail_level, layer, use_arrow)
            mcck_gpd_read_file.assert_called_with(
                file_name, layer=layer, use_arrow=use_arrow
            )
            assert construction.config == expected_result

    @patch("lantmateriet.construction.Construction._process")
    @patch("lantmateriet.construction.Construction.__init__", return_value=None)
    def test_unit_construction_process(
        self, mock_construction_init, mock_construction_process
    ):
        """Unit test of Construction process method.

        Args:
            mock_construction_init: mock of Geometry __init__
            mock_construction_process: mock of Construction _process
        """
        construction = Construction("path")
        construction.process()
        mock_construction_process.assert_called_once_with("construction", True, True)

    @patch("lantmateriet.construction.Construction._save")
    @patch("lantmateriet.construction.Construction.__init__", return_value=None)
    def test_unit_construction_save(
        self, mock_construction_init, mock_construction_save
    ):
        """Unit test of construction save method.

        Args:
            mock_construction_init: mock of Construction __init__
            mock_construction_save: mock of Construction _save
        """
        construction = Construction("path")
        construction.save({}, "path")
        mock_construction_save.assert_called_once_with("construction", {}, "path")
