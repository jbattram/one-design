# Fähigkeit: Präsentationen

Du baust aus einer Markdown-Datei eine Präsentation als HTML-Datei. Die Folien haben ein festes 16:9-Format, man blättert mit den Pfeiltasten.

## Ablauf
1. Frage nach Thema, Zielgruppe, Anlass und Umfang. Schlage eine Folienstruktur vor und lass sie bestätigen.
2. Schreibe die Markdown-Datei nach `decks/<name>/praesentation.md` (Format unten).
3. Baue: `python3 build.py decks/<name>/praesentation.md decks/<name>/index.html`
4. Gib `index.html` an die Nutzerin zurück.
5. Änderungswünsche: Markdown anpassen, neu bauen. Nie das HTML von Hand ändern.

## Format der Markdown-Datei
Die Datei beginnt mit dem Titel. Danach folgt pro Folie ein Block: `---`, dann YAML, dann `---`. Zwischen den Blöcken stehen Kommentarzeilen `# FOLIE n: Name`.

```
---
title: "All-Hands Dezember 2026"
---

---
layout: title
headline: "Vom Macher zum Kurator"
highlight: "Kurator"
subline: "All-Hands Dezember 2026"
illustration: "hands.png"
---
```

Layouts (`layout:`) und ihre Felder:
- `title`: headline, subline, illustration, highlight, optional cta_link + cta_text. Für Titel-, Kapitel-, Umfrage- und Schlussfolien.
- `wide_photos`: headline, intro, image_position (left/right), photos (Liste mit path und rotate), highlight.
- `chart_text`: headline, number (große Zahl), subtext, chart_image, chart_position (left/right), highlight.
- `three_columns`: headline, columns (Liste mit title, icon, items), highlight.
- `team_grid`: headline, illustration, people (Liste mit image, name, title), highlight.
- Auf jeder Folie möglich: badge (Text neben dem Kreis unten rechts, Standard "All Hands 2026"), qr_code (URL).

## Regeln für Präsentationen
- Pro Folie genau ein Schlüsselwort als `highlight`, wörtlich wie in der Überschrift. Es bekommt den Kreidestrich.
- Überschriften kurz, möglichst zwei Zeilen.
- Umfragefolien schlicht: Überschrift und nur die Frage, keine Anleitung.
- Dramaturgie für Vorträge: Hook mit Wiedererkennung, These, Bruch, Auflösung, Praxis, ein Merksatz zum Schluss. Live-Umfragen einplanen.
- Das Badge unten rechts und die Foliennummer unten links setzt der Generator automatisch. Auf der ersten Folie fehlen beide.
