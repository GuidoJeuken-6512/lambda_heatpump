# Modbus Register der Lambda Wärmepumpen

## Übersicht

Diese Dokumentation listet alle von der Integration verarbeiteten Modbus-Register auf, gruppiert nach Gerätetyp und Funktion.

## Allgemeine Umgebungsregister

### Status-Register
| Register | Beschreibung | Typ | Faktor | Einheit |
|----------|--------------|-----|--------|---------|
| 0 | Fehlernummer | int16 | 1 | - |
| 1 | Betriebsstatus | uint16 | 1 | - |
| 2 | Aktuelle Umgebungstemperatur | int16 | 0.1 | °C |
| 3 | Durchschnittliche Umgebungstemperatur (1h) | int16 | 0.1 | °C |
| 4 | Berechnete Umgebungstemperatur | int16 | 0.1 | °C |

## E-Manager

### Status-Register
| Register | Beschreibung | Typ | Faktor | Einheit |
|----------|--------------|-----|--------|---------|
| 100 | Fehlernummer | int16 | 1 | - |
| 101 | Betriebsstatus | uint16 | 1 | - |
| 102 | Aktuelle Leistungsaufnahme | int16 | 1 | W |
| 103 | Aktueller Stromverbrauch | int16 | 1 | W |
| 104 | Sollwert Stromverbrauch | int16 | 1 | W |

## Wärmepumpe 1

### Temperatur-Register
| Register | Beschreibung | Typ | Faktor | Einheit |
|----------|--------------|-----|--------|---------|
| 1004 | Vorlauftemperatur | int16 | 0.1 | °C |
| 1005 | Rücklauftemperatur | int16 | 0.1 | °C |
| 1006 | Vorlauf Wärmesenke | int16 | 0.1 | °C |
| 1007 | Eintrittstemperatur Wärmequelle | int16 | 0.1 | °C |
| 1008 | Austrittstemperatur Wärmequelle | int16 | 0.1 | °C |
| 1009 | Volumenstrom Wärmequelle | int16 | 1 | l/h |

### Leistungs-Register
| Register | Beschreibung | Typ | Faktor | Einheit |
|----------|--------------|-----|--------|---------|
| 1010 | Verdichterleistung | int16 | 1 | % |
| 1011 | Aktuelle Heizleistung | int16 | 1 | kW |
| 1012 | Frequenzumrichter Leistungsaufnahme | int16 | 1 | W |
| 1013 | Leistungszahl (COP) | int16 | 0.1 | - |

### Status-Register
| Register | Beschreibung | Typ | Werte |
|----------|--------------|-----|-------|
| 1000 | Fehlerstatus | int16 | - |
| 1001 | Fehlernummer | int16 | - |
| 1002 | Status | uint16 | - |
| 1003 | Betriebsstatus | uint16 | 0: Aus, 1: Heizen, 2: Kühlen |
| 1019 | Relais-Status 2. Heizstufe | uint16 | 0: Aus, 1: Ein |

### Energie-Register
| Register | Beschreibung | Typ | Faktor | Einheit |
|----------|--------------|-----|--------|---------|
| 1020 | Kumulierter Stromverbrauch | int32 | 1 | kWh |
| 1022 | Kumulierte Wärmeabgabe | int32 | 1 | kWh |

## Boiler 1

### Temperatur-Register
| Register | Beschreibung | Typ | Faktor | Einheit | Bereich |
|----------|--------------|-----|--------|---------|---------|
| 2002 | Ist-Temperatur Boiler Hoch | int16 | 0.1 | °C | 25-65°C |
| 2003 | Ist-Temperatur Boiler Tief | int16 | 0.1 | °C | 25-65°C |
| 2050 | Soll-Temperatur | int16 | 0.1 | °C | 25-65°C |

### Status-Register
| Register | Beschreibung | Typ | Werte |
|----------|--------------|-----|-------|
| 2000 | Fehlernummer | int16 | - |
| 2001 | Betriebsstatus | uint16 | 0: Aus, 1: Bereit, 2: Heizen |

