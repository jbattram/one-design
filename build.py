#!/usr/bin/env python3
"""
one.design – HTML Präsentations-Generator
Konvertiert Markdown mit YAML-Frontmatter zu schönen destination.one Präsentationen
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

# ============================================================================
# LOAD CONFIGURATION
# ============================================================================

def load_brand() -> Dict[str, Any]:
    """Load BRAND.json configuration"""
    brand_path = Path(__file__).parent / "BRAND.json"
    with open(brand_path) as f:
        return json.load(f)

BRAND = load_brand()

# ============================================================================
# LOAD DESIGN ELEMENTS
# ============================================================================

def load_neon_line_svg() -> str:
    """Load neon line SVG as data URI"""
    svg_path = Path(__file__).parent / "neon-line.svg"
    if svg_path.exists():
        with open(svg_path, 'r') as f:
            svg_content = f.read()
        # Convert to base64 data URI
        import base64
        svg_b64 = base64.b64encode(svg_content.encode()).decode()
        return f"data:image/svg+xml;base64,{svg_b64}"
    return ""

NEON_LINE_SVG = load_neon_line_svg()

# ============================================================================
# MARKDOWN PARSER
# ============================================================================

DEFAULT_BADGE = 'one.design'  # wird in build_presentation mit dem Titel der Präsentation überschrieben


class MarkdownPresentation:
    """Parse markdown file with YAML frontmatter per slide"""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.slides: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self._parse()

    def _parse(self):
        """Parse markdown file into slides"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by "---" separators (YAML frontmatter + slides)
        sections = content.split('\n---\n')

        # First section: document metadata
        if sections:
            try:
                meta_text = sections[0]
                if meta_text.startswith('---\n'):
                    meta_text = meta_text[4:]
                self.metadata = yaml.safe_load(meta_text) or {}
            except:
                self.metadata = {}

        # Process slides (sections 1+)
        # Each section is a complete YAML block (no markdown body in this simple format)
        for i in range(1, len(sections)):
            slide_text = sections[i].strip()
            if not slide_text:
                continue

            # Try to parse the entire section as YAML
            try:
                slide_data = yaml.safe_load(slide_text)
                if slide_data and isinstance(slide_data, dict):
                    self.slides.append(slide_data)
                else:
                    # If YAML parse failed, treat as markdown body
                    self.slides.append({'body': slide_text})
            except Exception as e:
                # If YAML fails, treat as markdown body
                self.slides.append({'body': slide_text})

# ============================================================================
# SLIDE RENDERERS
# ============================================================================

# ============================================================================
# PLATZHALTER-GRAFIKEN (wenn eine Datei in assets/ fehlt)
# ============================================================================
import hashlib
import urllib.parse as _up

_PAL = [("#dcefa6", "#a6e4da"), ("#e6f5b8", "#b5ebe2"), ("#cfeaa0", "#9fe0d4"), ("#e2f2b0", "#aee6e8")]

def _svg_uri(svg: str) -> str:
    return "data:image/svg+xml," + _up.quote(svg.replace("\n", ""), safe="/:=' ").replace(" ", "%20")

def placeholder(kind: str, key: str = "") -> str:
    """Markenkonforme Platzhalter-Grafik als Data-URI. kind: photo | illu | chart | icon | person"""
    h = int(hashlib.md5((key or kind).encode()).hexdigest(), 16)
    c1, c2 = _PAL[h % len(_PAL)]
    g = f"<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='{c1}'/><stop offset='1' stop-color='{c2}'/></linearGradient></defs>"
    if kind == "photo":
        sx = 120 + (h >> 4) % 260
        hx = 60 + (h >> 8) % 200
        svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='600' height='800' viewBox='0 0 600 800' preserveAspectRatio='xMidYMid slice'>{g}"
               f"<rect width='600' height='800' fill='url(#g)'/>"
               f"<circle cx='{sx+120}' cy='230' r='85' fill='#ffffff' fill-opacity='0.75'/>"
               f"<path d='M0,800 L0,560 Q{hx+80},430 {hx+210},560 T520,520 L600,560 L600,800 Z' fill='#ffffff' fill-opacity='0.55'/>"
               f"<path d='M0,800 L0,660 Q{hx+140},560 {hx+300},680 T600,640 L600,800 Z' fill='#a8db20' fill-opacity='0.55'/></svg>")
    elif kind == "illu":
        svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='900' height='900' viewBox='0 0 900 900'>{g}"
               f"<circle cx='500' cy='470' r='300' fill='url(#g)'/>"
               f"<path d='M120,640 C250,420 330,760 460,520 S700,300 800,420' fill='none' stroke='#000000' stroke-width='10' stroke-linecap='round'/>"
               f"<circle cx='800' cy='420' r='26' fill='#b4f000'/></svg>")
    elif kind == "chart":
        bars = [0.35, 0.55, 0.45, 0.8, 0.65, 0.95]
        parts = "".join(
            f"<rect x='{90+i*125}' y='{600-b*480}' width='80' height='{b*480}' rx='6' fill='{'#a8db20' if i != 5 else '#00cfc0'}'/>"
            for i, b in enumerate(bars))
        svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='900' height='700' viewBox='0 0 900 700'>{parts}"
               f"<path d='M60,600 L860,600' stroke='#000000' stroke-width='6' stroke-linecap='round'/></svg>")
    elif kind == "person":
        svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 400 400'>{g}"
               f"<rect width='400' height='400' fill='url(#g)'/><circle cx='200' cy='160' r='70' fill='#ffffff' fill-opacity='0.8'/>"
               f"<path d='M60,400 Q200,230 340,400 Z' fill='#ffffff' fill-opacity='0.8'/></svg>")
    else:  # icon
        svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'>"
               "<circle cx='60' cy='60' r='54' fill='#a8db20'/>"
               "<path d='M32,66 L52,86 L90,40' fill='none' stroke='#000000' stroke-width='9' stroke-linecap='round' stroke-linejoin='round'/></svg>")
    return _svg_uri(svg)

