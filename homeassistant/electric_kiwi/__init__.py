"""The Electric Kiwi integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .electric_kiwi_api import ElectricKiwiAPI
from .electric_kiwi_api_service import ElectricKiwiAPIService

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
)

from .const import (
    DOMAIN,
    CONF_AUTH_OBJ
)

import logging

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS = ["select", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Electric Kiwi API from a config entry."""

    api_service = ElectricKiwiAPIService(hass, entry)
    electric_kiwi_api = ElectricKiwiAPI(api_service)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = electric_kiwi_api

    # Grab the current HOP & HOP utilisation values
    await electric_kiwi_api.async_get_hop_hour()
    await electric_kiwi_api.get_average_hop_utilisation_for_last(daysCount=7)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[CONF_DOMAIN].pop(entry.entry_id)

    return unload_ok
