"""Polygon unit tests."""

from unittest.mock import patch

from lantmateriet.polygon import Polygon


class TestUnitPolygon:
    """Unit tests of Polygon."""

    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_polygon_init(self, mock_geometry):
        """Unit test of Polygon __init__ method."""
        polygon = Polygon("path", "50", "layer", "name", "field")
        assert polygon.dissolve is True
        mock_geometry.assert_called_once()

    @patch("lantmateriet.geometry.Geometry._process")
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_polygon_process(self, mock_geometry, mock_geometry_process):
        """Unit test of Polygon process method."""
        polygon = Polygon("path", "50", "layer", "name", "field")
        polygon.process(False)
        mock_geometry_process.assert_called_once()

    @patch("lantmateriet.geometry.Geometry._save")
    @patch("lantmateriet.geometry.Geometry.__init__")
    def test_unit_polygon_save(self, mock_geometry, mock_geometry_save):
        """Unit test of Polygon save method."""
        polygon = Polygon("path", "50", "layer", "name", "field")
        polygon.save("path", "file")
        mock_geometry_save.assert_called_once()