# Maximale Kantenlänge in Pixel je Bildart (Anzeigegröße auf der Folie + Reserve)
MAX_IMAGE_SIDE = {"icon": 320, "badge": 160, "illu": 1400, "photo": 1920,
                  "chart": 1600, "person": 640}


def _shrink_image(f: Path, kind: str):
    """Verkleinert ein Bild passend zur Bildart. Gibt (Mime, Bytes) zurück oder None,
    wenn Pillow fehlt, das Bild kein Pixelbild ist oder die Verkleinerung nichts bringt."""
    try:
        from PIL import Image
        import io
    except Exception:
        return None
    if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
        return None
    try:
        im = Image.open(f)
        im.load()
        limit = MAX_IMAGE_SIDE.get(kind, 1400)
        if max(im.size) > limit:
            im.thumbnail((limit, limit), Image.LANCZOS)
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        buf = io.BytesIO()
        if has_alpha:
            im.convert("RGBA").save(buf, "PNG", optimize=True)
            mime = "image/png"
        else:
            im.convert("RGB").save(buf, "JPEG", quality=90, optimize=True)
            mime = "image/jpeg"
        data = buf.getvalue()
        if len(data) >= f.stat().st_size:
            return None
        return mime, data
    except Exception:
        return None


def asset_src(kind: str, name: str) -> str:
    """Echte Datei aus assets/ (eingebettet als Data-URI), falls vorhanden – sonst Platzhalter."""
    if name:
        f = Path(__file__).parent / "assets" / name
        if f.is_file():
            import base64, mimetypes
            mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            data = None
            # Pixelbilder auf Anzeigegröße verkleinern, damit die HTML-Datei schlank bleibt
            small = _shrink_image(f, kind)
            if small:
                mime, data = small
            if data is None:
                data = f.read_bytes()
            # Bild direkt einbetten, damit die HTML-Datei allein vollständig ist
            return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")
    return placeholder(kind, name)


