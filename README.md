# ORVO Eingangsanzeige

Anzeigeseite für den Fernseher im Eingangsbereich des Oldenburger Rudervereins (ORVO), gedacht für Yodeck („Web Page“).

- **Bilderstrecke:** Fotos aus den letzten Beiträgen auf orvo.de
- **Termine:** Vereinskalender aus easyVerein; eine GitHub Action überträgt sie alle 30 Minuten nach `events.json` (Abo-Adresse als Secret `EASYVEREIN_ICS`)
- **Wetter:** Open-Meteo
- **Wasser:** Pegelonline (Wassertemperatur Weser/Elsfleth, Pegel Hunte/Oldenburg-Drielake)
- **Ruderzeit:** bürgerliche Dämmerung, im Browser berechnet

Die Seite ist eine einzelne Datei (`index.html`) ohne Server. Einstellungen stehen oben im Skript (`CFG`).
URL-Parameter: `?slide=12` (Sekunden pro Bild).

**Ausführliche Dokumentation:** [docs/DOKUMENTATION.md](docs/DOKUMENTATION.md)

**Live:** https://schulze9.github.io/orvo-anzeige/
