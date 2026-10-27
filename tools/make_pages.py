"""Renders one day's reading into the folder layout the app reads.

Usage:  python tools/make_pages.py tools/src/4.json

The source file holds every language:

    {
      "ar": {"title": "...", "body": "Paragraph one.\n\nParagraph two.",
             "question": "Optional reflection question",
             "source": "Optional credit, shown under the footer",
             "poem": true},  # optional: centred lines; "\n" breaks a line
      "en": {...}, "de": {...}, "tr": {...}
    }

and produces <N>/<lang>/1.png, 2.png, ... (+ q.txt when there is a question),
plus a flat <N>/1.png, ... copy in FLAT_LANG for builds older than languages,
where N is the source file's name. Long texts flow onto as many pages as
needed. The look matches the original sample pages in 1/-3/.

Audiences. The root folders (1/, 2/, ...) are the days from before there were
audiences, for everyone, and they stay as they are. Each audience has its own
complete list that starts at day 1: muslim/<N>/<lang>/ and general/<N>/<lang>/.
Days 1 to 10 there are copies of the root days (--copy-shared); every day after
them is added to the audience folders only: put its source in tools/src/muslim/
or tools/src/general/ (the file name is the day number) and it is rendered
there, with no flat copy. Every run also rewrites index.json, which tells the
app where each list ends so it never probes for folders.

    python tools/make_pages.py tools/src/muslim/11.json tools/src/general/11.json
    python tools/make_pages.py --copy-shared  # copy the root days into both audiences
    python tools/make_pages.py --index        # only rewrite index.json

A language may instead give "pages": [{"title": ..., "body": ...}, ...] to fix
the page breaks itself, each page with its own title. A top-level
"_flat": false leaves the flat folder alone (used for the original 1/-3/).
"""

import json
import sys
from pathlib import Path

import arabic_reshaper
from PIL import Image, ImageDraw, ImageFont

# The pure-Python algorithm mirrors brackets and «» in right-to-left text.
# The newer Rust-backed `bidi.get_display` (python-bidi 0.5+) does not, so
# "(1)" and «...» would come out reversed.
from bidi.algorithm import get_display

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(r"C:\Windows\Fonts")

# Page geometry and colours, measured from the sample pages.
W, H = 1080, 1520
MARGIN = 110
BG = (251, 247, 239)
TITLE = (79, 55, 139)
TEXT = (43, 37, 34)
MUTED = (140, 130, 122)
RULE = (227, 218, 203)
TITLE_TOP = 140
BODY_TOP = 300  # first page, under the title
BODY_TOP_NEXT = 150  # following pages
BODY_BOTTOM = 1290
RULE_Y = 1330
FOOTER_Y = 1368
SOURCE_Y = 1420

RTL = {"ar"}
FONT_FILES = {
    # Segoe UI covers Arabic; Georgia reads well for Latin scripts.
    "ar": ("segoeuib.ttf", "segoeui.ttf"),
    "latin": ("georgiab.ttf", "georgia.ttf"),
}
DAY_LABEL = {"ar": "اليوم {n}", "en": "Day {n}", "de": "Tag {n}", "tr": "Gün {n}", "fr": "Jour {n}"}


def shape(text, lang):
    """Arabic needs joined letters and visual order; Pillow without raqm
    does neither by itself."""
    return get_display(arabic_reshaper.reshape(text)) if lang in RTL else text


def wrap(draw, text, font, lang, width):
    """Splits on words in reading order, measuring the shaped line."""
    lines = []
    for paragraph in text.split("\n\n"):
        # A single line break is kept (verse halves, short lines).
        for part in paragraph.split("\n"):
            words, line = part.split(), ""
            for word in words:
                candidate = f"{line} {word}".strip()
                if draw.textlength(shape(candidate, lang), font=font) <= width:
                    line = candidate
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
        lines.append(None)  # paragraph gap
    while lines and lines[-1] is None:
        lines.pop()
    return lines


def new_page():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def draw_line(draw, y, text, font, fill, lang, align="start"):
    shaped = shape(text, lang)
    width = draw.textlength(shaped, font=font)
    if align == "center":
        x = (W - width) / 2
    elif (align == "start") == (lang in RTL):
        x = W - MARGIN - width
    else:
        x = MARGIN
    draw.text((x, y), shaped, font=font, fill=fill)


# Builds from before language folders only fetch the flat <N>/1.png, ...
# Without a flat copy they would stop at this folder forever, so every
# folder also gets one, in this language.
FLAT_LANG = "ar"


