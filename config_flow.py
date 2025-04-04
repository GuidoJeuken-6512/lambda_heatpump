"""Config flow for Lambda Heatpumps integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_MODBUS_HOST,
    CONF_MODBUS_PORT,
    CONF_SLAVE_ID,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    CONF_MODEL,
    CONF_AMOUNT_OF_HEATPUMPS,
    CONF_AMOUNT_OF_BOILERS,
    CONF_AMOUNT_OF_BUFFERS,
    CONF_AMOUNT_OF_SOLAR,
    CONF_AMOUNT_OF_HEAT_CIRCUITS,
)

_LOGGER = logging.getLogger(__name__)


class LambdaHeatpumpsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lambda Heatpumps."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._test_modbus_connection(
                    user_input[CONF_MODBUS_HOST],
                    user_input[CONF_MODBUS_PORT],
                    user_input[CONF_SLAVE_ID],
                )

                unique_id = f"{user_input[CONF_MODBUS_HOST]}:{user_input[CONF_MODBUS_PORT]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Lambda Wärmepumpe ({user_input[CONF_MODEL]})",
                    data=user_input,
                )

            except ConnectionException:
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_slave_id"
            except Exception as ex:
                _LOGGER.exception("Unexpected exception: %s", ex)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_config_schema(),
            errors=errors,
        )

    async def _test_modbus_connection(
        self, host: str, port: int, slave_id: int
    ) -> None:
        """Test the Modbus connection."""
        await self.hass.async_add_executor_job(
            self._test_connection, host, port, slave_id
        )

    @staticmethod
    def _test_connection(host: str, port: int, slave_id: int) -> None:
        """Test the connection to the Modbus device."""
        client = ModbusTcpClient(host=host, port=port)
        try:
            if not client.connect():
                raise ConnectionException("Cannot connect to Modbus client")
            result = client.read_holding_registers(100, count=1, slave=slave_id)
            if result.isError():
                raise ValueError("Invalid slave ID")
        finally:
            client.close()

    @staticmethod
    def _get_config_schema() -> vol.Schema:
        """Return the configuration schema."""
        model_options = ["EU08L", "EU10L", "EU13L", "EU15L", "EU20L"]
        return vol.Schema(
            {
                vol.Required(CONF_MODBUS_HOST, default="192.168.178.125"): str,
                vol.Required(CONF_MODBUS_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
                vol.Required(CONF_MODEL): vol.In(model_options),
                vol.Required(CONF_AMOUNT_OF_HEATPUMPS, default=1): int,
                vol.Required(CONF_AMOUNT_OF_BOILERS, default=1): int,
                vol.Required(CONF_AMOUNT_OF_BUFFERS, default=0): int,
                vol.Required(CONF_AMOUNT_OF_SOLAR, default=0): int,
                vol.Required(CONF_AMOUNT_OF_HEAT_CIRCUITS, default=1): int,
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> LambdaHeatpumpsOptionsFlow:
        """Get the options flow for this handler."""
        return LambdaHeatpumpsOptionsFlow(config_entry)


class LambdaHeatpumpsOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Lambda Heatpumps."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        _LOGGER.debug("Options flow initialized")

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        _LOGGER.debug("Options flow initiated with input: %s", user_input)

        if user_input is not None:
            _LOGGER.debug("Processing user input for options update")

            if (
                user_input[CONF_MODBUS_HOST] != self._config_entry.data[CONF_MODBUS_HOST]
                or user_input[CONF_SLAVE_ID] != self._config_entry.data[CONF_SLAVE_ID]
            ):
                try:
                    await self._test_modbus_connection(
                        user_input[CONF_MODBUS_HOST],
                        self._config_entry.data[CONF_MODBUS_PORT],
                        user_input[CONF_SLAVE_ID],
                    )
                except ConnectionException:
                    return self.async_abort(reason="cannot_connect")
                except ValueError:
                    return self.async_abort(reason="invalid_slave_id")

                new_data = {**self._config_entry.data, **user_input}
                self.hass.config_entries.async_update_entry(
                    self._config_entry, data=new_data
                )
                return self.async_abort(reason="restart_required")

            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init", data_schema=self._get_options_schema()
        )

    async def _test_modbus_connection(
        self, host: str, port: int, slave_id: int
    ) -> None:
        """Test the Modbus connection."""
        await self.hass.async_add_executor_job(
            self._test_connection, host, port, slave_id
        )

    @staticmethod
    def _test_connection(host: str, port: int, slave_id: int) -> None:
        """Test the connection to the Modbus device."""
        client = ModbusTcpClient(host=host, port=port)
        try:
            if not client.connect():
                raise ConnectionException("Cannot connect to Modbus client")
            result = client.read_holding_registers(100, count=1, slave=slave_id)
            if result.isError():
                raise ValueError("Invalid slave ID")
        finally:
            client.close()

    def _get_options_schema(self) -> vol.Schema:
        """Return the options schema."""
        return vol.Schema(
            {
                vol.Required(
                    CONF_MODBUS_HOST,
                    default=self._config_entry.data[CONF_MODBUS_HOST],
                ): str,
                vol.Required(
                    CONF_SLAVE_ID,
                    default=self._config_entry.data[CONF_SLAVE_ID],
                ): int,
                vol.Required(
                    CONF_AMOUNT_OF_HEATPUMPS,
                    default=self._config_entry.options.get(CONF_AMOUNT_OF_HEATPUMPS, 1),
                ): int,
                vol.Required(
                    CONF_AMOUNT_OF_BOILERS,
                    default=self._config_entry.options.get(CONF_AMOUNT_OF_BOILERS, 1),
                ): int,
                vol.Required(
                    CONF_AMOUNT_OF_BUFFERS,
                    default=self._config_entry.options.get(CONF_AMOUNT_OF_BUFFERS, 1),
                ): int,
                vol.Required(
                    CONF_AMOUNT_OF_SOLAR,
                    default=self._config_entry.options.get(CONF_AMOUNT_OF_SOLAR, 0),
                ): int,
                vol.Required(
                    CONF_AMOUNT_OF_HEAT_CIRCUITS,
                    default=self._config_entry.options.get(CONF_AMOUNT_OF_HEAT_CIRCUITS, 1),
                ): int,
            }
        )
