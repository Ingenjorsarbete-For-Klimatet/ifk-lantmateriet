"""Administrative division borders module."""

import os

from lantmateriet.admin_border_types import (
    FeatureCollectionGeoJsonKommuner,
    FeatureCollectionGeoJsonLan,
    FeatureCollectionGeoJsonRike,
    FeatureGeoJsonLan,
    FeatureGeoJsonRike,
)
from owslib.ogcapi.features import Features

USER = os.environ["IFK_LANTMATERIET_USER"]
PASS = os.environ["IFK_LANTMATERIET_PASSWORD"]
BASE_URL = "https://api.lantmateriet.se/ogc-features/v1/administrativ-indelning"
BASIC_AUTH = (USER, PASS)
LIMIT = 1000
COUNTRY = "rike"
COUNTIES = "lan"
MUNICIPALITIES = "kommuner"


class AdminBorders:
    """Administrative divisions class.

    Targets Kommun, Län och Rike Direkt
    API: https://api.lantmateriet.se/ogc-features/v1/administrativ-indelning
    """

    def __init__(self, limit: int = LIMIT):
        """Initialise admin borders object.

        Args:
            limit: limit of API calls
        """
        self._features = Features(BASE_URL, auth=BASIC_AUTH)
        self._limit = limit

    @property
    def collections(self) -> list[str]:
        """Return available feature collections.

        Returns:
            feature collections
        """
        return self._features.feature_collections()

    @property
    def country(self) -> list[FeatureGeoJsonRike]:
        """Get country.

        Returns:
            country
        """
        raw_country = self._features.collection_items(COUNTRY, limit=self._limit)
        country = FeatureCollectionGeoJsonRike(**raw_country)
        return country.features

    @property
    def counties(self) -> list[FeatureGeoJsonLan]:
        """Get counties.

        Returns:
            counties
        """
        raw_counties = self._features.collection_items(COUNTIES, limit=self._limit)
        counties = FeatureCollectionGeoJsonLan(**raw_counties)
        return counties.features

    @property
    def municipalities(self) -> list[FeatureCollectionGeoJsonKommuner]:
        """Get municipalities.

        Returns:
            municipalities
        """
        raw_municipalities = self._features.collection_items(MUNICIPALITIES, limit=self._limit)
        municipalities = FeatureCollectionGeoJsonKommuner(**raw_municipalities)
        return municipalities.features
