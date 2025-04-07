# Modbus Register der Lambda Wärmepumpen

## Übersicht

Diese Dokumentation listet alle von der Integration verarbeiteten Modbus-Register auf, gruppiert nach Gerätetyp und Funktion.

## Wärmepumpe

### Temperatur-Register
| Register | Beschreibung | Typ | Faktor | Einheit |
|----------|--------------|-----|--------|---------|
| 1004 | Vorlauftemperatur | int16 | 0.1 | °C |
| 1015 | Sollwert Vorlauftemperatur | int16 | 0.1 | °C |
| 1010 | Außentemperatur | int16 | 0.1 | °C |
| 1014 | Rücklauftemperatur | int16 | 0.1 | °C |
| 1022 | Verdampfertemperatur | int16 | 0.1 | °C |

### Betriebsmodus
| Register | Beschreibung | Typ | Werte |
|----------|--------------|-----|-------|
| 1003 | Betriebsmodus | int16 | 0: Aus, 1: Heizen, 2: Kühlen |

### Status-Register
| Register | Beschreibung | Typ | Werte |
|----------|--------------|-----|-------|
| 1001 | Betriebsstatus | int16 | 0: Aus, 1: Bereit, 2: Heizen, 3: Kühlen |
| 1002 | Fehlercode | int16 | Siehe Fehlercode-Tabelle |

## Boiler

### Temperatur-Register
| Register | Beschreibung | Typ | Faktor | Einheit | Bereich |
|----------|--------------|-----|--------|---------|---------|
| 2002 | Ist-Temperatur | int16 | 0.1 | °C | 25-65°C |
| 2050 | Soll-Temperatur | int16 | 0.1 | °C | 25-65°C |

### Status-Register
| Register | Beschreibung | Typ | Werte |
|----------|--------------|-----|-------|
| 2001 | Betriebsstatus | int16 | 0: Aus, 1: Bereit, 2: Heizen |
| 2003 | Fehlercode | int16 | Siehe Fehlercode-Tabelle |

## Pufferspeicher

### Temperatur-Register
| Register | Beschreibung | Typ | Faktor | Einheit | Bereich |
|----------|--------------|-----|--------|---------|---------|
| 3002 | Ist-Temperatur | int16 | 0.1 | °C | 30-80°C |
| 3050 | Soll-Temperatur | int16 | 0.1 | °C | 30-80°C |

### Status-Register
| Register | Beschreibung | Typ | Werte |
|----------|--------------|-----|-------|
| 3001 | Betriebsstatus | int16 | 0: Aus, 1: Bereit, 2: Heizen |
| 3003 | Fehlercode | int16 | Siehe Fehlercode-Tabelle |

## System-Register

### Allgemeine Informationen
| Register | Beschreibung | Typ | Format |
|----------|--------------|-----|--------|
| 5001 | Seriennummer | int32 | - |
| 5006 | Firmware-Version | int16 | x.y |
| 5052 | Gerätetyp | int16 | - |

## Fehlercodes

### Wärmepumpe (Register 1002)
| Code | Beschreibung |
|------|--------------|
| 0 | Kein Fehler |
| 1 | Hochdruck |
| 2 | Niederdruck |
| 3 | Verdampferfrost |
| 4 | Überhitzung |

### Boiler (Register 2003)
| Code | Beschreibung |
|------|--------------|
| 0 | Kein Fehler |
| 1 | Temperatursensor |
| 2 | Überhitzung |
| 3 | Niedriger Wasserstand |

### Pufferspeicher (Register 3003)
| Code | Beschreibung |
|------|--------------|
| 0 | Kein Fehler |
| 1 | Temperatursensor |
| 2 | Überhitzung |
| 3 | Niedriger Wasserstand |

## Hinweise

1. **Temperaturfaktoren**
   - Alle Temperaturen werden mit einem Faktor von 0.1 multipliziert
   - Beispiel: Register-Wert 250 = 25.0°C

2. **Register-Typen**
   - int16: 16-Bit Ganzzahl mit Vorzeichen (-32768 bis 32767)
   - int32: 32-Bit Ganzzahl mit Vorzeichen
   - float32: 32-Bit Gleitkommazahl

3. **Schreibzugriff**
   - Nur Soll-Temperaturen sind schreibbar
   - Alle anderen Register sind nur lesbar 