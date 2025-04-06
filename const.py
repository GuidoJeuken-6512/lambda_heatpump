import json
from homeassistant.const import CONF_LANGUAGE


# Domain
DOMAIN = "lambda_heatpumps"


# Manufacturer
MANUFACTURER = "Lambda Wärmepumpen GmbH"

# Configuration
CONF_MODBUS_HOST = "modbus_host"
CONF_MODBUS_PORT = "modbus_port"
CONF_SLAVE_ID = "slave_id"
CONF_MODEL = "model"
CONF_AMOUNT_OF_HEATPUMPS = "amount_of_heatpumps"
CONF_AMOUNT_OF_BOILERS = "amount_of_boilers"
CONF_AMOUNT_OF_BUFFERS = "amount_of_buffers"
CONF_AMOUNT_OF_SOLAR = "amount_of_solar"
CONF_AMOUNT_OF_HEAT_CIRCUITS = "amount_of_heat_circuits"

DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1



# Register definitions
# Modules:
# - General Ambient => GA
# - General E-Manager => EM
# - Heat pump (ModulNr. 1-3)
# - Boiler (ModulNr. 1-5)
# - Buffer (ModulNr. 1-5)
# - Solar (ModulNr. 1-2)



SENSOR_CONFIG = [
    # General Ambient
    {
        "bereich": "general_ambient",
        "name": "general_ambient_error_number",
        "register": 0,
        "type": "LambdaErrorSensor",
        "data_format": "int16"
    },
    {
        "bereich": "general_ambient",
        "name": "general_ambient_operating_state",
        "register": 1,
        "type": "LambdaStateSensor",
        "states_function": "get_operating_states",
        "data_format": "uint16"
    },
    {
        "bereich": "general_ambient",
        "name": "general_ambient_actual_ambient_temp",
        "register": 2,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "general_ambient",
        "name": "general_ambient_average_ambient_temp_1h",
        "register": 3,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "general_ambient",
        "name": "general_ambient_calculated_ambient_temp",
        "register": 4,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },

    # E-Manager
    {
        "bereich": "e_manager",
        "name": "e_manager_error_number",
        "register": 100,
        "type": "LambdaErrorSensor",
        "data_format": "int16"
    },
    {
        "bereich": "e_manager",
        "name": "e_manager_operating_state",
        "register": 101,
        "type": "LambdaStateSensor",
        "states_function": "get_operating_states",
        "data_format": "uint16"
    },
    {
        "bereich": "e_manager",
        "name": "e_manager_actual_power_input",
        "register": 102,
        "type": "LambdaPowerSensor",
        "factor": 1,
        "unit_of_measurement": "W",
        "data_format": "int16"
    },
    {
        "bereich": "e_manager",
        "name": "e_manager_actual_power_consumption",
        "register": 103,
        "type": "LambdaPowerSensor",
        "factor": 1,
        "unit_of_measurement": "W",
        "data_format": "int16"
    },
    {
        "bereich": "e_manager",
        "name": "e_manager_power_consumption_setpoint",
        "register": 104,
        "type": "LambdaPowerSensor",
        "factor": 1,
        "unit_of_measurement": "W",
        "data_format": "int16"
    },

    # Heatpump 1
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_error_state",
        "register": 1000,
        "type": "LambdaStateSensor",
        "states_function": "get_hp_error_states"   ,
        "data_format": "uint16"     
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_error_number",
        "register": 1001,
        "type": "LambdaErrorSensor"  ,
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_state",
        "register": 1002,
        "type": "LambdaStateSensor",
        "states_function": "get_hp_states"   ,
        "data_format": "uint16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_operating_state",
        "register": 1003,
        "type": "LambdaStateSensor",
        "states_function": "get_hp_operation_states"   ,
        "data_format": "uint16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_flowline_temp",
        "register": 1004,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_returnline_temp",
        "register": 1005,
        "type": "LambdaTemperaturSensor",
        "factor": 0.01,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_flow_heat_sink",
        "register": 1006,
        "type": "LambdaFlowSensor",
        "factor": 0.01,
        "unit_of_measurement": "m³/h",
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_energy_source_inlet_temperature",
        "register": 1007,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_energy_source_outlet_temperature",
        "register": 1008,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {   
        "bereich": "heatpump_1",
        "name": "heatpump_1_volume_flow_energy_source",
        "register": 1009,
        "type": "LambdaFlowSensor",
        "factor": 0.01,
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_compressor_unit_rating",
        "register": 1010,
        "type": "LambdaPercentageSensor",
        "factor": 0.01,
        "data_format": "uint16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_actual_heating_capacity",
        "register": 1011,
        "type": "LambdaPowerSensor",
        "factor": 0.01,
        "unit_of_measurement": "kW",
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_frequency_inverter_actual_power_consumption",
        "register": 1012,
        "type": "LambdaPowerSensor",
        "factor": 1,
        "unit_of_measurement": "W",
        "data_format": "int16"
    },

    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_coefficient_of_performance",
        "register": 1013,
        "type": "LambdaPercentageSensor",
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_password_register_to_release_modbus_request_registers",
        "register": 1014,
        "type": "LambdaErrorSensor",
        "data_format": "uint16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_request_type",
        "register": 1015,
        "type": "LambdaStateSensor",
        "states_function": "get_hp_request_types",
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_requested_flow_line_temperature",
        "register": 1016,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "min": 0.0,
        "max": 70.0,
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_requested_return_line_temperature",
        "register": 1017,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "min": 0.0,
        "max": 65.0,
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_requested_temperature_difference_between_flow_line_and_return_line",
        "register": 1018,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "K",
        "min": 0.0,
        "max": 35.0,
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_relais_state_for_2nd_heating_stage",
        "register": 1019,
        "type": "LambdaStateSensor",
        "states_function": "get_hp_relais_states",
        "data_format": "int16"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_accumulated_electrical_energy_consumption_of_compressor_unit",
        "register": 1020,
        "type": "LambdaEnergySensor",
        "factor": 1,
        "unit_of_measurement": "Wh",
        "data_format": "int32"
    },
    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_accumulated_thermal_energy_output_of_compressor_unit",
        "register": 1022,
        "type": "LambdaEnergySensor",
        "factor": 1,
        "unit_of_measurement": "Wh",
        "data_format": "int32"
    },

    {
        "bereich": "heatpump_1",
        "name": "heatpump_1_quit_all_active_heat_pump_errors",
        "register": 1050,
        "type": "LambdaErrorSensor",
        "data_format": "uint16"
    },



    # Boiler 1
    {
        "bereich": "boiler_1",
        "name": "boiler_1_error_number",
        "register": 2000,
        "type": "LambdaErrorSensor",
        "data_format": "int16"
    },
    {
        "bereich": "boiler_1",
        "name": "boiler_1_operating_state",
        "register": 2001,
        "type": "LambdaStateSensor",
        "states_function": "get_boiler_operating_states",
        "data_format": "uint16"
    },
    {
        "bereich": "boiler_1",
        "name": "boiler_1_actual_temperature_boiler_high_sensor",
        "register": 2002,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "boiler_1",
        "name": "boiler_1_actual_temperature_boiler_low_sensor",
        "register": 2003,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "boiler_1",
        "name": "boiler_1_setting_for_maximum_boiler_temperature",
        "register": 2050,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    

    # Buffer 1
    {
        "bereich": "buffer_1",
        "name": "buffer_1_error_number",
        "register": 3000,
        "type": "LambdaErrorSensor",
        "data_format": "int16"
    },
    {
        "bereich": "buffer_1",
        "name": "buffer_1_operating_state",
        "register": 3001,
        "type": "LambdaStateSensor",
        "states_function": "get_buffer_operating_states",
        "data_format": "uint16"
    },
    {
        "bereich": "buffer_1",
        "name": "buffer_1_actual_temperature_buffer_high_sensor",
        "register": 3002,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "buffer_1",
        "name": "buffer_1_actual_temperature_buffer_low_sensor",
        "register": 3003,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "buffer_1",
        "name": "buffer_1_setting_for_maximum_buffer_temperature",
        "register": 3050,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },

    # Solar 1
    {
        "bereich": "solar_1",
        "name": "solar_1_error_number",
        "register": 4000,
        "type": "LambdaErrorSensor",
        "data_format": "int16"
    },
    {
        "bereich": "solar_1",
        "name": "solar_1_operating_state",
        "register": 4001,
        "type": "LambdaStateSensor",
        "states_function": "get_solar_operating_states",
        "data_format": "uint16"
    },
    {
        "bereich": "solar_1",
        "name": "solar_1_actual_temperatur_collector_sensor", 
        "register": 4002,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "solar_1",
        "name": "solar_1_actual_temperature_buffer_1_sensor",
        "register": 4003,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "solar_1",
        "name": "solar_1_actual_temperature_buffer_2_sensor",
        "register": 4004,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "solar_1",
        "name": "solar_1_setting_for_maximum_buffer_temperature",
        "register": 4050,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "min": 25.0,
        "max": 90.0,
        "data_format": "int16"
    },
    {
        "bereich": "solar_1",
        "name": "solar_1_setting_for_buffer_changeover_temperature",
        "register": 4051,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "min": 25.0,
        "max": 90.0,
        "data_format": "int16"
    },


    # Heating Circuit 1
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_error_number",
        "register": 5000,
        "type": "LambdaErrorSensor",
        "data_format": "int16"
    },
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_operating_state",
        "register": 5001,
        "type": "LambdaStateSensor",
        "states_function": "get_heatingcircuit_operating_states",
        "data_format": "uint16"
    },
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_actual_temperature_flow_line_sensor",
        "register": 5002,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_actual_temperature_return_line_sensor",
        "register": 5003,
        "type": "LambdaTemperaturSensor",
        "factor": 0.01,
        "unit_of_measurement": "°C",
        "data_format": "int16"
    },
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_actual_temperature_room_device_sensor",
        "register": 5004,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "min": -29.9,
        "max": 99.9,
        "data_format": "int16"
    },
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_setpoint_temperature_flow_line",
        "register": 5005,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "min": 15.0,
        "max": 65.0,
        "data_format": "int16"
    },
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_operating_mode",
        "register": 5006,
        "type": "LambdaStateSensor",
        "states_function": "get_heatingcircuit_operating_modes"     ,
        "data_format": "int16"   
    },
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_setting_for_flow_line_temperature_setpoint_offset",
        "register": 5050,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "K",
        "min": -10.0,
        "max": 10.0,
        "data_format": "int16"
    },
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_setting_for_heating_mode_room_setpoint_temperature",
        "register": 5051,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "min": 15.0,
        "max": 40.0,
        "data_format": "int16"
    },
    {
        "bereich": "heatingcircuit_1",
        "name": "heatingcircuit_1_setting_for_cooling_mode_room_setpoint_temperature",
        "register": 5052,
        "type": "LambdaTemperaturSensor",
        "factor": 0.1,
        "unit_of_measurement": "°C",
        "min": 15.0,
        "max": 40.0,
        "data_format": "int16"
    },
]


