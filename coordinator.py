from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.exceptions import ConnectionException
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian
from datetime import timedelta
import logging

logging.getLogger("pymodbus.logging").setLevel(logging.ERROR)

_LOGGER = logging.getLogger(__name__)

class LambdaHeatpumpCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, port, slave_id, update_interval=timedelta(seconds=10)):
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self._registers_to_read = {}
        self._client = None

        _LOGGER.debug(f"Initializing Coordinator: Host={self.host}, Port={self.port}, Slave ID={self.slave_id}")

        if not self.host or not self.port:
            raise ValueError("Invalid host or port for Modbus client.")

        super().__init__(
            hass,
            _LOGGER,
            name="LambdaHeatpumpCoordinator",
            update_interval=update_interval,
        )

    def add_register(self, register, register_type='int16'):
        self._registers_to_read[register] = register_type
    
    def remove_register(self, register):
        self._registers_to_read.pop(register, None)

    def clear_registers(self):
        self._registers_to_read.clear()

    async def _ensure_client(self):
        """Stelle sicher, dass ein aktiver Modbus-Client vorhanden ist."""
        if not self._client or not self._client.is_socket_open():
            _LOGGER.debug("Kein aktiver Client gefunden oder Socket nicht geöffnet. Erstelle neuen Client.")
            self._client = ModbusTcpClient(self.host, port=self.port)
            if not await self.hass.async_add_executor_job(self._client.connect):
                self._client = None
                raise UpdateFailed(f"Failed to connect to Modbus client {self.host}:{self.port}")

    async def _async_update_data(self):
        try:
            await self._ensure_client()
            data = {}

            for register, register_type in self._registers_to_read.items():
                try:
                    count = 2 if register_type in ['int32', 'float32'] else 1
                    result = await self.hass.async_add_executor_job(
                        self._read_register, register, count
                    )
                    if result.isError():
                        _LOGGER.error("Error reading register %s: %s", register, result)
                        data[f"register_{register}"] = None
                    else:
                        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG)
                        value = self._decode_value(decoder, register_type)
                        data[f"register_{register}"] = value
                        _LOGGER.debug("Register %s read: %s", register, value)
                except Exception as e:
                    _LOGGER.error("Error reading register %s: %s", register, e)
                    data[f"register_{register}"] = None

            return data
        except ConnectionException as conn_err:
            _LOGGER.error("Connection error: %s", conn_err)
            raise UpdateFailed(f"Connection error: {conn_err}")
        except Exception as err:
            _LOGGER.exception("Error fetching data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}")

    def _read_register(self, register, count):
        return self._client.read_holding_registers(register, count=count, slave=self.slave_id)

    def _decode_value(self, decoder, register_type):
        if register_type == 'int16':
            return decoder.decode_16bit_int()
        elif register_type == 'uint16':
            return decoder.decode_16bit_uint()
        elif register_type == 'int32':
            return decoder.decode_32bit_int()
        elif register_type == 'float32':
            return decoder.decode_32bit_float()
        else:
            _LOGGER.error("Unbekannter Registertyp %s", register_type)
            return None

    async def async_shutdown(self):
        """Schließe die Verbindung beim Herunterfahren."""
        if self._client:
            self._client.close()
            self._client = None

    async def async_write_register(self, register, value):
        """Schreibe einen Wert in ein Modbus-Register."""
        try:
            await self._ensure_client()

            def write_to_register():
                return self._client.write_registers(
                    address=register,
                    values=[value],
                    slave=self.slave_id
                )

            result = await self.hass.async_add_executor_job(write_to_register)

            if result.isError():
                raise UpdateFailed(f"Failed to write to register {register}: {result}")

            _LOGGER.debug("Successfully wrote value %s to register %s", value, register)
            await self.async_request_refresh()

        except Exception as err:
            _LOGGER.exception("Error writing to register %s: %s", register, err)
            raise UpdateFailed(f"Error writing to register {register}: {err}")

    def _write_registers(self, register, payload, count):
        return self._client.write_registers(register, payload, slave=self.slave_id, count=count)
