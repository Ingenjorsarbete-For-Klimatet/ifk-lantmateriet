"""Administrative division borders integration tests."""

from lantmateriet.admin_borders import AdminBorders


class TestAdminBorder:
    """Integration tests for AdminBorder."""

    def test_integration_admin_borders_collections(self):
        """Integration test for AdminBorders collections."""
        client = AdminBorders()
        assert len(client.collections) >= 3

    def test_integration_admin_borders_country(self):
        """Integration test for AdminBorders country."""
        client = AdminBorders(limit=1)
        assert len(client.country) >= 1

    def test_integration_admin_borders_counties(self):
        """Integration test for AdminBorders counties."""
        client = AdminBorders(limit=1)
        assert len(client.counties) >= 1

    def test_integration_admin_borders_municipalities(self):
        """Integration test for AdminBorders municipalities."""
        client = AdminBorders(limit=1)
        assert len(client.municipalities) >= 1
