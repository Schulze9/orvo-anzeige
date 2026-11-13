# ORVO Eingangsanzeige

Anzeigeseite für den Fernseher im Eingangsbereich des Oldenburger Rudervereins (ORVO), gedacht für Yodeck („Web Page“).

- **Bilderstrecke:** Fotos aus den letzten Beiträgen auf orvo.de
- **Termine:** ORVO-Kalender (My Calendar, `/wp-json/my-calendar/v1/events`)
- **Wetter:** Open-Meteo
- **Wasser:** Pegelonline (Wassertemperatur Weser/Elsfleth, Pegel Hunte/Oldenburg-Drielake)
- **Ruderzeit:** bürgerliche Dämmerung, im Browser berechnet

Eine einzelne Datei (`index.html`), keine Server-Abhängigkeiten. Einstellungen stehen oben im Skript (`CFG`).
URL-Parameter: `?slide=12` (Sekunden pro Bild).

**Ausführliche Dokumentation:** [docs/DOKUMENTATION.md](docs/DOKUMENTATION.md)

**Live:** https://schulze9.github.io/orvo-anzeige/
