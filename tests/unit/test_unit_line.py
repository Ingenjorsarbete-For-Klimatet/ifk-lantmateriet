"""Line unit tests."""

from unittest.mock import patch

from lantmateriet.line import Line


class TestUnitLine:
    """Unit tests of Line."""

    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_line_init(self, mock_geometry):
        """Unit test of Line __init__ method."""
        line = Line("path", "50", "layer", "name", "field")
        assert line.dissolve is False
        mock_geometry.assert_called_once()

    @patch("lantmateriet.geometry.Geometry._process")
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_line_process(self, mock_geometry, mock_geometry_process):
        """Unit test of Line process method."""
        line = Line("path", "50", "layer", "name", "field")
        line.process(False)
        mock_geometry_process.assert_called_once()

    @patch("lantmateriet.geometry.Geometry._save")
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_line_save(self, mock_geometry, mock_geometry_save):
        """Unit test of Line save method."""
        line = Line("path", "50", "layer", "name", "field")
        line.save("path", "file")
        mock_geometry_save.assert_called_once()
