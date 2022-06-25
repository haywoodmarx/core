from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from datetime import timedelta
from .electric_kiwi_api import ElectricKiwiAPI

import logging

from .const import (
    DOMAIN,
    CONF_TOKEN,
    NAME_COMPONENT_HOP_SELECT
)

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
)

SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup_entry(hass, config_entry, async_add_entities):
    electric_kiwi = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([HOPSelect(hass, electric_kiwi)])

class HOPSelect(SelectEntity):

    _LOGGER = logging.getLogger(__name__)

    _hass = None
    _electric_kiwi = None

    def __init__(self, hass: HomeAssistant, electric_kiwi: ElectricKiwiAPI):
        self._hass = hass
        self._electric_kiwi = electric_kiwi

    @property
    def name(self) -> str:
        return NAME_COMPONENT_HOP_SELECT

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""

        return self._electric_kiwi.all_hop

    @property
    def current_option(self) -> str:
        """Return the state of the entity."""

        return self._electric_kiwi.last_retrieved_hop

    async def async_update(self) -> None:
        """Retrieve latest state."""
        self._LOGGER.warning('Requesting update of hour of power')

        await self._electric_kiwi.async_get_hop_hour()

    async def async_select_option(self, option: str) -> None:
        """Home Assistant made a new selection"""
        self._LOGGER.warning('User selected new hour of power: ' + option)

        await self._electric_kiwi.async_set_hop_hour(option)