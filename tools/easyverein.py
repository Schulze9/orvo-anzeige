#!/usr/bin/env python3
"""Holt den ORVO-Kalender aus easyVerein (ICS-Abo) und schreibt events.json für die Anzeige.

Die Abo-Adresse enthält einen geheimen Schlüssel und kommt deshalb aus der
Umgebungsvariablen EASYVEREIN_ICS (in GitHub als Repository-Secret hinterlegt).

Übernommen werden nur Titel, Beginn, Ende und Kalendername – keine Beschreibungen,
denn die enthalten Telefonnummern, E-Mail-Adressen und Kontodaten.

Aufruf:  EASYVEREIN_ICS=https://… python3 tools/easyverein.py events.json
"""
import json, os, re, sys, urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Berlin")
DAYS_AHEAD = 180

# Kalender, die nur eine Fahrzeug- oder Raumbuchung zu einer Veranstaltung sind.
# Sie werden als kurzer Hinweis am Termin angezeigt, nicht als eigene Kategorie.
RESOURCES = {
    "Bus": "Bus",
    "Anhänger groß": "Hänger groß",
    "Anhänger mittel": "Hänger mittel",
    "Anhänger klein": "Hänger klein",
    "Clubraum": "Clubraum",
}
SKIP = {"Vorstand"}                       # interne Kalender nicht anzeigen
COLORS = {
    "Wanderfahrten": "#2f66f5",
    "Regatten - Breitensport": "#cc253f",
    "Regatten - Rennrudern": "#cc253f",
    "Vereinstermine": "#ffc65c",
    "Trainingszeiten": "#4fc3e8",
}


def unfold(text):
    return re.sub(r"\r?\n[ \t]", "", text).replace("\r", "")


def unescape(v):
    return re.sub(r"\\([\\;,nN])", lambda m: "\n" if m.group(1) in "nN" else m.group(1), v)


def parse_dt(prop, value):
    """liefert (datetime in Europe/Berlin, ganztägig?)"""
    if "VALUE=DATE" in prop or re.fullmatch(r"\d{8}", value):
        return datetime.strptime(value[:8], "%Y%m%d").replace(tzinfo=TZ), True
    dt = datetime.strptime(value[:15], "%Y%m%dT%H%M%S")
    if value.endswith("Z"):
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        m = re.search(r"TZID=([^;:]+)", prop)
        dt = dt.replace(tzinfo=ZoneInfo(m.group(1)) if m else TZ)
    return dt.astimezone(TZ), False


def events(ics):
    for block in unfold(ics).split("BEGIN:VEVENT")[1:]:
        block = block.split("END:VEVENT")[0]
        props = {}
        for line in block.split("\n"):
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            name = k.split(";")[0].upper()
            props.setdefault(name, (k, v.strip()))
        if "DTSTART" not in props or "SUMMARY" not in props:
            continue
        if props.get("STATUS", ("", ""))[1].upper() == "CANCELLED":
            continue
        start, all_day = parse_dt(*props["DTSTART"])
        if "DTEND" in props:
            end, _ = parse_dt(*props["DTEND"])
            if all_day:                           # DTEND ist bei ganztägigen Terminen exklusiv
                end = end - timedelta(seconds=1)
        else:
            end = start + (timedelta(days=1, seconds=-1) if all_day else timedelta(hours=1))
        yield {
            "title": unescape(props["SUMMARY"][1]).strip(),
            "cal": unescape(props.get("CLASSIFICATION", ("", ""))[1]).strip(),
            "start": start, "end": end, "allDay": all_day,
        }


def clean_title(t):
    # „Midwinter (mittlerer Hänger)“ -> „Midwinter“
    return re.sub(r"\s*\((?:[^()]*\b(?:Hänger|Anhänger|Bus)\b[^()]*)\)\s*$", "", t, flags=re.I).strip()


def build(ics, today=None):
    today = today or datetime.now(TZ).date()
    horizon = today + timedelta(days=DAYS_AHEAD)
    merged = {}
    for e in events(ics):
        # easyVerein speichert manche Tagestermine als 00:00 UTC (= 01:00 Uhr) bis 23:59
        if not e["allDay"] and e["start"].hour <= 1 and e["start"].minute == 0 and e["end"].strftime("%H:%M") >= "23:59":
            e["allDay"] = True
            e["start"] = e["start"].replace(hour=0)
        if e["cal"] in SKIP or e["end"].date() < today or e["start"].date() > horizon:
            continue
        title = re.sub(r"\s+", " ", clean_title(e["title"]) or e["title"])
        key = (e["start"].date(), re.sub(r"\W+", "", title.lower()))
        m = merged.setdefault(key, {"title": title, "start": e["start"], "end": e["end"],
                                    "allDay": e["allDay"], "cats": [], "res": []})
        m["start"], m["end"] = min(m["start"], e["start"]), max(m["end"], e["end"])
        m["allDay"] = m["allDay"] and e["allDay"]
        if e["cal"] in RESOURCES:
            if RESOURCES[e["cal"]] not in m["res"]:
                m["res"].append(RESOURCES[e["cal"]])
        elif e["cal"] and e["cal"] != "None" and e["cal"] not in m["cats"]:
            m["cats"].append(e["cal"])
    out = []
    for m in sorted(merged.values(), key=lambda m: (m["start"], m["title"])):
        cat = m["cats"][0] if m["cats"] else ""
        out.append({
            "title": m["title"],
            "begin": m["start"].strftime("%Y-%m-%d %H:%M:%S"),
            "end": m["end"].strftime("%Y-%m-%d %H:%M:%S"),
            "allDay": m["allDay"],
            "cat": cat,
            "res": m["res"],
            "color": COLORS.get(cat, ""),
        })
    return out


def main():
    url = os.environ.get("EASYVEREIN_ICS", "").strip()
    target = sys.argv[1] if len(sys.argv) > 1 else "events.json"
    if not url:
        sys.exit("EASYVEREIN_ICS ist nicht gesetzt")
    req = urllib.request.Request(url, headers={"User-Agent": "ORVO-Anzeige"})
    ics = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    if "BEGIN:VCALENDAR" not in ics:
        sys.exit("Antwort ist kein Kalender – Abo-Adresse prüfen")
    data = {"source": "easyVerein", "events": build(ics)}
    with open(target, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(data['events'])} Termine -> {target}")


if __name__ == "__main__":
    main()