class SlideRenderer:
    """Base class for rendering slides"""

    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML special chars"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    @staticmethod
    def render_bullets(text: str) -> str:
        """Convert markdown bullets to HTML"""
        lines = text.strip().split('\n')
        html = []

        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                text_content = line[2:].strip()
                html.append(f'<li>{SlideRenderer.escape_html(text_content)}</li>')

        if html:
            return '<ul>' + ''.join(html) + '</ul>'
        return ''

    @staticmethod
    def render_headline_with_highlight(text: str, highlight: Optional[str] = None) -> str:
        """Render headline with optional organischer Kreide-Underline on highlighted word"""
        if highlight and highlight in text:
            # Split by highlight word and escape each part
            parts = text.split(highlight)
            escaped_parts = [SlideRenderer.escape_html(part) for part in parts]
            escaped_highlight = SlideRenderer.escape_html(highlight)
            # CSS::after handles the underline with organic chalk stroke
            return f'<span class="kreide-underline">{escaped_highlight}</span>'.join(escaped_parts)
        return SlideRenderer.escape_html(text)

    @staticmethod
    def render_cta_button(cta_link: Optional[str] = None, cta_text: Optional[str] = None) -> str:
        """Render CTA button if link and text provided"""
        if cta_link and cta_text:
            return f'<a href="{SlideRenderer.escape_html(cta_link)}" class="cta-button">{SlideRenderer.escape_html(cta_text)}</a>'
        return ''

    @staticmethod
    def render_qr_code(qr_url: Optional[str] = None, as_replacement: bool = False) -> str:
        """Render QR code badge"""
        if not qr_url:
            return ''

        # Generate QR code using QR code API (simple service)
        qr_data_url = f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={qr_url}"
        size_class = "qr-replacement" if as_replacement else "qr-badge"

        return f'''
        <div class="qr-code-wrapper {size_class}">
            <img src="{qr_data_url}" alt="QR Code" class="qr-code">
        </div>
        '''

    @staticmethod
    def get_circle_style(slide_index: int = 0) -> str:
        """Generate variable circle positioning"""
        import hashlib
        # Use slide index as seed for consistent variation
        seed = int(hashlib.md5(str(slide_index).encode()).hexdigest()[:8], 16) % 100

        positions = [
            "--circle-size: 750px; --circle-opacity: 0.5; --circle-bottom: -150px; --circle-right: -200px;",
            "--circle-size: 850px; --circle-opacity: 0.45; --circle-bottom: -250px; --circle-right: -100px;",
            "--circle-size: 800px; --circle-opacity: 0.5; --circle-bottom: -180px; --circle-right: -280px;",
            "--circle-size: 900px; --circle-opacity: 0.4; --circle-bottom: -300px; --circle-right: -150px;",
            "--circle-size: 780px; --circle-opacity: 0.5; --circle-bottom: -120px; --circle-right: -220px;",
        ]

        return f"style=\"{positions[seed % len(positions)]}\""

    def render(self, data: Dict[str, Any]) -> str:
        """Override in subclasses"""
        raise NotImplementedError

class TitleSlideRenderer(SlideRenderer):
    """Slide 1: Title + Illustration"""

    def render(self, data: Dict[str, Any]) -> str:
        headline = data.get('headline', '')
        subline = data.get('subline', '')
        illustration = data.get('illustration', '')
        highlight = data.get('highlight', None)
        badge_text = data.get('badge', DEFAULT_BADGE)
        cta_link = data.get('cta_link', None)
        cta_text = data.get('cta_text', None)
        qr_code = data.get('qr_code', None)

        # Render headline with optional underline
        headline_html = self.render_headline_with_highlight(headline, highlight) if highlight else self.escape_html(headline)

        illu_html = ''
        if illustration:
            illu_html = f'<img src="{asset_src("illu", illustration)}" alt="" class="title-illu">'
        elif qr_code:
            # QR as replacement for illustration
            illu_html = self.render_qr_code(qr_code, as_replacement=True)

        cta_html = self.render_cta_button(cta_link, cta_text)
        qr_html = self.render_qr_code(qr_code) if illustration and qr_code else ''

        return f'''
        <section class="slide title-slide{' has-illu' if illustration else ''}">
            <div class="badge-label">{self.escape_html(badge_text)}</div>
            <div class="title-content">
                <h1>{headline_html}</h1>
                <p class="subline">{self.escape_html(subline)}</p>
                {cta_html}
            </div>
            <div class="title-illu-container">
                {illu_html}
                {qr_html}
            </div>
        </section>
        '''

class WidePhotosRenderer(SlideRenderer):
    """Slide 2: Wide + Photo Collage"""

    def render(self, data: Dict[str, Any]) -> str:
        headline = data.get('headline', '')
        subline = data.get('subline', '')
        intro = data.get('intro', '')
        image_position = data.get('image_position', 'right')  # left or right
        photos = data.get('photos', [])
        highlight = data.get('highlight', None)
        badge_text = data.get('badge', DEFAULT_BADGE)
        cta_link = data.get('cta_link', None)
        cta_text = data.get('cta_text', None)
        qr_code = data.get('qr_code', None)

        # Render headline with optional underline
        headline_html = self.render_headline_with_highlight(headline, highlight) if highlight else self.escape_html(headline)

        # Generate photo HTML with rotation
        photo_html = []
        for idx, photo in enumerate(photos):
            path = photo.get('path', '')
            rotate = photo.get('rotate', 0)
            photo_html.append(
                f'<img src="{asset_src("photo", path)}" alt="" class="photo" '
                f'style="transform: rotate({rotate}deg);">'
            )

        qr_html = self.render_qr_code(qr_code) if photos and qr_code else ''
        photos_div = '<div class="photos-collage">' + ''.join(photo_html) + qr_html + '</div>'

        cta_html = self.render_cta_button(cta_link, cta_text)

        text_div = f'''
        <div class="text-col">
            <h2>{headline_html}</h2>
            <p class="intro">{self.escape_html(intro)}</p>
            {cta_html}
        </div>
        '''

        # Arrange based on position
        if image_position == 'left':
            layout = photos_div + text_div
            layout_class = 'wide-photos flip'
        else:
            layout = text_div + photos_div
            layout_class = 'wide-photos'

        return f'''
        <section class="slide {layout_class}">
            <div class="badge-label">{self.escape_html(badge_text)}</div>
            {layout}
        </section>
        '''

