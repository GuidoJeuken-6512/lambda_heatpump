from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.exceptions import ConnectionException
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian
from datetime import timedelta
import logging
from typing import Dict, Any, Optional, Union, List
import asyncio
from functools import wraps
from dataclasses import dataclass
import struct
from homeassistant.core import HomeAssistant

logging.getLogger("pymodbus.logging").setLevel(logging.ERROR)

_LOGGER = logging.getLogger(__name__)

@dataclass
class ModbusConfig:
    """Konfiguration für die Modbus-Verbindung."""
    host: str
    port: int
    slave_id: int
    connection_timeout: int = 5
    retry_count: int = 3
    retry_delay: float = 1.0
    update_interval: timedelta = timedelta(seconds=10)
    max_register_chunk_size: int = 50

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        _LOGGER.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator

class LambdaHeatpumpCoordinator(DataUpdateCoordinator):
    """Koordinator für die Lambda-Wärmepumpe über Modbus."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        config: ModbusConfig,
    ):
        """Initialisiere den Lambda-Wärmepumpen-Koordinator.
        
        Args:
            hass: Home Assistant Instanz
            config: Modbus-Konfiguration
        """
        if not hass:
            raise ValueError("Home Assistant Instanz darf nicht None sein")
            
        if not config:
            raise ValueError("Modbus-Konfiguration darf nicht None sein")
            
        self.config = config
        self._validate_config()
        
        self._registers_to_read: Dict[int, str] = {}
        self._client: Optional[ModbusTcpClient] = None
        self._last_successful_update: Optional[float] = None
        self._connection_status: bool = False
        self._register_cache: Dict[int, Any] = {}
        self._cache_timestamp: Dict[int, float] = {}
        self._cache_duration: float = 5.0  # Cache-Dauer in Sekunden
        self.data: Dict[str, Any] = {}  # Initialisiere data als leeres Dictionary

        _LOGGER.debug(
            "Initializing Coordinator: Host=%s, Port=%d, Slave ID=%d, "
            "Update Interval=%s, Connection Timeout=%d",
            self.config.host,
            self.config.port,
            self.config.slave_id,
            self.config.update_interval,
            self.config.connection_timeout
        )

        try:
            super().__init__(
                hass,
                _LOGGER,
                name="LambdaHeatpumpCoordinator",
                update_interval=self.config.update_interval,
            )
        except Exception as e:
            _LOGGER.error("Fehler bei der Initialisierung des Coordinators: %s", e)
            raise

    def _validate_config(self) -> None:
        """Validiere die Modbus-Konfiguration."""
        if not self.config.host:
            raise ValueError("Host-Adresse darf nicht leer sein")
            
        if not 1 <= self.config.port <= 65535:
            raise ValueError(f"Ungültiger Port: {self.config.port}")
            
        if not 1 <= self.config.slave_id <= 247:
            raise ValueError(f"Ungültige Slave-ID: {self.config.slave_id}")
            
        if self.config.connection_timeout < 1:
            raise ValueError(f"Ungültiger Connection Timeout: {self.config.connection_timeout}")
            
        if self.config.retry_count < 1:
            raise ValueError(f"Ungültige Anzahl von Wiederholungsversuchen: {self.config.retry_count}")
            
        if self.config.retry_delay < 0:
            raise ValueError(f"Ungültige Verzögerung zwischen Wiederholungsversuchen: {self.config.retry_delay}")
            
        if self.config.max_register_chunk_size < 1 or self.config.max_register_chunk_size > 125:
            raise ValueError(f"Ungültige Chunk-Größe: {self.config.max_register_chunk_size}")

    def add_register(self, register: int, register_type: str = 'int16') -> None:
        """Füge ein Register zur Liste der zu lesenden Register hinzu.
        
        Args:
            register: Die Register-Adresse
            register_type: Der Typ des Registers (int16, uint16, int32, float32)
        """
        if register_type not in ['int16', 'uint16', 'int32', 'float32']:
            _LOGGER.warning(f"Unsupported register type: {register_type}. Using default type 'int16'")
            register_type = 'int16'
            
        self._registers_to_read[register] = register_type
        _LOGGER.debug(f"Added register {register} with type {register_type} to read list. Total registers: {len(self._registers_to_read)}")
        
        # Debug-Ausgabe aller registrierten Register
        _LOGGER.debug("Currently registered registers:")
        for reg, reg_type in self._registers_to_read.items():
            _LOGGER.debug(f"  - Register {reg} (Type: {reg_type})")
    
    def remove_register(self, register):
        self._registers_to_read.pop(register, None)

    def clear_registers(self):
        self._registers_to_read.clear()

    @retry_on_failure(max_retries=3)
    async def _ensure_client(self) -> None:
        """Stelle sicher, dass ein aktiver Modbus-Client vorhanden ist."""
        if not self._client or not self._client.is_socket_open():
            _LOGGER.debug("Kein aktiver Client gefunden oder Socket nicht geöffnet. Erstelle neuen Client.")
            self._client = ModbusTcpClient(
                self.config.host,
                port=self.config.port,
                timeout=self.config.connection_timeout
            )
            if not await self.hass.async_add_executor_job(self._client.connect):
                self._client = None
                self._connection_status = False
                raise UpdateFailed(f"Failed to connect to Modbus client {self.config.host}:{self.config.port}")
            self._connection_status = True

    async def _async_update_data(self) -> Dict[str, Any]:
        """Aktualisiere die Daten von der Wärmepumpe."""
        try:
            await self._ensure_client()
            data = {}
            self._last_successful_update = self.hass.loop.time()
            
            # Debug-Ausgabe der zu lesenden Register
            _LOGGER.debug("Registers to read:")
            for register, reg_type in self._registers_to_read.items():
                _LOGGER.debug(f"  - Register {register} ({reg_type})")
            
            # Gruppiere Register für effizientere Abfragen
            grouped_registers = self._group_registers_by_type()
            
            for register_type, registers in grouped_registers.items():
                try:
                    _LOGGER.debug(f"Reading registers of type {register_type}: {registers}")
                    result = await self._read_grouped_registers(registers, register_type)
                    
                    for register, value in result.items():
                        if value is not None:
                            data[f"register_{register}"] = value
                            _LOGGER.debug(f"Register {register} value: {value}")
                        else:
                            _LOGGER.warning(f"Register {register} returned None")
                            
                except Exception as e:
                    _LOGGER.error(f"Error reading registers of type {register_type}: {e}")
                    for register in registers:
                        data[f"register_{register}"] = None
                        _LOGGER.warning(f"Setting register {register} to None due to error")

            _LOGGER.debug(f"Update completed. Data contains {len(data)} values")
            _LOGGER.debug(f"Available registers in data: {list(data.keys())}")

            # Debug-Ausgabe für Register 2002 und 2003
            for register in [2002, 2003]:
                _LOGGER.debug(f"Starting Modbus read for register {register}")
                
                # Lesen der Holding-Register
                result = await self.hass.async_add_executor_job(
                    lambda: self._client.read_holding_registers(address=register, count=1, slave=self.config.slave_id)
                )
                
                if result.isError():
                    _LOGGER.error(f"Modbus error reading register {register}: {result}")
                    continue
                    
                _LOGGER.debug(f"Raw Modbus response for register {register}: {result.registers}")
                
                # Decodieren des Wertes
                value = struct.unpack(">h", struct.pack(">H", result.registers[0]))[0]
                _LOGGER.debug(f"Decoded int16 value for register {register}: {value}")
                
                # Speichern des Wertes
                data[f"register_{register}"] = value
                _LOGGER.debug(f"Register {register} value: {value}")
            
            return data
            
        except ConnectionException as conn_err:
            self._connection_status = False
            _LOGGER.error("Connection error: %s", conn_err)
            raise UpdateFailed(f"Connection error: {conn_err}")
        except Exception as err:
            _LOGGER.exception("Error fetching data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}")

    def _group_registers_by_type(self) -> Dict[str, list]:
        """Gruppiere Register nach ihrem Typ für effizientere Abfragen."""
        grouped = {}
        for register, reg_type in self._registers_to_read.items():
            if reg_type not in grouped:
                grouped[reg_type] = []
            grouped[reg_type].append(register)
            
        # Debug-Ausgabe der gruppierten Register
        _LOGGER.debug("Grouped registers by type:")
        for reg_type, registers in grouped.items():
            _LOGGER.debug(f"  - Type {reg_type}: {registers}")
            
        return grouped

    def _split_registers_into_chunks(self, registers: list, max_chunk_size: int = 50) -> list:
        """Teile Register in kleinere Blöcke auf."""
        if not registers:
            return []
        
        registers.sort()
        chunks = []
        current_chunk = []
        
        for register in registers:
            if not current_chunk:
                current_chunk.append(register)
            else:
                if register - current_chunk[0] < max_chunk_size:
                    current_chunk.append(register)
                else:
                    chunks.append(current_chunk)
                    current_chunk = [register]
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    async def _read_grouped_registers(self, registers: list, register_type: str) -> Dict[int, Any]:
        """Lese eine Gruppe von Registern effizient."""
        if not registers:
            return {}
            
        values = {}
        register_chunks = self._split_registers_into_chunks(registers)
        
        for chunk in register_chunks:
            try:
                start_register = chunk[0]
                count = len(chunk)
                
                # Für 32-Bit-Werte müssen wir die Anzahl der Register anpassen
                if register_type in ['int32', 'float32']:
                    count = count * 2
                
                _LOGGER.debug(f"Reading {count} registers starting at {start_register}")
                
                # Versuche zuerst die Holding-Register zu lesen
                try:
                    result = await self.hass.async_add_executor_job(
                        lambda: self._client.read_holding_registers(address=start_register, count=count, slave=self.config.slave_id)
                    )
                    _LOGGER.debug(f"Holding registers response for {start_register}: {result.registers}")
                except Exception as e:
                    _LOGGER.debug(f"Failed to read holding registers, trying input registers: {e}")
                    result = await self.hass.async_add_executor_job(
                        lambda: self._client.read_input_registers(address=start_register, count=count, slave=self.config.slave_id)
                    )
                    _LOGGER.debug(f"Input registers response for {start_register}: {result.registers}")
                
                if result.isError():
                    _LOGGER.error(f"Error reading registers starting at {start_register}: {result}")
                    continue
                    
                if not result.registers:
                    _LOGGER.error(f"No registers returned for address {start_register}")
                    continue
                
                # Erstelle einen Decoder mit der korrekten Byte-Reihenfolge
                decoder = BinaryPayloadDecoder.fromRegisters(
                    result.registers,
                    byteorder=Endian.BIG,
                    wordorder=Endian.BIG
                )
                
                for register in chunk:
                    try:
                        if register_type == 'int16':
                            value = decoder.decode_16bit_int()
                            _LOGGER.debug(f"Decoded int16 value for register {register}: {value}")
                            values[register] = value
                        elif register_type == 'uint16':
                            value = decoder.decode_16bit_uint()
                            _LOGGER.debug(f"Decoded uint16 value for register {register}: {value}")
                            values[register] = value
                        elif register_type == 'int32':
                            value = decoder.decode_32bit_int()
                            _LOGGER.debug(f"Decoded int32 value for register {register}: {value}")
                            values[register] = value
                        elif register_type == 'float32':
                            value = decoder.decode_32bit_float()
                            _LOGGER.debug(f"Decoded float32 value for register {register}: {value}")
                            values[register] = value
                        else:
                            _LOGGER.error(f"Unsupported register type: {register_type}")
                            values[register] = None
                            
                    except Exception as e:
                        _LOGGER.error(f"Error decoding register {register}: {e}")
                        values[register] = None
                        
            except Exception as e:
                _LOGGER.error(f"Error processing chunk starting at {chunk[0]}: {e}")
                for register in chunk:
                    values[register] = None
                    
        return values

    def _read_register(self, register: int, count: int = 1) -> Any:
        """Lese ein einzelnes Register oder eine Gruppe von Registern."""
        try:
            # Versuche zuerst die Holding-Register zu lesen
            try:
                return self._client.read_holding_registers(register, count, slave=self.config.slave_id)
            except Exception as e:
                _LOGGER.debug(f"Failed to read holding register {register}, trying input register: {e}")
                # Wenn das fehlschlägt, versuche die Input-Register
                return self._client.read_input_registers(register, count, slave=self.config.slave_id)
        except Exception as e:
            _LOGGER.error(f"Error reading register {register}: {e}")
            raise

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
                    slave=self.config.slave_id
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
        return self._client.write_registers(register, payload, slave=self.config.slave_id, count=count)