## Pufferspeicher 1

### Temperatur-Register
| Register | Beschreibung | Typ | Faktor | Einheit | Bereich |
|----------|--------------|-----|--------|---------|---------|
| 3002 | Ist-Temperatur Puffer Hoch | int16 | 0.1 | °C | 30-80°C |
| 3003 | Ist-Temperatur Puffer Tief | int16 | 0.1 | °C | 30-80°C |
| 3050 | Soll-Temperatur | int16 | 0.1 | °C | 30-80°C |

### Status-Register
| Register | Beschreibung | Typ | Werte |
|----------|--------------|-----|-------|
| 3000 | Fehlernummer | int16 | - |
| 3001 | Betriebsstatus | uint16 | 0: Aus, 1: Bereit, 2: Heizen |

## Solar 1

### Temperatur-Register
| Register | Beschreibung | Typ | Faktor | Einheit |
|----------|--------------|-----|--------|---------|
| 4002 | Ist-Temperatur Kollektor | int16 | 0.1 | °C |
| 4003 | Ist-Temperatur Puffer 1 | int16 | 0.1 | °C |
| 4004 | Ist-Temperatur Puffer 2 | int16 | 0.1 | °C |
| 4050 | Soll-Temperatur Puffer | int16 | 0.1 | °C |
| 4051 | Umschalttemperatur Puffer | int16 | 0.1 | °C |

### Status-Register
| Register | Beschreibung | Typ | Werte |
|----------|--------------|-----|-------|
| 4000 | Fehlernummer | int16 | - |
| 4001 | Betriebsstatus | uint16 | - |

## Heizkreis 1

### Temperatur-Register
| Register | Beschreibung | Typ | Faktor | Einheit |
|----------|--------------|-----|--------|---------|
| 5002 | Ist-Temperatur Vorlauf | int16 | 0.1 | °C |
| 5003 | Ist-Temperatur Rücklauf | int16 | 0.1 | °C |
| 5004 | Ist-Temperatur Raumgerät | int16 | 0.1 | °C |
| 5005 | Soll-Temperatur Vorlauf | int16 | 0.1 | °C |
| 5050 | Sollwert-Vorlauf-Temperatur-Offset | int16 | 0.1 | °C |
| 5051 | Soll-Temperatur Raum Heizbetrieb | int16 | 0.1 | °C |
| 5052 | Soll-Temperatur Raum Kühlbetrieb | int16 | 0.1 | °C |

### Status-Register
| Register | Beschreibung | Typ | Werte |
|----------|--------------|-----|-------|
| 5000 | Fehlernummer | int16 | - |
| 5001 | Betriebsstatus | uint16 | - |
| 5006 | Betriebsmodus | uint16 | - |

## Hinweise

1. **Temperaturfaktoren**
   - Alle Temperaturen werden mit einem Faktor von 0.1 multipliziert
   - Beispiel: Register-Wert 250 = 25.0°C

2. **Register-Typen**
   - int16: 16-Bit Ganzzahl mit Vorzeichen (-32768 bis 32767)
   - int32: 32-Bit Ganzzahl mit Vorzeichen
   - uint16: 16-Bit Ganzzahl ohne Vorzeichen (0 bis 65535)

3. **Schreibzugriff**
   - Nur Soll-Temperaturen sind schreibbar
   - Alle anderen Register sind nur lesbar

4. **Klimasteuerung**
   - Boiler 1:
     - Temperaturregister: 2002
     - Sollwertregister: 2050
     - Max. Temperatur: 60°C
     - Min. Temperatur: 40°C
     - Genauigkeit: 1°C
     - Skalierung: 0.1
     - Einheit: °C

   - Heizkreis 1:
     - Raumtemperaturregister: 5004
     - Sollwertregister: 5051
     - Max. Temperatur: 35°C
     - Min. Temperatur: 15°C
     - Genauigkeit: 1°C
     - Skalierung: 0.1
     - Einheit: °C 