class ChartTextRenderer(SlideRenderer):
    """Slide 3: Chart + Text + Big Number"""

    def render(self, data: Dict[str, Any]) -> str:
        headline = data.get('headline', '')
        number = data.get('number', '')
        subtext = data.get('subtext', '')
        chart_image = data.get('chart_image', '')
        chart_position = data.get('chart_position', 'left')  # left or right
        highlight = data.get('highlight', None)
        badge_text = data.get('badge', DEFAULT_BADGE)
        cta_link = data.get('cta_link', None)
        cta_text = data.get('cta_text', None)
        qr_code = data.get('qr_code', None)

        # Render headline with optional underline
        headline_html = self.render_headline_with_highlight(headline, highlight) if highlight else self.escape_html(headline)

        chart_html = ''
        qr_html = ''
        if chart_image:
            chart_html = f'<img src="{asset_src("chart", chart_image)}" alt="Chart" class="chart-image">'
            if qr_code:
                qr_html = self.render_qr_code(qr_code)

        cta_html = self.render_cta_button(cta_link, cta_text)

        text_div = f'''
        <div class="chart-text-content">
            <h2>{headline_html}</h2>
            <div class="big-number">{self.escape_html(number)}</div>
            <p class="subtext">{self.escape_html(subtext)}</p>
            {cta_html}
        </div>
        '''

        chart_div = f'<div class="chart-col">{chart_html}{qr_html}</div>'

        # Arrange based on position
        if chart_position == 'left':
            layout = chart_div + text_div
            layout_class = 'chart-text'
        else:
            layout = text_div + chart_div
            layout_class = 'chart-text flip'

        return f'''
        <section class="slide {layout_class}">
            <div class="badge-label">{self.escape_html(badge_text)}</div>
            {layout}
        </section>
        '''

class TeamGridRenderer(SlideRenderer):
    """Slide 4: Team Portraits"""

    def render(self, data: Dict[str, Any]) -> str:
        headline = data.get('headline', '')
        illustration = data.get('illustration', '')
        people = data.get('people', [])
        highlight = data.get('highlight', None)
        badge_text = data.get('badge', DEFAULT_BADGE)
        cta_link = data.get('cta_link', None)
        cta_text = data.get('cta_text', None)
        qr_code = data.get('qr_code', None)

        # Render headline with optional underline
        headline_html = self.render_headline_with_highlight(headline, highlight) if highlight else self.escape_html(headline)

        illu_html = ''
        qr_html = ''
        if illustration:
            illu_html = f'<img src="{asset_src("illu", illustration)}" alt="" class="team-illu">'
            if qr_code:
                qr_html = self.render_qr_code(qr_code)
        elif qr_code:
            # QR as replacement
            illu_html = self.render_qr_code(qr_code, as_replacement=True)

        # Generate person cards
        people_html = []
        for person in people:
            image = person.get('image', '')
            name = person.get('name', '')
            title = person.get('title', '')

            img_tag = f'<img src="{asset_src("person", image)}" alt="{name}" class="person-photo">' if image else ''

            people_html.append(f'''
            <div class="person">
                {img_tag}
                <p class="person-name">{self.escape_html(name)}</p>
                <p class="person-title">{self.escape_html(title)}</p>
            </div>
            ''')

        cta_html = self.render_cta_button(cta_link, cta_text)

        return f'''
        <section class="slide team-grid">
            <div class="badge-label">{self.escape_html(badge_text)}</div>
            <div class="team-illu-col">
                {illu_html}
                {qr_html}
            </div>
            <div class="team-people">
                <h2>{headline_html}</h2>
                <div class="people-grid">
                    {''.join(people_html)}
                </div>
                {cta_html}
            </div>
        </section>
        '''

