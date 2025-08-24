"""Config flow for Smart Updater."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN


class SmartUpdaterOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Smart Updater."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "auto_update_time",
                        default=self.config_entry.options.get("auto_update_time", "03:00:00"),
                    ): selector.TimeSelector(),
                    vol.Optional(
                        "auto_update_entities",
                        default=self.config_entry.options.get("auto_update_entities", []),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="update",
                            multiple=True,
                        ),
                    ),
                    vol.Optional(
                        "auto_restart",
                        default=self.config_entry.options.get("auto_restart", False),
                    ): bool,
                }
            ),
        )


class SmartUpdaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Updater."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SmartUpdaterOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="Smart Updater", data={})
