"""Climate platform for Lambda Heatpumps."""
from __future__ import annotations

import logging
from typing import Any, final
from dataclasses import dataclass

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    HVACMode,
    HVACAction,
    ClimateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import LambdaHeatpumpCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class LambdaClimateEntityDescription(ClimateEntityDescription):
    """Describes Lambda climate entity."""
    
    register_temp: int
    register_setpoint: int
    register_mode: int | None = None
    register_setpoint_high: int = 70
    register_setpoint_low: int = 30
    factor: float = 0.1
    data_type: str = "int16"
    precision: float = 0.5
    force_heat_only: bool = False  # New field to enforce HEAT-only mode

CLIMATE_DESCRIPTIONS: tuple[LambdaClimateEntityDescription, ...] = (
    LambdaClimateEntityDescription(
        key="boiler_1_climate",
        name="Boiler 1",
        translation_key="boiler_climate",
        register_temp=2002,
        register_setpoint=2050,
        register_mode=None,  # Disable mode register for HEAT-only
        register_setpoint_high=70,
        register_setpoint_low=30,
        factor=0.1,
        force_heat_only=True  # Enable HEAT-only for this specific entity
    ),
    # Add more descriptions as needed
)

class LambdaHeatpumpClimate(CoordinatorEntity[LambdaHeatpumpCoordinator], ClimateEntity):
    """Representation of a Lambda Heatpump climate device."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]  # Default modes
    _enable_turn_on_off_backwards_compatibility = False

    entity_description: LambdaClimateEntityDescription

    def __init__(
        self,
        coordinator: LambdaHeatpumpCoordinator,
        config_entry: ConfigEntry,
        description: LambdaClimateEntityDescription,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator)
        self.entity_description = description
        self._config_entry = config_entry
        self._attr_device_info = device_info
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        
        # Override modes if force_heat_only is True
        if description.force_heat_only:
            self._attr_hvac_modes = [HVACMode.HEAT]
            self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        
        # Register required modbus registers
        coordinator.add_register(description.register_temp, description.data_type)
        coordinator.add_register(description.register_setpoint, description.data_type)
        if description.register_mode is not None:
            coordinator.add_register(description.register_mode, description.data_type)

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if (value := self.coordinator.data.get(f"register_{self.entity_description.register_temp}")) is not None:
            return round(value * self.entity_description.factor, 1)
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if (value := self.coordinator.data.get(f"register_{self.entity_description.register_setpoint}")) is not None:
            return round(value * self.entity_description.factor, 1)
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current hvac mode."""
        if self.entity_description.force_heat_only:
            return HVACMode.HEAT
            
        if self.entity_description.register_mode is None:
            return HVACMode.HEAT
            
        if (mode := self.coordinator.data.get(f"register_{self.entity_description.register_mode}")) is not None:
            return HVACMode.HEAT if mode else HVACMode.OFF
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation."""
        if self.hvac_mode == HVACMode.OFF and not self.entity_description.force_heat_only:
            return HVACAction.OFF
            
        if None in (current_temp := self.current_temperature, target_temp := self.target_temperature):
            return None
            
        return HVACAction.HEATING if current_temp < target_temp else HVACAction.IDLE

    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return self.entity_description.precision

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self.entity_description.register_setpoint_low

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self.entity_description.register_setpoint_high

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
            
        scaled_temp = int(temperature / self.entity_description.factor)
        await self.coordinator.async_write_register(self.entity_description.register_setpoint, scaled_temp)
        # await self.coordinator.async_write_register(
        #     self.entity_description.register_setpoint,
        #     scaled_temp,
        #     self.entity_description.data_type
        # )
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new hvac mode."""
        if self.entity_description.force_heat_only:
            _LOGGER.debug("HVAC mode change ignored for HEAT-only device")
            return
            
        if self.entity_description.register_mode is None:
            return
            
        value = 1 if hvac_mode == HVACMode.HEAT else 0
        await self.coordinator.async_write_register(
            self.entity_description.register_mode,
            value,
            self.entity_description.data_type
        )
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_available = self.coordinator.last_update_success
        super()._handle_coordinator_update()

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lambda heatpump climate entities from a config entry."""
    coordinator: LambdaHeatpumpCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    num_boilers = config_entry.data.get("amount_of_boilers", 1)
    model = config_entry.data.get("model", "Unknown Model")

    entities: list[LambdaHeatpumpClimate] = []
    
    for i in range(1, num_boilers + 1):
        device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_boiler_{i}")},
            name=f"Boiler {i}",
            manufacturer=MANUFACTURER,
            model=model,
            via_device=(DOMAIN, config_entry.entry_id),
        )

        # Find matching description
        for description in CLIMATE_DESCRIPTIONS:
            if description.key == f"boiler_{i}_climate":
                entities.append(
                    LambdaHeatpumpClimate(
                        coordinator=coordinator,
                        config_entry=config_entry,
                        description=description,
                        device_info=device_info,
                    )
                )
                break

    async_add_entities(entities)