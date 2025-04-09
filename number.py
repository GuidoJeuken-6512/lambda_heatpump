from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Final
from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)




from .const import DOMAIN, MANUFACTURER
from .coordinator import LambdaHeatpumpCoordinator

@dataclass(kw_only=True)
class LambdaNumberEntityDescription(NumberEntityDescription):
    """Beschreibung eines Lambda Heatpump Number."""
    register: int
    data_type: str = "int16"
    factor: float = 1.0

_LOGGER = logging.getLogger(__name__)

NUMBER_DESCRIPTIONS: Final[tuple[LambdaNumberEntityDescription, ...]] = (
    LambdaNumberEntityDescription(
        key="boiler_1_setting_for_maximum_boiler_temperature",
        name="Setting for Maximum Boiler Temperature",
        register=2050,
        data_type="int16",
        factor=0.1,
        native_min_value=25.0,
        native_max_value=65.0,
        native_step=0.5,
        native_unit_of_measurement="°C",
    ),
    LambdaNumberEntityDescription(
        key="buffer_1_setting_for_maximum_buffer_temperature",
        name="Setting for Maximum Buffer Temperature",
        register=3050,
        data_type="int16",
        factor=0.1,
        native_min_value=25.0,
        native_max_value=90.0,
        native_step=0.5,
        native_unit_of_measurement="°C",
    ),
    LambdaNumberEntityDescription(
        key="solar_1_setting_for_maximum_buffer_temperature",
        name="Setting for Maximum Buffer Temperature",
        register=4050,
        data_type="int16",
        factor=0.1,
        native_min_value=25.0,
        native_max_value=90.0,
        native_step=0.5,
        native_unit_of_measurement="°C",
    ),
    LambdaNumberEntityDescription(
        key="solar_1_setting_for_buffer_changeover_temperature",
        name="Setting for Buffer Changeover Temperature",
        register=4051,
        data_type="int16",
        factor=0.1,
        native_min_value=25.0,
        native_max_value=90.0,
        native_step=0.1,
        native_unit_of_measurement="°C",
    ),
    # Fügen Sie hier weitere Number-Beschreibungen hinzu
)




class LambdaHeatpumpNumber(CoordinatorEntity, NumberEntity):
    def __init__(
        self,
        coordinator: LambdaHeatpumpCoordinator,
        config_entry: ConfigEntry,
        description: LambdaNumberEntityDescription,
        device_info: DeviceInfo,
    ):
        super().__init__(coordinator)
        self.entity_description = description
        self._register = description.register

        self._attr_name = description.name
        self._attr_translation_key = description.key
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_device_info = device_info

        self.coordinator.add_register(self._register, description.data_type)

    @property
    def native_value(self):
        value = self.coordinator.data.get(str(self._register))
        if value is not None:
            return value * self.entity_description.factor
        return None

    async def async_set_native_value(self, value: float) -> None:
        scaled_value = int(value / self.entity_description.factor)
        await self.coordinator.async_write_register(self._register, scaled_value)
        await self.coordinator.async_request_refresh()

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    num_boilers = config_entry.data.get("amount_of_boilers", 0)
    num_buffers = config_entry.data.get("amount_of_buffers", 0)
    num_solar = config_entry.data.get("amount_of_solar", 0)
    model = config_entry.data.get("model", "Unknown Model")

    device_infos = {
        "boiler_1": DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_boiler_1")},
            name="Lambda Boiler 1",
            manufacturer=MANUFACTURER,
            model=model,
        ),
        "buffer_1": DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_buffer_1")},
            name="Lambda Buffer 1",
            manufacturer=MANUFACTURER,
            model=model,
        ),
        "solar_1": DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_solar_1")},
            name="Lambda Solar 1",
            manufacturer=MANUFACTURER,
            model=model,
        ),
    }

    numbers = []
    for description in NUMBER_DESCRIPTIONS:
        if "boiler_" in description.key and int(description.key.split('_')[1]) > num_boilers:
            continue
        if "buffer_" in description.key and int(description.key.split('_')[1]) > num_buffers:
            continue
        if "solar_" in description.key and int(description.key.split('_')[1]) > num_solar:
            continue

        category = description.key.split('_')[0]
        device_info = device_infos.get(f"{category}_{description.key.split('_')[1]}", None)

        if device_info:
            number = LambdaHeatpumpNumber(
                coordinator=coordinator,
                config_entry=config_entry,
                description=description,
                device_info=device_info,
            )
            numbers.append(number)

    async_add_entities(numbers)

# class LambdaWritableNumberEntity(CoordinatorEntity, NumberEntity):
#     def __init__(self, coordinator, name, register, model, min_value, max_value, step, factor=1, config_entry_id=None):
#         super().__init__(coordinator)
#         self._name = name
#         self._register = register
#         self._model = model
#         self._config_entry_id = config_entry_id
#         self._attr_native_min_value = min_value
#         self._attr_native_max_value = max_value
#         self._attr_native_step = step
#         self._factor = factor
#         self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

#     @property
#     def name(self):
#         return self._name

#     @property
#     def unique_id(self):
#         return f"lambda_{self.coordinator.host}_{self.coordinator.port}_{self.coordinator.slave_id}_{self._register}"

#     @property
#     def device_info(self):
#         return {
#             "identifiers": {(DOMAIN, self._config_entry_id)},
#             "name": "Lambda Wärmepumpe",
#             "manufacturer": MANUFACTURER,
#             "model": self._model,
#         }

#     @property
#     def native_value(self):
#         """Return the current value."""
#         value = self.coordinator.data.get(f"register_{self._register}")
#         return value * self._factor if value is not None else None

#     async def async_set_native_value(self, value):
#         """Update the current value."""
#         scaled_value = int(value / self._factor)
#         _LOGGER.debug(f"Writing value {value} (scaled to {scaled_value}) to register {self._register}")
#         await self.coordinator.async_write_register(self._register, scaled_value)
#         await self.coordinator.async_request_refresh()

#     async def async_added_to_hass(self):
#         """When entity is added to hass."""
#         await super().async_added_to_hass()
#         self._handle_coordinator_update()

#     @callback
#     def _handle_coordinator_update(self):
#         """Handle updated data from the coordinator."""
#         value = self.coordinator.data.get(f"register_{self._register}")
#         if value is not None:
#             self._attr_native_value = value * self._factor
#         self.async_write_ha_state()

# async def async_setup_entry(hass, entry, async_add_entities):
#     coordinator = hass.data[DOMAIN][entry.entry_id]

#     numbers = []

#     # Beispiel für einen Boiler-Setpoint
#     boiler_setpoint = LambdaWritableNumberEntity(
#         coordinator,
#         name="Boiler Maximum Temperature",
#         register=2050,
#         model=entry.data.get("model"),
#         min_value=25.0,
#         max_value=65.0,
#         step=0.1,
#         factor=0.1,
#         config_entry_id=entry.entry_id
#     )
#     numbers.append(boiler_setpoint)

#     # Hier können Sie weitere Number-Entities hinzufügen, basierend auf Ihren Anforderungen

#     async_add_entities(numbers)