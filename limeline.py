#!/usr/bin/env python3
"""
one.design – Anbindung an One Intelligence (Open WebUI) für Illustrationen im Stil "one lime line".

Nur Standardbibliothek, läuft mit python3 ohne Installation.

Die beiden Prompt-Vorlagen sind die Fassungen, die das Modell "one lime line" aus dem
Stil-Prompt macht (Standard und Badge). Pro Folie ändert sich nur die Motiv-Beschreibung.

Test auf dem eigenen Rechner (Schlüssel wird nie ausgegeben oder gespeichert):

    read -s OI_API_KEY; export OI_API_KEY      # Schlüssel unsichtbar eingeben, Enter
    python3 limeline.py --test                 # direkte Bildschnittstelle, Beispiel "Köln"
    python3 limeline.py --models               # Modelle auflisten (für den Chat-Weg)
    python3 limeline.py --test --chat MODELL-ID   # zusätzlich über das Modell im Chat versuchen

Einstellungen über Umgebungsvariablen:
    OI_API_KEY   API-Schlüssel (Pflicht)
    OI_BASE_URL  Standard: https://oi.destination.one
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = os.environ.get("OI_BASE_URL", "https://oi.destination.one").rstrip("/")

# ---------------------------------------------------------------------------
# Prompt-Vorlagen (wortgleich aus den Ergebnissen von "one lime line" übernommen)
# ---------------------------------------------------------------------------

STANDARD = (
    "A minimalist vector illustration of {motiv}, drawn in one single continuous black line (#000000). "
    "The line is deep black, smooth, monoline, clean vector continuous line art, starting from the left, "
    "forming the motif through elegant loops, and flowing out to the right with no loose ends. "
    "Behind the line, add a single organic abstract shape filled only with a linear gradient from "
    "Light Green (#a8db20) to Turquoise (#00cfc0). The color shape is slightly horizontally offset to the "
    "right behind the black line, creating a misregistered print / misprint effect. "
    "Pure white background (#FFFFFF), flat style, no shading, no texture, no sketch, no pencil look, no hatching."
)

BADGE = (
    "A minimalist vector badge. An imperfect organic circle filled with a linear gradient from "
    "Light Green (#a8db20) to Turquoise (#00cfc0). On top of the circle, drawn in one single continuous "
    "black line (#000000), is {motiv}, all formed by one uninterrupted smooth monoline vector line that "
    "begins on the left, creates the motif through loops, and exits to the right without open ends. "
    "The organic black line stays fully inside the circle and does not extend beyond it. "
    "Deep black, evenly thick, clean vector continuous line art, no sketch look, no pencil texture, "
    "no hatching. White background (#FFFFFF), flat style, no shading, no shadows, no texture."
)

VORLAGEN = {"standard": STANDARD, "badge": BADGE}


def compose_prompt(art: str, motiv: str) -> str:
    """Setzt die Motiv-Beschreibung (englisch, konkret zeichenbar) in die Vorlage ein."""
    art = art.strip().lower()
    if art not in VORLAGEN:
        raise ValueError(f"Unbekannte Bildart '{art}'. Erlaubt: {', '.join(VORLAGEN)}")
    return VORLAGEN[art].format(motiv=motiv.strip())


# Beispiele aus den Chat-Ergebnissen, damit der Test direkt vergleichbar ist
BEISPIEL = {
    "standard": "Cologne (Köln) represented by the Cologne Cathedral skyline and a subtle Rhine river curve",
    "badge": ("Cologne: the iconic Cologne Cathedral silhouette with twin spires, subtle cathedral arches, "
              "and a small flowing Rhine river curve"),
}

# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


def _key() -> str:
    key = os.environ.get("OI_API_KEY", "").strip()
    if not key:
        sys.exit("OI_API_KEY ist nicht gesetzt. Siehe Hinweis am Anfang der Datei.")
    return key


def _request(path: str, payload: dict | None = None, timeout: int = 180):
    """Gibt (Status, Bytes) zurück. Der Schlüssel erscheint nie in Ausgaben."""
    url = path if path.startswith("http") else BASE_URL + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data is not None else "GET")
    req.add_header("Authorization", f"Bearer {_key()}")
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # Netzwerk, Zertifikat, Zeitüberschreitung
        return 0, str(e).encode()


def _snippet(b: bytes, n: int = 400) -> str:
    return b.decode("utf-8", "replace")[:n].replace("\n", " ")


def list_models():
    status, body = _request("/api/models")
    print(f"GET /api/models -> {status}")
    if status == 200:
        for m in json.loads(body).get("data", []):
            print(f"  {m.get('id')}  |  {m.get('name')}")
    else:
        print(_snippet(body))


def generate_direct(art: str, motiv: str, out: Path) -> bool:
    """Weg 1: direkte Bildschnittstelle von Open WebUI, Prompt wird unverändert durchgereicht."""
    prompt = compose_prompt(art, motiv)
    status, body = _request("/api/v1/images/generations", {"prompt": prompt, "n": 1})
    print(f"POST /api/v1/images/generations ({art}) -> {status}")
    if status != 200:
        print("  Antwort:", _snippet(body))
        return False
    try:
        items = json.loads(body)
        url = items[0]["url"] if isinstance(items, list) else items["data"][0]["url"]
    except Exception:
        print("  Unerwartetes Antwortformat:", _snippet(body))
        return False
    st, img = _request(url)
    if st != 200:
        print(f"  Bild konnte nicht geladen werden ({st}):", _snippet(img))
        return False
    out.write_bytes(img)
    print(f"  gespeichert: {out} ({len(img)} Bytes)")
    return True


def generate_via_chat(model_id: str, art: str, motiv: str):
    """Weg 2 (Fallback): Prompt als Chat-Nachricht an das Modell, Bildgenerierung eingeschaltet."""
    prompt = compose_prompt(art, motiv)
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "features": {"image_generation": True},
        "stream": False,
    }
    status, body = _request("/api/chat/completions", payload)
    print(f"POST /api/chat/completions ({art}, Modell {model_id}) -> {status}")
    text = _snippet(body, 1200)
    print("  Antwort (Anfang):", text)
    urls = re.findall(r"(/cache/image/[^\s\)\"']+|https?://[^\s\)\"']+\.(?:png|jpg|webp))", body.decode("utf-8", "replace"))
    if urls:
        print("  Mögliche Bild-Adressen:", urls[:3])


def main(argv):
    if "--models" in argv:
        list_models()
        return
    if "--test" in argv:
        here = Path(__file__).resolve().parent
        print(f"Server: {BASE_URL}")
        status, body = _request("/api/version")
        print(f"GET /api/version -> {status} {_snippet(body, 120)}")
        if status == 0:
            sys.exit("Server nicht erreichbar (Netzwerk/VPN/Adresse prüfen).")
        for art in ("standard", "badge"):
            generate_direct(art, BEISPIEL[art], here / f"test-koeln-{art}.png")
        if "--chat" in argv:
            model = argv[argv.index("--chat") + 1]
            generate_via_chat(model, "standard", BEISPIEL["standard"])
        return
    print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
