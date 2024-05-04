"""Point unit tests."""

from unittest.mock import patch

from lantmateriet.point import Point


class TestUnitPoint:
    """Unit tests of Point."""

    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_point_init(self, mock_geometry):
        """Unit test of Point __init__ method."""
        point = Point("path", "50", "layer", "name", "field")
        assert point.dissolve is False
        mock_geometry.assert_called_once()

    @patch("lantmateriet.geometry.Geometry._process")
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_point_process(self, mock_geometry, mock_geometry_process):
        """Unit test of Point process method."""
        point = Point("path", "50", "layer", "name", "field")
        point.process()
        mock_geometry_process.assert_called_once()

    @patch("lantmateriet.geometry.Geometry._save")
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_point_save(self, mock_geometry, mock_geometry_save):
        """Unit test of Point save method."""
        point = Point("path", "50", "layer", "name", "field")
        point.save("path", "file")
        mock_geometry_save.assert_called_once()