async def async_get_translation(hass, key, language="en"):
    translations = await async_get_translations(hass, language, DOMAIN)
    return translations.get(key, key)

def get_operating_states(language="en"):
    states = {
        0: "OFF",
        1: "AUTOMATIC",
        2: "MANUAL",
        3: "ERROR",
        4: "OFFLINE"
    }
    return states

def get_hp_error_states(language="en"):
    # Beispielhafte Zustände, diese sollten entsprechend der tatsächlichen Zustände angepasst werden
    states = {
        0: "NONE",
        1: "MESSAGE",
        2: "WARNING",
        3: "ALARM",
        4: "FAULT"
    }
    return states

def get_hp_states(language="en"):
    # Beispielhafte Zustände, diese sollten entsprechend der tatsächlichen Zustände angepasst werden
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
    return states


def get_hp_operation_states(language="en"):
    # Beispielhafte Zustände, diese sollten entsprechend der tatsächlichen Zustände angepasst werden
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
    return states

def get_hp_request_types(language="en"):
    # Beispielhafte Zustände, diese sollten entsprechend der tatsächlichen Zustände angepasst werden
    types = {
        0: "NO REQUEST",
        1: "FLOW PUMP CIRCULATION",
        2: "CENTRAL HEATING",
        3: "CENTRAL COOLING",
        4: "DOMESTIC HOT WATER"
    }
    return types

