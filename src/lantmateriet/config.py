"""Config module.

Configuration taken from

- 1M: https://www.lantmateriet.se/globalassets/geodata/geodataprodukter/pb-topografi-1m-nedladdning-vektor.pdf
- 50: https://www.lantmateriet.se/globalassets/geodata/geodataprodukter/pb-topografi-50-nedladdning-vektor.pdf
"""


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

    ground: dict[str, dict[str, str]] = {
        "mark": {
            "Vattenyta": "01_vattenyta.geojson",
            "Glaciär": "05_glaciar.geojson",
            "Kalfjäll": "08_kalfjall.geojson",
            "Skog": "02_skog.geojson",
            "Öppen mark": "15_oppen_mark.geojson",
            "Bebyggelse": "06_bebygelse.geojson",
            "Hav": "16_hav.geojson",
            "Ej karterat område": "17_ej_kartlagt.geojson",
        },
        "markkantlinje": {},
        "sankmark": {},
    }
    construction: dict[str, dict[str, str]] = {"byggnadspunkt": {}}
    communication: dict[str, dict[str, str]] = {
        "vaglinje": {
            "Motorväg": "01_motorvag.geojson",
            "Motortrafikled": "02_motortrafikled.geojson",
            "Landsväg": "03_landsvag.geojson",
            "Landsväg liten": "04_landsvag_liten.geojson",
            "Småväg": "05_smavag.geojson",
        },
        "farjeled": {"Färjeled": "01_farjeled.geojson"},
        "ovrig_vag": {"Vandringsled": "01_vandringsled.geojson"},
        "ralstrafik": {"Järnväg": "01_jarnvag.geojson"},
    }

    exclude = {"Hav", "Ej karterat område"}
    exteriorise = {"Skog"}
    ground_water = {
        "Hav",
        "Vattenyta",
    }


class Config50(BaseConfig):
    """Config class."""

    ground: dict[str, dict[str, str]] = {
        "mark": {
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
        },
        "markkantlinje": {},
        "sankmark": {},
        "markframkomlighet": {},
    }
    construction: dict[str, dict[str, str]] = {
        "byggnad": {
            "Bostad": "01_bostad.geojson",
            "Industri": "02_industri.geojson",
            "Samhällsfunktion": "03_samhallsfunktion.geojson",
            "Verksamhet": "04_verksamhet.geojson",
            "Ekonomibyggnad": "05_ekonomibyggnad.geojson",
            "Komplementbyggnad": "06_komplementbyggnad.geojson",
            "Övrig byggnad": "07_ovrig.geojson",
        },
        "byggnadsanlaggningslinje": {},
        "byggnadsanlaggningspunkt": {},
        "byggnadspunkt": {},
    }
    communication: dict[str, dict[str, str]] = {
        "vaglinje": {
            "Motorväg": "01_motorvag.geojson",
            "Motortrafikled": "02_motortrafikled.geojson",
            "Mötesfri väg": "03_motesfri_vag.geojson",
            "Landsväg": "04_landsvag.geojson",
            "Landsväg liten": "05_landsvag_liten.geojson",
            "Småväg": "06_smavag.geojson",
            "Småväg enkel standard": "07_smavag_enkel_standard.geojson",
            "Övergripande länk": "08_overgripande_lank.geojson",
            "Huvudgata": "09_huvudgata.geojson",
            "Lokalgata stor": "10_lokalgata_stor.geojson",
            "Lokalgata liten": "11_lokalgata_liten.geojson",
        },
        "vagpunkt": {},
        "farjeled": {"Färjeled": "01_farjeled.geojson"},
        "ovrig_vag": {
            "Parkväg": "01_parkvag.geojson",
            "Cykelväg": "02_cykelvag.geojson",
            "Gångstig": "03_gangstig.geojson",
            "Elljusspår": "04_elljusspar.geojson",
            "Traktorväg": "05_traktorvag.geojson",
            "Vandringsled": "06_vandringsled.geojson",
            "Vandrings- och vinterled": "07_vandrings_vinterled.geojson",
            "Vinterled": "08_vinterled.geojson",
        },
        "transportled_fjall": {
            "Lämplig färdväg": "01_lamplig_fardvag.geojson",
            "Rennäringsled": "02_rennaringsled.geojson",
            "Fångstarm till led": "03_fangstarm_till_led.geojson",
            "Roddled": "04_roddled.geojson",
            "Svårorienterad gångstig": "05_svarorienterad_gangstig.geojson",
            "Skidspår": "06_skidspar.geojson",
            "Båtdrag": "07_batdrag.geojson",
            "Trafikerad båtled": "08_trafikerad_batled.geojson",
        },
        "ledintressepunkt_fjall": {},
        "ralstrafik": {
            "Järnväg": "01_jarnvag.geojson",
            "Museijärnväg": "02_museijarnvag.geojson",
        },
        "ralstrafikstation": {},
    }

    exclude = {"Hav", "Ej karterat område"}
    exteriorise = {"Barr- och blandskog"}
    ground_water = {
        "Anlagt vatten",
        "Sjö",
        "Vattendragsyta",
        "Hav",
    }


config_1m = Config1M()
config_50 = Config50()
