# Lambda Wärmepumpen Integration für Home Assistant

Diese Integration ermöglicht die Steuerung und Überwachung von Lambda Wärmepumpen über Home Assistant.

## Funktionen

- Anzeige und Steuerung von Temperaturen für verschiedene Gerätetypen:
  - Wärmepumpen
  - Boiler
  - Pufferspeicher
- Unterstützung für verschiedene Betriebsmodi:
  - Heizen
  - Kühlen (bei unterstützten Geräten)
  - Automatik (bei unterstützten Geräten)
- Echtzeit-Temperaturüberwachung
- Konfigurierbare Temperaturgrenzen und Schrittweiten

## Installation

1. Kopieren Sie den `lambda_wp` Ordner in das `custom_components` Verzeichnis Ihrer Home Assistant Installation
2. Starten Sie Home Assistant neu
3. Fügen Sie die Integration über die Benutzeroberfläche hinzu:
   - Gehen Sie zu Einstellungen > Geräte & Dienste
   - Klicken Sie auf "+ Integration hinzufügen"
   - Suchen Sie nach "Lambda Wärmepumpe"

## Konfiguration

### Erforderliche Parameter

- **Host**: IP-Adresse oder Hostname der Wärmepumpe
- **Port**: Modbus TCP Port (Standard: 502)
- **Slave ID**: Modbus Slave ID (Standard: 1)
- **Anzahl der Boiler**: Anzahl der angeschlossenen Boiler
- **Anzahl der Wärmepumpen**: Anzahl der angeschlossenen Wärmepumpen
- **Anzahl der Pufferspeicher**: Anzahl der angeschlossenen Pufferspeicher

### Optionale Parameter

- **Name**: Benutzerdefinierter Name für die Integration
- **Scan Intervall**: Aktualisierungsintervall in Sekunden (Standard: 30)

## Gerätetypen und Register

### Boiler
- Temperatur-Register: 2002
- Sollwert-Register: 2050
- Temperaturbereich: 25°C - 65°C
- Schrittweite: 0.5°C

### Wärmepumpe
- Temperatur-Register: 1004
- Sollwert-Register: 1015
- Betriebsmodus-Register: 1003
- Unterstützt Heizen und Kühlen

### Pufferspeicher
- Temperatur-Register: 3002
- Sollwert-Register: 3050
- Temperaturbereich: 30°C - 80°C

## Register-Konfiguration

### Temperatur-Register
- Register 1004 (Flowline Temperatur): Faktor 0.01, Einheit °C
- Register 2002 (Boiler High Sensor): Faktor 0.1, Einheit °C
- Register 2003 (Boiler Low Sensor): Faktor 0.1, Einheit °C

### Volumenstrom-Register
- Register 1006 (Flow Heat Sink): Faktor 0.01, Einheit m³/h

## Fehlerbehebung

### Häufige Probleme

1. **Keine Verbindung zur Wärmepumpe**
   - Überprüfen Sie die Netzwerkverbindung
   - Stellen Sie sicher, dass der Modbus TCP Port erreichbar ist
   - Überprüfen Sie die Slave ID

2. **Fehlende Temperaturwerte**
   - Überprüfen Sie die Register-Adressen
   - Stellen Sie sicher, dass die Geräte korrekt konfiguriert sind
   - Überprüfen Sie die Logs auf Dekodierungsfehler

3. **Falsche Temperaturwerte**
   - Überprüfen Sie den Faktor in der Konfiguration
   - Stellen Sie sicher, dass der korrekte Register-Typ verwendet wird

### Logging

Die Integration protokolliert detaillierte Informationen im Home Assistant Log. Aktivieren Sie das Debug-Logging für die Komponente `lambda_wp`, um weitere Details zu erhalten:

```yaml
logger:
  default: info
  logs:
    custom_components.lambda_wp: debug
```

## Unterstützung

Bei Fragen oder Problemen können Sie ein Issue im GitHub Repository erstellen.

## Lizenz

Diese Integration ist unter der MIT-Lizenz lizenziert.