class ThreeColumnsRenderer(SlideRenderer):
    """Slide 5: 3-Column List"""

    def render(self, data: Dict[str, Any]) -> str:
        headline = data.get('headline', '')
        columns = data.get('columns', [])
        highlight = data.get('highlight', None)
        badge_text = data.get('badge', DEFAULT_BADGE)
        cta_link = data.get('cta_link', None)
        cta_text = data.get('cta_text', None)
        qr_code = data.get('qr_code', None)

        # Render headline with optional underline
        headline_html = self.render_headline_with_highlight(headline, highlight) if highlight else self.escape_html(headline)

        col_html = []
        for col in columns:
            col_title = col.get('title', '')
            icon = col.get('icon', '')
            items = col.get('items', [])

            icon_tag = f'<img src="{asset_src("icon", icon)}" alt="" class="column-icon">' if icon else ''

            # Render items as bullets
            items_html = ''.join([
                f'<li>{self.escape_html(item)}</li>'
                for item in items
            ])

            col_html.append(f'''
            <div class="column">
                {icon_tag}
                <h3>{self.escape_html(col_title)}</h3>
                <ul>
                    {items_html}
                </ul>
            </div>
            ''')

        cta_html = self.render_cta_button(cta_link, cta_text)
        qr_html = self.render_qr_code(qr_code) if qr_code else ''

        return f'''
        <section class="slide three-columns">
            <div class="badge-label">{self.escape_html(badge_text)}</div>
            <h2>{headline_html}</h2>
            <div class="columns-container">
                {''.join(col_html)}
            </div>
            {cta_html}
            {qr_html}
        </section>
        '''

# ============================================================================
# RENDERER FACTORY
# ============================================================================

def get_renderer(layout_type: str) -> SlideRenderer:
    """Get the appropriate renderer for a layout type"""
    renderers = {
        'title': TitleSlideRenderer,
        'wide_photos': WidePhotosRenderer,
        'chart_text': ChartTextRenderer,
        'team_grid': TeamGridRenderer,
        'three_columns': ThreeColumnsRenderer,
    }

    renderer_class = renderers.get(layout_type, TitleSlideRenderer)
    return renderer_class()

