# Modbus Funktionen der Lambda Wärmepumpen

## Übersicht

Diese Dokumentation beschreibt die von der Integration genutzten Modbus-Funktionen und deren Verwendung.

## Lesen von Registern

### Funktion 3: Holding Register lesen
- **Beschreibung**: Liest Holding Register (4xxxx)
- **Verwendung**: 
  - Lesen von Sollwerten
  - Lesen von Konfigurationsparametern
  - Lesen von Systeminformationen

### Funktion 4: Input Register lesen
- **Beschreibung**: Liest Input Register (1xxxx, 2xxxx, 3xxxx)
- **Verwendung**:
  - Lesen von Istwerten
  - Lesen von Statusinformationen
  - Lesen von Fehlercodes

## Schreiben in Register

### Funktion 6: Einzelnes Holding Register schreiben
- **Beschreibung**: Schreibt einen einzelnen Wert in ein Holding Register
- **Verwendung**:
  - Setzen von Sollwerten
  - Ändern von Konfigurationsparametern
  - Steuern von Betriebsmodi

### Funktion 16: Mehrere Holding Register schreiben
- **Beschreibung**: Schreibt mehrere Werte in Holding Register
- **Verwendung**:
  - Setzen mehrerer Sollwerte gleichzeitig
  - Konfiguration mehrerer Parameter

## Fehlerbehandlung

### Modbus-Exception Codes
| Code | Beschreibung | Bedeutung |
|------|--------------|-----------|
| 1 | Illegal Function | Nicht unterstützte Funktion |
| 2 | Illegal Data Address | Ungültige Registeradresse |
| 3 | Illegal Data Value | Ungültiger Datenwert |
| 4 | Slave Device Failure | Gerätefehler |

### Fehlerbehandlung in der Integration
- **Wiederholungsversuche**: Automatische Wiederholung bei Kommunikationsfehlern
- **Timeout**: 3 Sekunden pro Registerzugriff
- **Logging**: Detaillierte Fehlerprotokolle für Diagnose

## Register-Adressierung

### Adressbereiche
- **Input Register**: 1000-3999
- **Holding Register**: 4000-4999
- **System Register**: 5000-5999

### Adresskonvertierung
- **1-basierte Adressierung**: Registeradressen beginnen bei 1
- **0-basierte Adressierung**: Modbus-Adressen beginnen bei 0
- **Konvertierung**: Registeradresse - 1 = Modbus-Adresse

## Best Practices

1. **Lesen von Registern**
   - Gruppieren verwandter Register
   - Minimale Anzahl von Lesevorgängen
   - Cache-Strategie für häufig gelesene Werte

2. **Schreiben in Register**
   - Validierung von Werten vor dem Schreiben
   - Bestätigung nach dem Schreiben
   - Fehlerbehandlung bei Schreibfehlern

3. **Fehlerbehandlung**
   - Logging aller Fehler
   - Automatische Wiederholung bei temporären Fehlern
   - Benachrichtigung bei kritischen Fehlern

4. **Performance**
   - Minimale Anzahl von Modbus-Anfragen
   - Optimale Gruppierung von Registern
   - Cache-Strategie für häufig gelesene Werte

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