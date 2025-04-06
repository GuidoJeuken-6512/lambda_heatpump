# Modbus Funktionen der Lambda Wärmepumpen Integration

## Übersicht

Diese Integration nutzt Modbus TCP zur Kommunikation mit Lambda Wärmepumpen. Die folgenden Funktionen werden implementiert:

### Lesen von Registern

1. **Einzelne Register lesen**
   - Funktion: `_read_register`
   - Beschreibung: Liest ein einzelnes Register oder eine Gruppe von Registern
   - Parameter:
     - `register`: Register-Adresse
     - `count`: Anzahl der zu lesenden Register
   - Rückgabewert: Dekodierter Register-Wert

2. **Gruppierte Register lesen**
   - Funktion: `_read_grouped_registers`
   - Beschreibung: Liest mehrere Register effizient in Chunks
   - Parameter:
     - `registers`: Liste der Register-Adressen
     - `register_type`: Datentyp der Register (int16, uint16, int32, float32)
   - Rückgabewert: Dictionary mit Register-Adressen und Werten

### Schreiben in Register

1. **Einzelnes Register schreiben**
   - Funktion: `async_write_register`
   - Beschreibung: Schreibt einen Wert in ein Register
   - Parameter:
     - `register`: Register-Adresse
     - `value`: Zu schreibender Wert
     - `register_type`: Datentyp des Registers

### Fehlerbehandlung

1. **Register-Dekodierung**
   - Unterstützte Datentypen:
     - int16: 16-Bit Ganzzahl mit Vorzeichen
     - uint16: 16-Bit Ganzzahl ohne Vorzeichen
     - int32: 32-Bit Ganzzahl mit Vorzeichen
     - float32: 32-Bit Gleitkommazahl

2. **Fehlerprotokollierung**
   - Detaillierte Logging-Informationen
   - Fehlerbehandlung für:
     - Verbindungsfehler
     - Dekodierungsfehler
     - Ungültige Register-Adressen

### Optimierungen

1. **Chunk-Verarbeitung**
   - Automatische Aufteilung großer Register-Gruppen
   - Konfigurierbare Chunk-Größe
   - Effiziente Verarbeitung sequentieller Register

2. **Caching**
   - Zwischenspeicherung von Register-Werten
   - Reduzierung der Modbus-Anfragen
   - Konfigurierbares Aktualisierungsintervall

## Beispiel-Code

```python
# Einzelnes Register lesen
value = await coordinator._read_register(2002)

# Mehrere Register lesen
values = await coordinator._read_grouped_registers([2002, 2003, 2004], 'int16')

# Register schreiben
await coordinator.async_write_register(2050, 45, 'int16')
```

## Fehlerbehebung

### Häufige Fehler

1. **Modbus Exception 131**
   - Ursache: Ungültige Register-Adresse
   - Lösung: Überprüfen Sie die Register-Adressen in der Dokumentation

2. **Dekodierungsfehler**
   - Ursache: Falscher Datentyp oder ungültige Daten
   - Lösung: Überprüfen Sie den register_type Parameter

3. **Verbindungsfehler**
   - Ursache: Netzwerkprobleme oder falsche Konfiguration
   - Lösung: Überprüfen Sie Host, Port und Slave ID 