# ============================================================================
# HTML TEMPLATE
# ============================================================================

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {primary_color};
            --secondary: {secondary_color};
            --bg: #ffffff;
            --text: #000000;
            --u: min(calc(100vw / 1920), calc(100vh / 1080));
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: '{font_family}';
            background: var(--bg);
            color: var(--text);
            margin: 0;
            overflow: hidden;
        }}

        .presentation {{
            width: 100%;
            height: 100vh;
            background: #e8ebe8;
            display: flex;
            flex-direction: column;
            overflow-y: scroll;
            scroll-snap-type: y mandatory;
        }}

        .slide {{
            width: calc(1920 * var(--u));
            height: calc(1080 * var(--u));
            margin: calc((100vh - 1080 * var(--u)) / 2) auto;
            background: #ffffff;
            flex-shrink: 0;
            padding: {padding};
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            scroll-snap-align: center;
            scroll-snap-stop: always;
            overflow: hidden;
        }}

        /* Background Circle - appears behind content */
        .slide::before {{
            content: '';
            position: absolute;
            border-radius: 50%;
            background: linear-gradient(135deg, #dcefa6 0%, #c3ebc4 45%, #a6e4da 100%);
            z-index: 0;
            pointer-events: none;
        }}

        /* Vary circle by slide position - all corners & sides */
        .slide:nth-child(1)::before {{
            width: 800px; height: 800px; opacity: 0.5; bottom: -150px; right: -200px;
        }}
        .slide:nth-child(2)::before {{
            width: 850px; height: 850px; opacity: 0.5; top: -300px; left: -250px;
        }}
        .slide:nth-child(3)::before {{
            width: 780px; height: 780px; opacity: 0.5; top: -200px; right: -150px;
        }}
        .slide:nth-child(4)::before {{
            width: 900px; height: 900px; opacity: 0.45; bottom: -350px; left: -300px;
        }}
        .slide:nth-child(5)::before {{
            width: 750px; height: 750px; opacity: 0.5; top: -100px; right: -100px;
        }}
        .slide:nth-child(6)::before {{
            width: 820px; height: 820px; opacity: 0.5; bottom: -200px; left: -180px;
        }}
        .slide:nth-child(7)::before {{
            width: 790px; height: 790px; opacity: 0.5; top: -250px; left: -150px;
        }}
        .slide:nth-child(8)::before {{
            width: 870px; height: 870px; opacity: 0.45; bottom: -100px; right: -250px;
        }}
        .slide:nth-child(n+9)::before {{
            width: 800px; height: 800px; opacity: 0.5; top: -180px; left: -200px;
        }}

        /* Badge - grüner Kreis (Platzhalter) + Label rechts daneben, Gruppe 2rem vom Rand */
        .badge-label {{
            position: absolute;
            bottom: 2rem;
            right: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            font-size: 28px;
            font-weight: 600;
            color: #000000;
            white-space: nowrap;
            z-index: 50;
            pointer-events: none;
        }}

        .badge-label::before {{
            content: '';
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: var(--primary);
            flex-shrink: 0;
        }}

        /* Foliennummer unten links */
        .slide-number {{
            position: absolute;
            bottom: 2rem;
            left: 2rem;
            font-size: 24px;
            font-weight: 600;
            color: #555555;
            z-index: 50;
            pointer-events: none;
        }}
        .slide:first-child .slide-number {{
            display: none;
        }}

        /* Badge nur auf der Cover-Folie (erste Folie) ausblenden */
        .slide:first-child .badge-label {{
            display: none;
        }}

        /* Ensure content is above circle */
        .slide > *:not(.badge-label):not(.slide-number) {{
            position: relative;
            z-index: 1;
        }}

        /* Weiße Bildhintergründe ausblenden: Weiß wird durchsichtig, Linie und Farbe bleiben */
        .title-illu-container, .team-illu-col, .chart-image, .column-icon {{
            mix-blend-mode: multiply;
        }}
        /* damit die Icons mit dem Farbkreis dahinter mischen, darf der Container keinen eigenen Stapel bilden */
        .slide > .columns-container {{
            z-index: auto !important;
        }}

        h1 {{
            font-size: {h1_size};
            font-weight: {h1_weight};
            margin-bottom: 20px;
        }}

        h2 {{
            font-size: {h2_size};
            font-weight: {h2_weight};
            margin-bottom: 20px;
        }}

        h3 {{
            font-size: 44px;
            font-weight: 700;
        }}

        p {{
            font-size: {body_size};
            line-height: 1.4;
        }}

        .subline {{
            font-size: {intro_size};
            line-height: 1.3;
            margin-top: 24px;
            color: #000000;
        }}

        .intro {{
            font-size: {intro_size};
            line-height: 1.3;
            margin-bottom: 30px;
        }}

        /* Title Slide */
        .title-slide {{
            display: grid;
            grid-template-columns: 1.8fr 1fr;
            gap: 60px;
            align-items: center;
        }}

        .title-content h1 {{
            font-size: 108px;
            font-weight: 900;
            line-height: 1.2;
            text-wrap: balance;
        }}

        .title-illu-container {{
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        .title-illu {{
            max-width: 100%;
            max-height: 600px;
        }}

        /* Mit Illustration: größer, rechts bis an den Rand (kein Padding auf dieser Seite) */
        .title-slide.has-illu {{
            padding-right: 0;
            grid-template-columns: 1.25fr 1fr;
            gap: 20px;
        }}

        .title-slide.has-illu .title-illu-container {{
            justify-content: flex-end;
            align-self: stretch;
        }}

        .title-slide.has-illu .title-illu {{
            max-height: 100%;
            max-width: 100%;
            object-fit: contain;
            object-position: right center;
        }}

        /* Wide Photos Slide */
        .wide-photos {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 80px;
            align-items: center;
        }}

        .wide-photos.flip {{
            grid-template-columns: 1fr 1fr;
        }}

        .wide-photos.flip .photos-collage {{
            order: 1;
        }}

        .wide-photos.flip .text-col {{
            order: 2;
        }}

        .text-col h2 {{
            font-size: 108px;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 40px;
        }}

        .photos-collage {{
            position: relative;
            height: 600px;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}

        .photos-collage .photo {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 8px;
        }}

        /* Chart + Text Slide */
        .chart-text {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 80px;
            align-items: center;
        }}

        .chart-text.flip {{
            grid-template-columns: 1fr 1fr;
        }}

        .chart-text.flip .chart-col {{
            order: 2;
        }}

        .chart-text.flip .chart-text-content {{
            order: 1;
        }}

        .chart-col {{
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        .chart-image {{
            max-width: 100%;
            max-height: 700px;
        }}

        .chart-text-content h2 {{
            font-size: 88px;
            line-height: 1.15;
            margin-bottom: 30px;
        }}

        .big-number {{
            font-size: 180px;
            font-weight: 900;
            color: #000000;
            line-height: 1;
            margin: 40px 0;
        }}

        .chart-text-content .subtext {{
            font-size: 28px;
            color: #666;
        }}

        /* Team Grid Slide */
        .team-grid {{
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 80px;
        }}

        .team-illu-col {{
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }}

        .team-illu {{
            max-width: 250px;
            max-height: 600px;
        }}

        .team-people h2 {{
            font-size: 108px;
            font-weight: 900;
            margin-bottom: 60px;
        }}

        .people-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 40px;
        }}

        .person {{
            text-align: center;
        }}

        .person-photo {{
            width: 100%;
            aspect-ratio: 1;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 20px;
            border: 3px solid var(--primary);
        }}

        .person-name {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .person-title {{
            font-size: 18px;
            color: #666;
        }}

        /* Three Columns Slide */
        .three-columns {{
            justify-content: center;
            padding-bottom: 200px;
        }}

        .three-columns h2 {{
            font-size: 108px;
            font-weight: 900;
            margin-bottom: 80px;
        }}

        .columns-container {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 60px;
        }}

        .column {{
            padding: 30px;
        }}

        .column-icon {{
            width: 120px;
            height: 120px;
            margin-bottom: 30px;
        }}

        .column h3 {{
            font-size: 44px;
            margin-bottom: 30px;
        }}

        .column ul {{
            list-style: none;
        }}

        .column li {{
            font-size: 28px;
            line-height: 1.6;
            margin-bottom: 20px;
            padding-left: 30px;
            position: relative;
        }}

        .column li:before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: var(--primary);
            font-size: 24px;
        }}

        /* Neon Underline with SVG wavy */
        /* Organischer Kreide-Underline */
        .kreide-underline {{
            position: relative;
            display: inline-block;
            text-decoration: none;
            isolation: isolate;
        }}

        .kreide-underline::after {{
            content: "";
            position: absolute;
            left: -0.04em;
            right: -0.04em;
            bottom: -0.16em;
            height: 0.3em;
            background-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%20300%2040'%20preserveAspectRatio='none'%3E%3Cdefs%3E%3Cfilter%20id='r'%20x='-5%25'%20y='-30%25'%20width='110%25'%20height='160%25'%3E%3CfeTurbulence%20type='fractalNoise'%20baseFrequency='0.09%200.35'%20numOctaves='3'%20seed='4'%20result='n'/%3E%3CfeDisplacementMap%20in='SourceGraphic'%20in2='n'%20scale='9'%20xChannelSelector='R'%20yChannelSelector='G'/%3E%3C/filter%3E%3C/defs%3E%3Cpath%20filter='url%28%23r%29'%20fill='%23b4f000'%20d='M4%2C14.6%20L22%2C8.1%20L58%2C8.9%20L95%2C2.7%20L140%2C6.8%20L186%2C3.5%20L232%2C10.9%20L272%2C10.2%20L296%2C17.4%20L293%2C27.0%20L298%2C34.7%20L262%2C35.0%20L226%2C28.3%20L184%2C31.4%20L142%2C24.8%20L98%2C30.7%20L56%2C27.0%20L24%2C32.0%20L6%2C29.5%20L9%2C22.2%20Z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-size: 100% 100%;
            pointer-events: none;
            z-index: -1;
        }}

        /* CTA Button */
        .cta-button {{
            display: inline-block;
            background-color: var(--primary);
            color: #000000;
            padding: 12px 28px;
            border-radius: 24px;
            text-decoration: none;
            font-weight: 700;
            font-size: 18px;
            margin-top: 20px;
            transition: background-color 0.3s ease, box-shadow 0.3s ease;
            border: none;
            cursor: pointer;
        }}

        .cta-button:hover {{
            background-color: var(--secondary);
            box-shadow: 0 0 15px rgba(0, 207, 192, 0.5);
        }}

        /* QR Code Badge */
        .qr-code-wrapper {{
            position: relative;
        }}

        .qr-code-wrapper.qr-badge {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            width: 240px;
            height: 240px;
            border-radius: 12px;
            background: linear-gradient(135deg, #dcefa6, #a6e4da);
            padding: 8px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .qr-code-wrapper.qr-replacement {{
            width: 480px;
            height: 480px;
            margin: 0 auto;
        }}

        .qr-code {{
            width: 100%;
            height: 100%;
            border-radius: 8px;
            background: white;
        }}

        /* Utilities */
        ul {{
            list-style: none;
            padding-left: 0;
        }}

        ul li {{
            font-size: {bullet_size};
            line-height: 1.6;
            margin-bottom: 15px;
            padding-left: 30px;
            position: relative;
        }}

        ul li:before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: var(--primary);
        }}
    </style>
