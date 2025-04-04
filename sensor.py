from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final, Optional, Dict

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MANUFACTURER
from .coordinator import LambdaHeatpumpCoordinator

@dataclass(kw_only=True)
class LambdaSensorEntityDescription(SensorEntityDescription):
    """Beschreibung eines Lambda Heatpump Sensors."""
    register: int
    data_type: str = "int16"
    factor: float = 1.0
    unit_of_measurement: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    states: Optional[Dict[int, str]] = field(default_factory=dict)


_LOGGER = logging.getLogger(__name__)


SENSOR_DESCRIPTIONS: Final[tuple[LambdaSensorEntityDescription, ...]] = (
    # General Ambient
    LambdaSensorEntityDescription(
        key="general_ambient_error_number",
        name="Error Number",
        register=0,
        data_type="int16",
    ),
    LambdaSensorEntityDescription(
        key="general_ambient_operating_state",
        name="Operating State",
        register=1,
        data_type="uint16",
        states = {
            0: "OFF",
            1: "AUTOMATIC",
            2: "MANUAL",
            3: "ERROR",
            4: "OFFLINE"
        }
    ),
    LambdaSensorEntityDescription(
        key="general_ambient_actual_ambient_temp",
        name="Actual Ambient Temperature",
        register=2,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="general_ambient_average_ambient_temp_1h",
        name="Average Ambient Temperature (1h)",
        register=3,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="general_ambient_calculated_ambient_temp",
        name="Calculated Ambient Temperature",
        register=4,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),

    # E-Manager
    LambdaSensorEntityDescription(
        key="e_manager_error_number",
        name="Error Number",
        register=100,
        data_type="int16",
    ),
    LambdaSensorEntityDescription(
        key="e_manager_operating_state",
        name="Operating State",
        register=101,
        data_type="uint16",
        states = {
            0: "OFF",
            1: "AUTOMATIK",
            2: "MANUAL",
            3: "ERROR",
            4: "OFFLINE"
        }
    ),
    LambdaSensorEntityDescription(
        key="e_manager_actual_power_input",
        name="Actual Power Input",
        register=102,
        data_type="int16",
        factor=1,
        unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT
    ),
    LambdaSensorEntityDescription(
        key="e_manager_actual_power_consumption",
        name="Actual Power Consumption",
        register=103,
        data_type="int16",
        factor=1,
        unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT
    ),
    LambdaSensorEntityDescription(
        key="e_manager_power_consumption_setpoint",
        name="Power Consumption Setpoint",
        register=104,
        data_type="int16",
        factor=1,
        unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT
    ),

    # Heatpump 1
    LambdaSensorEntityDescription(
        key="heatpump_1_error_state",
        name="Error State",
        register=1000,
        data_type="uint16",
        states = {
            0: "NONE",
            1: "MESSAGE",
            2: "WARNING",
            3: "ALARM",
            4: "FAULT"
        }
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_error_number",
        name="Error Number",
        register=1001,
        data_type="int16",
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_state",
        name="State",
        register=1002,
        data_type="uint16",
        states = {
            0: "INIT",
            1: "REFERENCE",
            2: "RESTART-BLOCK",
            3: "READY",
            4: "START PUMPS",
            5: "START COMPRESSOR",
            6: "PRE-REGULATION",
            7: "REGULATION",
            8: "Not Used",
            9: "COOLING",
            10: "DEFROSTING",
            20: "STOPPING",
            30: "FAULT-LOCK",
            31: "ALARM-BLOCK",
            40: "ERROR-RESET"
        }
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_operating_state",
        name="Operating State",
        register=1003,
        data_type="uint16",
        states = {
            0: "STBY",
            1: "CH",
            2: "DHW",
            3: "CC",
            4: "CIRCULATE",
            5: "DEFROST",
            6: "OFF",
            7: "FROST",
            8: "STBY-FROST",
            9: "Not used",
            10: "SUMMER",
            11: "HOLIDAY",
            12: "ERROR",
            13: "WARNING",
            14: "INFO-MESSAGE",
            15: "TIME-BLOCK",
            16: "RELEASE-BLOCK",
            17: "MINTEMP-BLOCK",
            18: "FIRMWARE-DOWNLOAD"
        }
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_flowline_temp",
        name="Flowline Temperature",
        register=1004,
        data_type="int16",
        factor=0.01,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_returnline_temp",
        name="Returnline Temperature",
        register=1005,
        data_type="int16",
        factor=0.01,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_flow_heat_sink",
        name="Flow Heat Sink",
        register=1006,
        data_type="int16",
        factor=0.01,
        unit_of_measurement="m³/h",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_energy_source_inlet_temperature",
        name="Energy Source Inlet Temperature",
        register=1007,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_energy_source_outlet_temperature",
        name="Energy Source Outlet Temperature",
        register=1008,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_volume_flow_energy_source",
        name="Volume Flow Energy Source",
        register=1009,
        data_type="int16",
        factor=0.01,
        unit_of_measurement="m³/h",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_compressor_unit_rating",
        name="Compressor Unit Rating",
        register=1010,
        data_type="uint16",
        factor=0.01,
        unit_of_measurement="%",
        device_class=SensorDeviceClass.POWER_FACTOR
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_actual_heating_capacity",
        name="Actual Heating Capacity",
        register=1011,
        data_type="int16",
        factor=10,
        unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_frequency_inverter_actual_power_consumption",
        name="Frequency Inverter Actual Power Consumption",
        register=1012,
        data_type="int16",
        factor=1,
        unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_coefficient_of_performance",
        name="Coefficient of Performance",
        register=1013,
        data_type="int16",
        factor=0.01,
        device_class=SensorDeviceClass.POWER_FACTOR
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_password_register_to_release_modbus_request_registers",
        name="Password Register to Release Modbus Request Registers",
        register=1014,
        data_type="uint16",
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_request_type",
        name="Request Type",
        register=1015,
        data_type="int16",
        states = {
            0: "NO REQUEST",
            1: "FLOW PUMP CIRCULATION",
            2: "CENTRAL HEATING",
            3: "CENTRAL COOLING",
            4: "DOMESTIC HOT WATER"
        }
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_requested_flow_line_temperature",
        name="Requested Flow Line Temperature",
        register=1016,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        min_value=0.0,
        max_value=70.0,
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_requested_return_line_temperature",
        name="Requested Return Line Temperature",
        register=1017,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        min_value=0.0,
        max_value=65.0,
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_requested_temperature_difference_between_flow_line_and_return_line",
        name="Requested Temperature Difference between Flow Line and Return Line",
        register=1018,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="K",
        min_value=0.0,
        max_value=35.0,
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_relais_state_for_2nd_heating_stage",
        name="Relais State for 2nd Heating Stage",
        register=1019,
        data_type="int16",
        states = {
            0: "OFF",
            1: "ON"
        }
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_accumulated_electrical_energy_consumption_of_compressor_unit",
        name="Accumulated Electrical Energy Consumption of Compressor Unit",
        register=1020,
        data_type="int32",
        factor=1,
        unit_of_measurement="Wh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_accumulated_thermal_energy_output_of_compressor_unit",
        name="Accumulated Thermal Energy Output of Compressor Unit",
        register=1022,
        data_type="int32",
        factor=1,
        unit_of_measurement="Wh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING
    ),
    LambdaSensorEntityDescription(
        key="heatpump_1_quit_all_active_heat_pump_errors",
        name="Quit All Active Heat Pump Errors",
        register=1050,
        data_type="uint16"
    ),

    # Boiler 1
    LambdaSensorEntityDescription(
        key="boiler_1_error_number",
        name="Error Number",
        register=2000,
        data_type="int16",
    ),
    LambdaSensorEntityDescription(
        key="boiler_1_operating_state",
        name="Boiler 1 Operating State",
        register=2001,
        data_type="uint16",
        states = {
            0: "STBY",
            1: "DHW",
            2: "LEGIO",
            3: "SUMMER",
            4: "FROST",
            5: "HOLIDAY",
            6: "PRIO-STOP",
            7: "ERROR",
            8: "OFF",
            9: "PROMPT-DHW",
            10: "TRAILING-STOP",
            11: "TEMP-LOCK",
            12: "STBY-FROST"
        }
    ),
    LambdaSensorEntityDescription(
        key="boiler_1_actual_temperature_boiler_high_sensor",
        name="Actual Temperature Boiler High Sensor",
        register=2002,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="boiler_1_actual_temperature_boiler_low_sensor",
        name="Actual Temperature Boiler Low Sensor",
        register=2003,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    # LambdaSensorEntityDescription(
    #     key="boiler_1_setting_for_maximum_boiler_temperature",
    #     name="Setting for Maximum Boiler Temperature",
    #     register=2050,
    #     data_type="int16",
    #     factor=0.1,
    #     unit_of_measurement="°C",
    #     device_class=SensorDeviceClass.TEMPERATURE
    # ),

    # Buffer 1
    LambdaSensorEntityDescription(
        key="buffer_1_error_number",
        name="Error Number",
        register=3000,
        data_type="int16",
    ),
    LambdaSensorEntityDescription(
        key="buffer_1_operating_state",
        name="Operating State",
        register=3001,
        data_type="uint16",
        states = {
            0: "STBY",
            1: "HEATING",
            2: "COOLING",
            3: "SUMMER",
            4: "FROST",
            5: "HOLIDAY",
            6: "PRIO-STOP",
            7: "ERROR",
            8: "OFF",
            9: "STBY-FROST"
        }
    ),
    LambdaSensorEntityDescription(
        key="buffer_1_actual_temperature_buffer_high_sensor",
        name="Actual Temperature Buffer High Sensor",
        register=3002,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="buffer_1_actual_temperature_buffer_low_sensor",
        name="Actual Temperature Buffer Low Sensor",
        register=3003,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="buffer_1_setting_for_maximum_buffer_temperature",
        name="Setting for Maximum Buffer Temperature",
        register=3050,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),

    # Solar 1
    LambdaSensorEntityDescription(
        key="solar_1_error_number",
        name="Error Number",
        register=4000,
        data_type="int16",
    ),
    LambdaSensorEntityDescription(
        key="solar_1_operating_state",
        name="Operating State",
        register=4001,
        data_type="uint16",
        states = {
            0: "STBY",
            1: "HEATING",
            2: "ERROR",
            3: "OFF"
        }
    ),
    LambdaSensorEntityDescription(
        key="solar_1_actual_temperatur_collector_sensor",
        name="Actual Temperature Collector Sensor",
        register=4002,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="solar_1_actual_temperature_buffer_1_sensor",
        name="Actual Temperature Buffer 1 Sensor",
        register=4003,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="solar_1_actual_temperature_buffer_2_sensor",
        name="Actual Temperature Buffer 2 Sensor",
        register=4004,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="solar_1_setting_for_maximum_buffer_temperature",
        name="Setting for Maximum Buffer Temperature",
        register=4050,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        min_value=25.0,
        max_value=90.0,
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="solar_1_setting_for_buffer_changeover_temperature",
        name="Setting for Buffer Changeover Temperature",
        register=4051,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        min_value=25.0,
        max_value=90.0,
        device_class=SensorDeviceClass.TEMPERATURE
    ),

    # Heating Circuit 1
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_error_number",
        name="Error Number",
        register=5000,
        data_type="int16",
    ),
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_operating_state",
        name="Operating State",
        register=5001,
        data_type="uint16",
        states = {
            0: "HEATING",
            1: "ECO",
            2: "COOLING",
            3: "FLOORDRY",
            4: "FROST",
            5: "MAX-TEMP",
            6: "ERROR",
            7: "SERVICE",
            8: "HOLIDAY",
            9: "CH-SUMMER",
            10: "CC-WINTER",
            11: "PRIO-STOP",
            12: "OFF",
            13: "RELEASE-OFF",
            14: "TIME-OFF",
            15: "STBY",
            16: "STBY-HEATING",
            17: "STBY-ECO",
            18: "STBY-COOLING",
            19: "STBY-FROST",
            20: "STBY-FLOORDRY"
        }
    ),
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_actual_temperature_flow_line_sensor",
        name="Actual Temperature Flow Line Sensor",
        register=5002,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_actual_temperature_return_line_sensor",
        name="Actual Temperature Return Line Sensor",
        register=5003,
        data_type="int16",
        factor=0.01,
        unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_actual_temperature_room_device_sensor",
        name="Actual Temperature Room Device Sensor",
        register=5004,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        min_value=-29.9,
        max_value=99.9,
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_setpoint_temperature_flow_line",
        name="Setpoint Temperature Flow Line",        
        register=5005,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        min_value=15.0,
        max_value=65.0,
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_operating_mode",
        name="Operating Mode",
        register=5006,
        data_type="int16",
        states = {
            0: "OFF",
            1: "MANUAL",
            2: "AUTOMATIC",
            3: "AUTO-HEATING",
            4: "AUTO-COOLING",
            5: "FROST",
            6: "SUMMER",
            7: "FLOOR-DRY"
        }
    ),
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_setting_for_flow_line_temperature_setpoint_offset",
        name="Setting for Flow Line Temperature Setpoint Offset",
        register=5050,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="K",
        min_value=-10.0,
        max_value=10.0,
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_setting_for_heating_mode_room_setpoint_temperature",
        name="Setting for Heating Mode Room Setpoint Temperature",
        register=5051,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        min_value=15.0,
        max_value=40.0,
        device_class=SensorDeviceClass.TEMPERATURE
    ),
    LambdaSensorEntityDescription(
        key="heatingcircuit_1_setting_for_cooling_mode_room_setpoint_temperature",
        name="Setting for Cooling Mode Room Setpoint Temperature",
        register=5052,
        data_type="int16",
        factor=0.1,
        unit_of_measurement="°C",
        min_value=15.0,
        max_value=40.0,
        device_class=SensorDeviceClass.TEMPERATURE
    ),

)



class LambdaHeatpumpSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: LambdaHeatpumpCoordinator,
        config_entry: ConfigEntry,
        description: LambdaSensorEntityDescription,
        device_info: DeviceInfo,
    ):
        super().__init__(coordinator)
        self.entity_description = description
        self._register = description.register

        # Setze den Namen
        self._attr_name = description.name
        self._attr_translation_key = description.key

        # Eindeutige ID mit config_entry.entry_id und description.key
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"

        # self._attr_entity_id = f"sensor.{description.key}"

        # Geräteinformationen
        self._attr_device_info = device_info
        # self._attr_device_info = DeviceInfo(
        #     identifiers={(DOMAIN, config_entry.entry_id)},
        #     name="Lambda Wärmepumpe",
        #     manufacturer=MANUFACTURER,
        #     model=model,
        # )

        _LOGGER.debug("Description: %s", description)
        _LOGGER.debug("Übersetzung: %s", self.entity_description.key)

        self.coordinator.add_register(self._register, description.data_type)

    @property
    def native_value(self):
        value = self.coordinator.data.get(f"register_{self._register}")
        if value is not None:
            # Wenn der Sensor ein Fehlernummer-Sensor ist, geben wir den Wert als Integer zurück
            if "error_number" in self.entity_description.key:
                return int(value)
            # Wenn der Sensor Zustände hat, geben wir den Zustand zurück
            if self.entity_description.states:
                return self.entity_description.states.get(value, "Unknown")
            value = value * self.entity_description.factor
            return value
        return None
    
    @property
    def native_unit_of_measurement(self):
        return self.entity_description.unit_of_measurement
    
    @property
    def native_translation_key(self):
        return self.entity_description.key
    
    @property
    def translation_key(self):
        return self.entity_description.key

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Richtet die Sensorplattform für einen Konfigurations-Eintrag ein."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Hole die Konfigurationswerte aus config_flow
    num_heatpumps = config_entry.data.get("amount_of_heatpumps", 1)
    num_boilers = config_entry.data.get("amount_of_boilers", 0)
    num_buffers = config_entry.data.get("amount_of_buffers", 0)
    num_solar = config_entry.data.get("amount_of_solar", 0)
    num_heatingcircuits = config_entry.data.get("amount_of_heat_circuits", 1)
    model = config_entry.data.get("model", "Unknown Model")  # Hole das Modell aus der Konfiguration

    device_infos = {
        "general_ambient": DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_general_ambient")},
            name="Lambda General Ambient",
            manufacturer=MANUFACTURER,
            model=model,
        ),
        "e_manager": DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_e_manager")},
            name="Lambda E-Manager",
            manufacturer=MANUFACTURER,
            model=model,
        ),
    }

    # Erstelle Geräteinformationen für mehrere Geräte pro Kategorie
    for i in range(1, num_heatpumps + 1):
        device_infos[f"heatpump_{i}"] = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_heatpump_{i}")},
            name=f"Lambda Heatpump {i}",
            manufacturer=MANUFACTURER,
            model=model,
        )

    for i in range(1, num_boilers + 1):
        device_infos[f"boiler_{i}"] = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_boiler_{i}")},
            name=f"Lambda Boiler {i}",
            manufacturer=MANUFACTURER,
            model=model,
        )

    for i in range(1, num_buffers + 1):
        device_infos[f"buffer_{i}"] = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_buffer_{i}")},
            name=f"Lambda Buffer {i}",
            manufacturer=MANUFACTURER,
            model=model,
        )

    for i in range(1, num_solar + 1):
        device_infos[f"solar_{i}"] = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_solar_{i}")},
            name=f"Lambda Solar {i}",
            manufacturer=MANUFACTURER,
            model=model,
        )

    for i in range(1, num_heatingcircuits + 1):
       device_infos[f"heatingcircuit_{i}"] = DeviceInfo(
           identifiers={(DOMAIN, f"{config_entry.entry_id}_heatingcircuit_{i}")},
           name=f"Lambda Heating Circuit {i}",
           manufacturer=MANUFACTURER,
           model=model,
       )
    sensors = []
    for description in SENSOR_DESCRIPTIONS:
        if "heatpump_" in description.key and int(description.key.split('_')[1]) > num_heatpumps:
            continue
        if "boiler_" in description.key and int(description.key.split('_')[1]) > num_boilers:
            continue
        if "buffer_" in description.key and int(description.key.split('_')[1]) > num_buffers:
            continue
        if "solar_" in description.key and int(description.key.split('_')[1]) > num_solar:
            continue
        if "heatingcircuit_" in description.key and int(description.key.split('_')[1]) > num_heatingcircuits:
            continue

        category = description.key.split('_')[0]
        # device_info = device_infos.get(description.key.split('_')[0], device_infos.get(f"{category}_{description.key.split('_')[1]}", None))
        device_info = device_infos.get(f"{category}_{description.key.split('_')[1]}", device_infos.get(category, None))

        _LOGGER.debug("Creating sensor: %s with device_info: %s", description.key, device_info)
        
        sensor = LambdaHeatpumpSensor(
            coordinator=coordinator,
            config_entry=config_entry,
            description=description,
            device_info=device_info, 
        )
        sensors.append(sensor)

    async_add_entities(sensors)

