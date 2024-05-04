"""Line unit tests."""

from unittest.mock import patch

import geopandas as gpd
import pytest
from lantmateriet import config
from lantmateriet.line import Line


class TestUnitLine:
    """Unit tests of Line."""

    @pytest.mark.parametrize(
        "file_name, detail_level, layer, use_arrow, df, expected_result",
        [
            (
                "path",
                "50",
                "vaglinje",
                True,
                gpd.GeoDataFrame(
                    {
                        "objekttyp": [
                            k for k in config.config_50.communication["vaglinje"].keys()
                        ]
                    }
                ),
                config.config_50,
            ),
            (
                "path",
                "50",
                "vaglinje",
                True,
                gpd.GeoDataFrame(
                    {
                        "objekttyp": [
                            k
                            for k in config.config_50.communication["vaglinje"].keys()
                            if k not in {"Motorväg"}
                        ]
                    }
                ),
                None,
            ),
        ],
    )
    @patch("lantmateriet.geometry.gpd.read_file")
    def test_unit_communication_init(
        self,
        mock_gpd_read_file,
        file_name,
        detail_level,
        layer,
        use_arrow,
        df,
        expected_result,
    ):
        """Unit test of Line __init__ method.

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
                communication = Line(file_name, detail_level, layer, use_arrow)
        else:
            communication = Line(file_name, detail_level, layer, use_arrow)
            mock_gpd_read_file.assert_called_with(
                file_name, layer=layer, use_arrow=use_arrow
            )
            assert communication.config == expected_result

    @patch("lantmateriet.communication.Line._process")
    @patch("lantmateriet.communication.Line.__init__", return_value=None)
    def test_unit_communication_process(
        self, mock_communication_init, mock_communication_process
    ):
        """Unit test of communication process method.

        Args:
            mock_communication_init: mock of Line __init__
            mock_communication_process: mock of Line _process
        """
        communication = Line("path")
        communication.item_type = "communication"
        communication.layer = "vaglinje"
        communication.dissolve = False

        communication.process()
        mock_communication_process.assert_called_once_with(
            "communication", "vaglinje", False, False, True
        )

    @patch("lantmateriet.communication.Line._save")
    @patch("lantmateriet.communication.Line.__init__", return_value=None)
    def test_unit_communication_save(
        self, mock_communication_init, mock_communication_save
    ):
        """Unit test of communication save method.

        Args:
            mock_communication_init: mock of Line __init__
            mock_communication_save: mock of Line _save
        """
        communication = Line("path")
        communication.item_type = "communication"
        communication.layer = "vaglinje"

        communication.save({}, "path")
        mock_communication_save.assert_called_once_with(
            "communication", "vaglinje", {}, "path"
        )