def get_hp_relais_states(language="en"):
    # 1 = NO-Relais for 2nd heating stage is activated
    states = {
        0: "OFF",
        1: "ON"
    }
    return states

def get_boiler_operating_states(language="en"):
    # Beispielhafte Zustände, diese sollten entsprechend der tatsächlichen Zustände angepasst werden
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
    return states

def get_buffer_operating_states(language="en"):
    # Beispielhafte Zustände, diese sollten entsprechend der tatsächlichen Zustände angepasst werden
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
    return states

def get_solar_operating_states(language="en"):
    # Beispielhafte Zustände, diese sollten entsprechend der tatsächlichen Zustände angepasst werden
    states = {
        0: "STBY",
        1: "HEATING",
        2: "ERROR",
        3: "OFF"
    }
    return states


def get_heatingcircuit_operating_states(language="en"):
    # Beispielhafte Zustände, diese sollten entsprechend der tatsächlichen Zustände angepasst werden
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
    return states


def get_heatingcircuit_operating_modes(language="en"):
    # Beispielhafte Zustände, diese sollten entsprechend der tatsächlichen Zustände angepasst werden
    modes = {
        0: "OFF",
        1: "MANUAL",
        2: "AUTOMATIC",
        3: "AUTO-HEATING",
        4: "AUTO-COOLING",
        5: "FROST",
        6: "SUMMER",
        7: "FLOOR-DRY"
    }
    return modes