</head>
<body>
    <div class="presentation">
        {slides_html}
    </div>
    <script>
        // Tastatursteuerung: Pfeiltasten wechseln Folie für Folie
        (function() {{
            const deck = document.querySelector('.presentation');
            const slides = () => deck.querySelectorAll('.slide');
            const current = () => Math.round(deck.scrollTop / deck.clientHeight);
            const go = (i) => {{
                const n = slides().length;
                const t = Math.max(0, Math.min(n - 1, i));
                deck.scrollTo({{ top: t * deck.clientHeight, behavior: 'smooth' }});
            }};
            document.addEventListener('keydown', (e) => {{
                if (e.metaKey || e.ctrlKey || e.altKey) return;
                const k = e.key;
                if (k === 'ArrowDown' || k === 'ArrowRight' || k === 'PageDown' || (k === ' ' && !e.shiftKey)) {{
                    e.preventDefault(); go(current() + 1);
                }} else if (k === 'ArrowUp' || k === 'ArrowLeft' || k === 'PageUp' || (k === ' ' && e.shiftKey)) {{
                    e.preventDefault(); go(current() - 1);
                }} else if (k === 'Home') {{
                    e.preventDefault(); go(0);
                }} else if (k === 'End') {{
                    e.preventDefault(); go(slides().length - 1);
                }}
            }});
            // Fokus sicherstellen (wichtig in eingebetteter Vorschau)
            window.addEventListener('load', () => window.focus());
            document.addEventListener('click', () => window.focus());
        }})();
    </script>
