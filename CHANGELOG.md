# Changelog

## [1.0.0] - 2024-03-19

### Hinzugefügt
- Initiale Version der Lambda Wärmepumpen Integration
- Unterstützung für Boiler, Wärmepumpen und Pufferspeicher
- Konfigurierbare Temperaturgrenzen und Schrittweiten
- Modbus TCP Kommunikation
- Automatische Register-Dekodierung

### Geändert
- Verbesserte Fehlerbehandlung bei der Register-Dekodierung
- Angepasste Temperaturbereiche für verschiedene Gerätetypen
- Optimierte Modbus-Kommunikation

### Behoben
- Korrektur der Register-Dekodierung für verschiedene Datentypen
- Behebung von Problemen mit der Temperaturanzeige
- Verbesserung der Stabilität der Modbus-Kommunikation

## [Unreleased]

### Changed
- Korrigierte Faktoren für Temperatur-Register:
  - Register 1004 (Flowline Temperatur) auf 0.01
  - Register 2002 (Boiler High Sensor) auf 0.1
  - Register 2003 (Boiler Low Sensor) auf 0.1
- Verbesserte Modbus-Kommunikation für Register 2002 und 2003
- Hinzugefügte Debug-Ausgaben für bessere Fehlersuche

### Fixed
- Korrekte Temperaturwerte für Boiler-Sensoren
- Stabile Werte für Flowline-Temperatur 