from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from datetime import timedelta

from .electric_kiwi_api import ElectricKiwiAPI

import logging

from .const import (
    DOMAIN,
    NAME_COMPONENT_HOP_SENSOR,
    NAME_COMPONENT_AVERAGE_HOP_SENSOR
)

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME
)

SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup_entry(hass, config_entry, async_add_entities):
    electric_kiwi = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([HOPSensor(hass, electric_kiwi), AverageHourOfPowerSensor(hass, electric_kiwi)])

class HOPSensor(SensorEntity):

    _LOGGER = logging.getLogger(__name__)

    _hass = None
    _electric_kiwi = None

    def __init__(self, hass: HomeAssistant, electric_kiwi: ElectricKiwiAPI):
        self._hass = hass
        self._electric_kiwi = electric_kiwi

        self._attributes = {
            ATTR_ATTRIBUTION: "Electric Kiwi",
            ATTR_FRIENDLY_NAME: "Current Hour of Power",
        }

    @property
    def name(self) -> str:
        return NAME_COMPONENT_HOP_SENSOR

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._electric_kiwi.last_retrieved_hop

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def current_option(self) -> str:
        """Return the state of the entity."""

        return self._electric_kiwi.last_retrieved_hop

    async def async_update(self) -> None:
        """Retrieve latest state."""
        self._LOGGER.warning('Requesting update of hour of power')

        await self._electric_kiwi.async_get_hop_hour()

class AverageHourOfPowerSensor(SensorEntity):

    _LOGGER = logging.getLogger(__name__)

    _hass = None
    _electric_kiwi = None

    def __init__(self, hass: HomeAssistant, electric_kiwi: ElectricKiwiAPI):
        self._hass = hass
        self._electric_kiwi = electric_kiwi

        self._attributes = {
            ATTR_ATTRIBUTION: "Electric Kiwi",
            ATTR_FRIENDLY_NAME: "7 Day Average Hour of Power",
        }

    @property
    def name(self) -> str:
        return NAME_COMPONENT_AVERAGE_HOP_SENSOR

    @property
    def state(self):
        """Return the state of the sensor."""
        return str(self._electric_kiwi.last_average_hop_utilisation)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    async def async_update(self) -> None:
        """Retrieve latest state."""
        self._LOGGER.warning('Requesting update of last 7 days Hour of Power utilisation')

        await electric_kiwi_api.get_average_hop_utilisation_for_last(daysCount=7)