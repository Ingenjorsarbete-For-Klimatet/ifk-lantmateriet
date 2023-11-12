"""Config module."""


class BaseConfig:
    """Base config class."""

    espg_3006: str = "EPSG:3006"
    epsg_4326: str = "EPSG:4326"
    ground_sweden: str = "00_sverige.geojson"

    border_land: str = "Riksgräns"
    border_sea: str = "Sjöterritoriets gräns i havet"
    border_county: str = "Länsgräns"
    border_municipality: str = "Kommungräns"

    def __getitem__(self, key):
        """Get item.

        Args:
            key: key

        Returns:
            value
        """
        return self.__getattribute__(key)


class Config1M(BaseConfig):
    """Topography 1M config class."""

    ground: dict[str, str] = {
        "Vattenyta": "01_vattenyta.geojson",
        "Glaciär": "05_glaciar.geojson",
        "Kalfjäll": "08_kalfjall.geojson",
        "Skog": "02_skog.geojson",
        "Öppen mark": "15_oppen_mark.geojson",
        "Bebyggelse": "06_bebygelse.geojson",
        "Hav": "16_hav.geojson",
        "Ej karterat område": "17_ej_kartlagt.geojson",
    }
    building: dict[str, str] = {}
    exclude = {"Hav", "Ej karterat område"}

    ground_water = {
        "Hav",
        "Vattenyta",
    }

    exteriorise = {"Skog"}


class Config50(BaseConfig):
    """Config class."""

    ground: dict[str, str] = {
        "Anlagt vatten": "01_anlagt_vatten.geojson",
        "Vattendragsyta": "02_vattendragsyta.geojson",
        "Sjö": "03_sjo.geojson",
        "Glaciär": "04_glaciar.geojson",
        "Kalfjäll": "05_kalfjall.geojson",
        "Fjällbjörkskog": "06_fjallbjorkskog.geojson",
        "Barr- och blandskog": "07_barr_blandskog.geojson",
        "Lövskog": "08_lovskog.geojson",
        "Åker": "09_aker.geojson",
        "Fruktodling": "10_fruktodling.geojson",
        "Öppen mark": "11_oppen_mark.geojson",
        "Hög bebyggelse": "12_hog_bebygelse.geojson",
        "Låg bebyggelse": "13_lag_bebygelse.geojson",
        "Sluten bebyggelse": "14_sluten_bebygelse.geojson",
        "Industri- och handelsbebyggelse": "15_industri_handel.geojson",
        "Hav": "16_hav.geojson",
        "Ej karterat område": "17_ej_kartlagt.geojson",
    }
    building: dict[str, str] = {
        "Bostad": "01_bostad.geojson",
        "Industri": "02_industri.geojson",
        "Samhällsfunktion": "03_samhallsfunktion.geojson",
        "Verksamhet": "04_verksamhet.geojson",
        "Ekonomibyggnad": "05_ekonomibyggnad.geojson",
        "Komplementbyggnad": "06_komplementbyggnad.geojson",
        "Övrig byggnad": "07_ovrig.geojson",
    }
    exclude = {"Hav", "Ej karterat område"}

    ground_water = {
        "Anlagt vatten",
        "Sjö",
        "Vattendragsyta",
        "Hav",
    }

    exteriorise = {"Barr- och blandskog"}


config_1m = Config1M()
config_50 = Config50()
