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
    force_heat_only: bool = False
    device_type: str = "boiler"  # "boiler", "heatpump", "buffer", etc.
    device_index: int = 1  # Index des Geräts (1-based)
    supports_cooling: bool = False
    supports_auto: bool = False
    supports_fan_only: bool = False
    supports_dry: bool = False
    min_temp: float = 5.0
    max_temp: float = 35.0
    temp_step: float = 0.5

CLIMATE_DESCRIPTIONS: tuple[LambdaClimateEntityDescription, ...] = (
    # Boiler 1
    LambdaClimateEntityDescription(
        key="boiler_1_climate",
        name="Boiler 1",
        translation_key="boiler_climate",
        register_temp=2002,
        register_setpoint=2050,
        register_mode=None,
        register_setpoint_high=70,
        register_setpoint_low=30,
        factor=0.1,
        data_type="int16",
        precision=0.5,
        force_heat_only=True,
        device_type="boiler",
        device_index=1,
        supports_cooling=False,
        supports_auto=False,
        supports_fan_only=False,
        supports_dry=False,
        min_temp=25.0,
        max_temp=65.0,
        temp_step=0.5,
    ),
    # Heatpump 1
    LambdaClimateEntityDescription(
        key="heatpump_1_climate",
        name="Heatpump 1",
        translation_key="heatpump_climate",
        register_temp=5004,  # Flowline Temperature
        register_setpoint=5051,  # Flowline Setpoint
        #register_mode=1003,  # Operating State
        register_setpoint_high=60,
        register_setpoint_low=20,
        factor=0.1,
        data_type="int16",
        force_heat_only=True,
        device_type="heatpump",
        device_index=1,
        supports_cooling=False,
        supports_auto=False,
        supports_fan_only=False,
        supports_dry=False,
        min_temp=15.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
    # Buffer 1
    LambdaClimateEntityDescription(
        key="buffer_1_climate",
        name="Buffer 1",
        translation_key="buffer_climate",
        register_temp=3002,  # Buffer Temperature
        register_setpoint=3050,  # Buffer Setpoint
        register_mode=None,
        register_setpoint_high=80,
        register_setpoint_low=30,
        factor=0.1,
        force_heat_only=True,
        device_type="buffer",
        device_index=1,
        supports_cooling=False,
        supports_auto=False,
        supports_fan_only=False,
        supports_dry=False,
        min_temp=5.0,
        max_temp=35.0,
        temp_step=0.5,
    ),
)

class LambdaHeatpumpClimate(CoordinatorEntity[LambdaHeatpumpCoordinator], ClimateEntity):
    """Representation of a Lambda Heatpump climate device."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
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
        
        # Set supported features based on device capabilities
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        if description.register_mode is not None:
            self._attr_supported_features |= ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        
        # Set HVAC modes based on device capabilities
        self._attr_hvac_modes = [HVACMode.HEAT]
        if description.supports_cooling:
            self._attr_hvac_modes.append(HVACMode.COOL)
        if description.supports_auto:
            self._attr_hvac_modes.append(HVACMode.AUTO)
        if description.supports_fan_only:
            self._attr_hvac_modes.append(HVACMode.FAN_ONLY)
        if description.supports_dry:
            self._attr_hvac_modes.append(HVACMode.DRY)
        if not description.force_heat_only:
            self._attr_hvac_modes.append(HVACMode.OFF)
        
        # Register required modbus registers
        _LOGGER.debug(f"Registering registers for {description.name}:")
        _LOGGER.debug(f"  - Temperature register: {description.register_temp} ({description.data_type})")
        coordinator.add_register(description.register_temp, description.data_type)
        
        _LOGGER.debug(f"  - Setpoint register: {description.register_setpoint} ({description.data_type})")
        coordinator.add_register(description.register_setpoint, description.data_type)
        
        if description.register_mode is not None:
            _LOGGER.debug(f"  - Mode register: {description.register_mode} ({description.data_type})")
            coordinator.add_register(description.register_mode, description.data_type)
            
        # Debug-Ausgabe der registrierten Register
        _LOGGER.debug(f"Registered registers for {description.name}:")
        for register, reg_type in coordinator._registers_to_read.items():
            _LOGGER.debug(f"  - Register {register} ({reg_type})")

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        try:
            register_key = str(self.entity_description.register_temp)
            if register_key not in self.coordinator.data:
                _LOGGER.debug(f"Temperature register {self.entity_description.register_temp} not found in coordinator data for {self.name}")
                return None
                
            value = self.coordinator.data[register_key]
            if value is None:
                _LOGGER.debug(f"Temperature register {self.entity_description.register_temp} has no value for {self.name}")
                return None
                
            return float(value) * self.entity_description.factor
            
        except Exception as e:
            _LOGGER.error(f"Error getting current temperature for {self.name}: {e}")
            return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if (value := self.coordinator.data.get(str(self.entity_description.register_setpoint))) is not None:
            return round(value * self.entity_description.factor, 1)
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current hvac mode."""
        if self.entity_description.force_heat_only:
            return HVACMode.HEAT
            
        if self.entity_description.register_mode is None:
            return HVACMode.HEAT
            
        if (mode := self.coordinator.data.get(str(self.entity_description.register_mode))) is not None:
            if self.entity_description.supports_cooling:
                return HVACMode.COOL if mode == 2 else HVACMode.HEAT
            return HVACMode.HEAT if mode else HVACMode.OFF
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation."""
        if self.hvac_mode == HVACMode.OFF and not self.entity_description.force_heat_only:
            return HVACAction.OFF
            
        if None in (current_temp := self.current_temperature, target_temp := self.target_temperature):
            return None
            
        if self.hvac_mode == HVACMode.COOL:
            return HVACAction.COOLING if current_temp > target_temp else HVACAction.IDLE
        return HVACAction.HEATING if current_temp < target_temp else HVACAction.IDLE

    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return self.entity_description.temp_step

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self.entity_description.min_temp

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self.entity_description.max_temp

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
            
        scaled_temp = int(temperature / self.entity_description.factor)
        await self.coordinator.async_write_register(self.entity_description.register_setpoint, scaled_temp)
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new hvac mode."""
        if self.entity_description.force_heat_only:
            _LOGGER.debug("HVAC mode change ignored for HEAT-only device")
            return
            
        if self.entity_description.register_mode is None:
            return
            
        if hvac_mode == HVACMode.OFF:
            value = 0
        elif hvac_mode == HVACMode.COOL and self.entity_description.supports_cooling:
            value = 2
        else:
            value = 1
            
        await self.coordinator.async_write_register(
            self.entity_description.register_mode,
            value,
            self.entity_description.data_type
        )
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            self._attr_available = self.coordinator.last_update_success
            if not self._attr_available:
                _LOGGER.warning(f"{self.name} is not available")
                return
                
            # Überprüfe, ob die erforderlichen Register vorhanden sind
            temp_key = str(self.entity_description.register_temp)
            setpoint_key = str(self.entity_description.register_setpoint)
            
            if temp_key not in self.coordinator.data:
                _LOGGER.debug(f"Temperature register {self.entity_description.register_temp} not found in coordinator data, waiting for next update")
                return
                
            if setpoint_key not in self.coordinator.data:
                _LOGGER.debug(f"Setpoint register {self.entity_description.register_setpoint} not found in coordinator data, waiting for next update")
                return
                
            _LOGGER.debug(f"Updating {self.name} with new data")
            super()._handle_coordinator_update()
            
        except Exception as e:
            _LOGGER.error(f"Error updating {self.name}: {e}")
            self._attr_available = False

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lambda heatpump climate entities from a config entry."""
    coordinator: LambdaHeatpumpCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    model = config_entry.data.get("model", "Unknown Model")
    
    # Get device counts from config
    num_boilers = config_entry.data.get("amount_of_boilers", 1)
    num_heatpumps = config_entry.data.get("amount_of_heatpumps", 1)
    num_buffers = config_entry.data.get("amount_of_buffers", 1)

    entities: list[LambdaHeatpumpClimate] = []
    
    # Create entities for each device type
    for device_type, count in [
        ("boiler", num_boilers),
        ("heatpump", num_heatpumps),
        ("buffer", num_buffers)
    ]:
        for i in range(1, count + 1):
            device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{config_entry.entry_id}_{device_type}_{i}")},
                name=f"{device_type.capitalize()} {i}",
                manufacturer=MANUFACTURER,
                model=model,
                via_device=(DOMAIN, config_entry.entry_id),
            )

            # Find matching description
            for description in CLIMATE_DESCRIPTIONS:
                if description.device_type == device_type and description.device_index == i:
                    _LOGGER.debug(f"Creating {device_type} {i} with registers: temp={description.register_temp}, setpoint={description.register_setpoint}")
                    
                    # Register required modbus registers
                    coordinator.add_register(description.register_temp, description.data_type)
                    coordinator.add_register(description.register_setpoint, description.data_type)
                    if description.register_mode is not None:
                        coordinator.add_register(description.register_mode, description.data_type)
                        
                    # Debug-Ausgabe der registrierten Register
                    _LOGGER.debug(f"Registered registers for {device_type} {i}:")
                    _LOGGER.debug(f"  - Temperature: {description.register_temp} ({description.data_type})")
                    _LOGGER.debug(f"  - Setpoint: {description.register_setpoint} ({description.data_type})")
                    if description.register_mode is not None:
                        _LOGGER.debug(f"  - Mode: {description.register_mode} ({description.data_type})")
                        
                    entities.append(
                        LambdaHeatpumpClimate(
                            coordinator=coordinator,
                            config_entry=config_entry,
                            description=description,
                            device_info=device_info,
                        )
                    )
                    break

    async_add_entities(entities, update_before_add=True)