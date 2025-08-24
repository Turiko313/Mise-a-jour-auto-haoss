"""The Smart Updater integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_time_change

from .const import DOMAIN

PLATFORMS = ["sensor"]
SERVICE_UPDATE_SELECTED = "update_selected"
SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
    }
)


async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Updater from a config entry."""
    hass.http.register_static_path(
        f"/hacsfiles/{DOMAIN}/smart-updater-card.js",
        hass.config.path(f"custom_components/{DOMAIN}/www/smart-updater-card.js"),
    )

    if "lovelace" in hass.data:
        lovelace = hass.data["lovelace"]
        if hasattr(lovelace, "resources"):
            resources = lovelace.resources
            url = f"/hacsfiles/{DOMAIN}/smart-updater-card.js"
            if not any(res["url"] == url for res in resources.async_items()):
                await resources.async_create_item(
                    {
                        "res_type": "module",
                        "url": url,
                    }
                )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_update_selected(call):
        """Handle the update_selected service call."""
        entity_ids = call.data["entity_id"]
        for entity_id in entity_ids:
            await hass.services.async_call(
                "update",
                "install",
                {"entity_id": entity_id},
                blocking=True,
            )

    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_SELECTED, handle_update_selected, schema=SERVICE_SCHEMA
    )

    unsub_options_update_listener = entry.add_update_listener(options_update_listener)

    async def auto_update(now):
        """Handle the automatic update."""
        auto_update_entities = entry.options.get("auto_update_entities", [])
        if not auto_update_entities:
            return

        # We only want to update the ones that actually have an update available.
        sensor_state = hass.states.get(f"sensor.{DOMAIN}_updates")
        if not sensor_state:
            return

        available_updates = [
            update["entity_id"] for update in sensor_state.attributes.get("updates", [])
        ]

        entities_to_update = [
            entity_id for entity_id in auto_update_entities if entity_id in available_updates
        ]

        if not entities_to_update:
            return

        await hass.services.async_call(
            DOMAIN,
            SERVICE_UPDATE_SELECTED,
            {"entity_id": entities_to_update},
            blocking=True,
        )

    time_str = entry.options.get("auto_update_time", "03:00:00")
    hour, minute, second = map(int, time_str.split(":"))

    unsub_time_tracker = async_track_time_change(
        hass, auto_update, hour=hour, minute=minute, second=second
    )

    entry.async_on_unload(
        lambda: hass.services.async_remove(DOMAIN, SERVICE_UPDATE_SELECTED)
    )
    entry.async_on_unload(unsub_options_update_listener)
    entry.async_on_unload(unsub_time_tracker)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
