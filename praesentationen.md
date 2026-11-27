# Fähigkeit: Präsentationen

Du baust aus einer Markdown-Datei eine Präsentation als HTML-Datei. Die Folien haben ein festes 16:9-Format, man blättert mit den Pfeiltasten.

## Ablauf
1. Frage nach Thema, Zielgruppe, Anlass und Umfang. Schlage eine Folienstruktur vor und lass sie bestätigen.
2. Schreibe die Markdown-Datei nach `decks/<name>/praesentation.md` (Format unten).
3. Baue: `python3 build.py decks/<name>/praesentation.md decks/<name>/index.html`
4. Prüfe die Meldung des Generators: Die Zahl der Folien muss zur geplanten Zahl passen. Stimmt sie nicht, ist die Markdown-Datei falsch aufgebaut (siehe Format).
5. Gib `index.html` an die Nutzerin zurück.
6. Änderungswünsche: Markdown anpassen, neu bauen. Nie das HTML von Hand ändern.

## Format der Markdown-Datei
Die Datei beginnt mit einem Titel-Block. Danach folgt pro Folie genau ein Block: eine Zeile `---`, dann die YAML-Felder, dann eine Zeile `---`. Zwischen den Blöcken steht eine Leerzeile.

Schreibe außerhalb der Blöcke keinen weiteren Text und keine Kommentarzeilen (zum Beispiel kein `# FOLIE 2`). Der Generator zählt alles, was nicht in einem Block steht, als eigene Folie. Willst du etwas notieren, schreibe es als `#`-Zeile innerhalb des Blocks vor dem schließenden `---`.

```
---
title: "Mein erster Vortrag"
---

---
layout: title
headline: "Ein Beispiel für one.design"
highlight: "Beispiel"
subline: "So sieht eine Präsentation aus"
illustration: "beispiel.png"
---

---
layout: wide_photos
headline: "Wenig Text, viel Luft"
highlight: "Luft"
intro: "Jede Folie hat eine klare Aussage."
image_position: right
photos:
  - path: "luft.png"
    rotate: -2
---
```

Layouts (`layout:`) und ihre Felder:
- `title`: headline, subline, illustration, highlight, optional cta_link + cta_text. Für Titel-, Kapitel-, Umfrage- und Schlussfolien.
- `wide_photos`: headline, intro, image_position (left/right), photos (Liste mit path und rotate), highlight.
- `chart_text`: headline, number (große Zahl), subtext, chart_image, chart_position (left/right), highlight.
- `three_columns`: headline, columns (Liste mit title, icon, items), highlight.
- `team_grid`: headline, illustration, people (Liste mit image, name, title), highlight.
- Auf jeder Folie möglich: badge (Text neben dem Kreis unten rechts, Standard "All Hands 2026"), qr_code (URL).

## Bilder
Bilder werden nur mit dem Dateinamen angegeben (zum Beispiel `kaffee.png`) und liegen im Ordner `assets/`. Fehlt eine Datei, setzt der Generator automatisch einen Platzhalter ein. Die Präsentation lässt sich also immer bauen. Sag der Nutzerin, wenn noch Platzhalter drin sind.

## Regeln für Präsentationen
- Pro Folie genau ein Schlüsselwort als `highlight`, wörtlich wie in der Überschrift. Es bekommt den Kreidestrich.
- Überschriften kurz, möglichst zwei Zeilen.
- Umfragefolien schlicht: Überschrift und nur die Frage, keine Anleitung.
- Dramaturgie für Vorträge: Hook mit Wiedererkennung, These, Bruch, Auflösung, Praxis, ein Merksatz zum Schluss. Live-Umfragen einplanen.
- Das Badge unten rechts und die Foliennummer unten links setzt der Generator automatisch. Auf der ersten Folie fehlen beide.