</body>
</html>
'''

# ============================================================================
# MAIN
# ============================================================================

def build_presentation(markdown_path: str, output_path: str = 'index.html'):
    """Build presentation from markdown"""

    # Parse markdown
    pres = MarkdownPresentation(markdown_path)

    # Standard-Badge: Titel der Präsentation (nicht ein fester Anlass)
    global DEFAULT_BADGE
    DEFAULT_BADGE = str(pres.metadata.get('badge') or pres.metadata.get('title') or 'one.design')

    # Render slides
    slides_html = []
    for slide_data in pres.slides:
        layout = slide_data.get('layout', 'title')
        renderer = get_renderer(layout)
        slide_html = renderer.render(slide_data)
        slides_html.append(slide_html)

    total = len(slides_html)
    slides_html = [
        h.rstrip()[:-len('</section>')] + f'<div class="slide-number">{i} / {total}</div></section>'
        if h.rstrip().endswith('</section>') else h
        for i, h in enumerate(slides_html, 1)
    ]

    # Badge-Symbol: Titelbild der ersten Folie klein statt des grünen Kreises.
    # Im Titelblock abschaltbar mit  badge_icon: false  oder anderes Bild mit  badge_icon: "datei.png"
    badge_icon = pres.metadata.get('badge_icon', None)
    if badge_icon is None and pres.slides:
        badge_icon = pres.slides[0].get('illustration', '')
    badge_css = ''
    if badge_icon:
        f = Path(__file__).parent / "assets" / str(badge_icon)
        if f.is_file():
            src = asset_src("badge", str(badge_icon))
            badge_css = (
                "<style>.badge-label::before{background:url('" + src + "') center/contain no-repeat;"
                "border-radius:0;mix-blend-mode:multiply;}</style>"
            )

    # Build HTML from template
    html = HTML_TEMPLATE.format(
        title=pres.metadata.get('title', 'Presentation'),
        primary_color=BRAND['colors']['primary'],
        secondary_color=BRAND['colors']['secondary'],
        font_family=BRAND['typography']['font_family'],
        h1_size=f"{BRAND['typography']['sizes']['h1']['size_px']}px",
        h1_weight=BRAND['typography']['sizes']['h1']['weight'],
        h2_size=f"{BRAND['typography']['sizes']['h2']['size_px']}px",
        h2_weight=BRAND['typography']['sizes']['h2']['weight'],
        intro_size=f"{BRAND['typography']['sizes']['intro']['size_px']}px",
        body_size=f"{BRAND['typography']['sizes']['body']['size_px']}px",
        bullet_size=f"{BRAND['typography']['sizes']['body']['size_px']}px",
        padding=f"{BRAND['layout']['padding']['vertical']} {BRAND['layout']['padding']['horizontal']}",
        slides_html='\n'.join(slides_html),
    )
    if badge_css:
        html = html.replace('</head>', badge_css + '</head>', 1)

    # Skalierung: alle px/rem im CSS an die Deck-Größe koppeln (Basis 1920x1080)
    import re as _re
    def _scale_css(m):
        css = m.group(0)
        css = _re.sub(r'(-?\d*\.?\d+)rem', lambda x: f"calc({float(x.group(1))*16:g} * var(--u))", css)
        css = _re.sub(r'(?<![\w#-])(-?\d*\.?\d+)px', lambda x: f"calc({x.group(1)} * var(--u))" if x.group(1) not in ('0',) else '0', css)
        return css
    html = _re.sub(r'<style>.*?</style>', _scale_css, html, flags=_re.S)

    # Write output
    output_file = Path(output_path)
    output_file.write_text(html, encoding='utf-8')

    print(f"✅ Presentation built: {output_path}")
    print(f"   {len(pres.slides)} slides")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python build.py <input.md> [output.html]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'index.html'

    build_presentation(input_file, output_file)