def render(day, lang, entry, flat=False, audience=None):
    bold, regular = FONT_FILES["ar" if lang in RTL else "latin"]
    title_font = ImageFont.truetype(str(FONTS / bold), 64)
    body_font = ImageFont.truetype(str(FONTS / regular), 40)
    footer_font = ImageFont.truetype(str(FONTS / regular), 28)
    line_h, gap = 66, 34

    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    source = (entry.get("source") or "").strip()
    # Poems are centred, one verse half per line.
    align = "center" if entry.get("poem") else "start"

    def lay_out(title, body):
        """One titled section; flows onto extra pages when it is long."""
        lines = wrap(probe, body.strip(), body_font, lang, W - 2 * MARGIN)
        title_lines = wrap(probe, title.strip(), title_font, lang, W - 2 * MARGIN)
        out, (img, draw) = [], new_page()
        y = TITLE_TOP
        for t in title_lines:
            if t is not None:
                draw_line(draw, y, t, title_font, TITLE, lang, "center")
                y += 84
        y = max(BODY_TOP, y + 70)
        for line in lines:
            if line is None:
                y += gap
                continue
            if y + line_h > BODY_BOTTOM:
                out.append(img)
                img, draw = new_page()
                y = BODY_TOP_NEXT
            draw_line(draw, y, line, body_font, TEXT, lang, align)
            y += line_h
        out.append(img)
        return out

    # "pages": [{title, body}, ...] fixes the page breaks, each page with its
    # own title; otherwise one title and a body that flows freely.
    sections = entry.get("pages") or [entry]
    pages = [p for s in sections for p in lay_out(s["title"], s["body"])]

    base = ROOT / audience if audience else ROOT
    out = base / str(day) if flat else base / str(day) / lang
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    for i, page in enumerate(pages, 1):
        d = ImageDraw.Draw(page)
        d.line([(MARGIN, RULE_Y), (W - MARGIN, RULE_Y)], fill=RULE, width=2)
        draw_line(d, FOOTER_Y, DAY_LABEL[lang].format(n=day), footer_font, MUTED, lang)
        draw_line(d, FOOTER_Y, f"{i} / {len(pages)}", footer_font, MUTED, lang, "end")
        if source:
            # On every page, so a single shared page still carries the credit.
            draw_line(d, SOURCE_Y, source, footer_font, MUTED, lang, "center")
        page.save(out / f"{i}.png", optimize=True)

    question = (entry.get("question") or "").strip()
    q_file = out / "q.txt"
    if question:
        q_file.write_text(question + "\n", encoding="utf-8")
    elif q_file.exists():
        q_file.unlink()
    return len(pages)


AUDIENCES = ("muslim", "general")

# The last root day for everyone. The root list is closed at 10.
SHARED_LAST = 10


def _exists(folder):
    """A folder is there when it has a first page, flat or in a language."""
    return (folder / "1.png").exists() or any(
        (folder / lang / "1.png").exists() for lang in DAY_LABEL
    )


def build_index():
    """Where each list of folders ends: the root days (1, 2, 3, ...) and each
    audience's own list, which also starts at 1."""
    def last_of(base):
        n = 0
        while _exists(base / str(n + 1)):
            n += 1
        return n

    # Root days past SHARED_LAST (the "update the app" day, from
    # tools/src/legacy/) are for versions older than index.json, which only
    # walk the root list. Capping shared keeps every newer version off them.
    index = {"shared": min(last_of(ROOT), SHARED_LAST)}
    for audience in AUDIENCES:
        index[audience] = last_of(ROOT / audience)
    return index


def copy_shared():
    """Copies the language folders of every root day into muslim/ and
    general/ (the flat copy is only for builds older than languages, so it is
    left out). Safe to repeat: a day is replaced by the root's version."""
    import shutil

    day = 1
    while day <= SHARED_LAST and _exists(ROOT / str(day)):
        for audience in AUDIENCES:
            for lang in DAY_LABEL:
                src = ROOT / str(day) / lang
                if not (src / "1.png").exists():
                    continue
                dst = ROOT / audience / str(day) / lang
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
        print(f"day {day} copied into {', '.join(AUDIENCES)}")
        day += 1


def write_index():
    index = build_index()
    (ROOT / "index.json").write_text(json.dumps(index) + "\n", encoding="utf-8")
    print(f"index.json: {index}")


def main(src):
    src = Path(src)
    day = int(src.stem)
    audience = src.parent.name if src.parent.name in AUDIENCES else None
    data = json.loads(src.read_text(encoding="utf-8"))
    for lang in ("ar", "en", "de", "tr", "fr"):
        if lang not in data:
            sys.exit(f"{src}: missing language '{lang}'")
    where = f"{audience}/{day}" if audience else f"{day}"
    for lang, entry in data.items():
        if lang.startswith("_"):
            continue
        print(f"{where}/{lang}: {render(day, lang, entry, audience=audience)} page(s)")
    # The flat copy is for builds older than languages, which only know the
    # shared folders; an audience folder has none. "_flat": false leaves an
    # existing flat folder (the original samples) exactly as it is.
    if not audience and data.get("_flat", True):
        print(f"{day}/ (flat, {FLAT_LANG}): {render(day, FLAT_LANG, data[FLAT_LANG], flat=True)} page(s)")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if arg == "--copy-shared":
            copy_shared()
        elif arg != "--index":
            main(arg)
    write_index()
