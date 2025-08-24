"""Sensor platform for Smart Updater."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities([SmartUpdaterSensor(hass)])


class SmartUpdaterSensor(SensorEntity):
    """Representation of a Smart Updater sensor."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._attr_name = "Smart Updater"
        self._attr_unique_id = f"{DOMAIN}_updates"
        self._attr_icon = "mdi:update"
        self._state = 0
        self._attributes = {"updates": []}

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        hacs_updates = []
        ha_update = None
        registry = er.async_get(self.hass)

        for entity in registry.entities.values():
            if entity.platform != "hacs" or entity.domain != "update":
                continue

            state = self.hass.states.get(entity.entity_id)
            if not state:
                continue

            installed_version = state.attributes.get("installed_version")
            latest_version = state.state

            if latest_version and latest_version != "off" and latest_version != installed_version:
                hacs_updates.append(
                    {
                        "name": state.name,
                        "entity_id": state.entity_id,
                        "installed_version": installed_version,
                        "latest_version": latest_version,
                    }
                )

        # Check for Home Assistant Core update
        ha_state = self.hass.states.get("update.home_assistant_core_update")
        if ha_state:
            installed_version = ha_state.attributes.get("installed_version")
            latest_version = ha_state.state
            if latest_version and latest_version != "off" and latest_version != installed_version:
                ha_update = {
                    "name": "Home Assistant Core",
                    "entity_id": ha_state.entity_id,
                    "installed_version": installed_version,
                    "latest_version": latest_version,
                }

        updates_list = hacs_updates
        if ha_update:
            updates_list.append(ha_update)

        self._state = len(updates_list)
        self._attributes["updates"] = updates_list
