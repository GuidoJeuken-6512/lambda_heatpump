"""Initialization of Lambda Heatpumps integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.exceptions import ConfigEntryNotReady
from pymodbus.exceptions import ConnectionException

from .const import (
    DOMAIN,
    MANUFACTURER,
    CONF_MODBUS_HOST,
    CONF_MODBUS_PORT,
    CONF_SLAVE_ID,
    CONF_MODEL
)
from .coordinator import LambdaHeatpumpCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["climate", "sensor", "number"]

# Liste der erforderlichen Konfigurationseinträge
REQUIRED_KEYS = [CONF_MODBUS_HOST, CONF_MODBUS_PORT, CONF_SLAVE_ID, CONF_MODEL]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lambda Heatpumps from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Prüfe, ob alle erforderlichen Konfigurationsschlüssel vorhanden sind
    for key in REQUIRED_KEYS:
        if key not in entry.data:
            _LOGGER.error("Konfigurationsschlüssel '%s' fehlt im Config Entry %s.", key, entry.entry_id)
            raise ConfigEntryNotReady(f"Fehlender Konfigurationsschlüssel: {key}")

    coordinator = LambdaHeatpumpCoordinator(
        hass,
        entry.data[CONF_MODBUS_HOST],
        entry.data[CONF_MODBUS_PORT],
        entry.data[CONF_SLAVE_ID]
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConnectionException as ex:
        _LOGGER.error("Modbus-Verbindung fehlgeschlagen während des Setups: %s", ex)
        raise ConfigEntryNotReady from ex

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Gerätedaten im Device Registry eintragen
    registry = async_get_device_registry(hass)
    registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer=MANUFACTURER,
        name=f"Lambda {entry.data[CONF_MODEL]}",
        model=entry.data[CONF_MODEL]
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Update-Listener hinzufügen, um bei Änderungen im Config Flow die neuen entry.data zu laden
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options: Reload the config entry so that new data is applied."""
    _LOGGER.debug("Konfigurationsänderungen erkannt für %s, lade die Config Entry neu.", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)
