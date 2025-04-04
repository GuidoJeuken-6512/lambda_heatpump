This is a custom component for Home Assistant to connect to Lambda Heatpumps using modbus.

The integration is based on that provided by Bany. https://github.com/bany08/hacs_lambda_heatpumps 
The basic functions work, but there is still some work to do 
- Config flow doesn't change the initial config correctly 
- Second climate sensor for room thermostat 
- Modbus polling interval via config_flow 
- Modbus registers depending on firmware.