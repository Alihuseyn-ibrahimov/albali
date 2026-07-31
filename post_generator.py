"""Al Balı Instagram post şablonu — 1080x1350 (4:5) vizual generator.

İstifadə:
    py -3 albali/post_generator.py --demo

Kontent sütunları üçün hazır stillər var (`COLUMNS`). Hər post eyni brend
kimliyini saxlayır: tünd fon, bal rəngi vurğular, pətək naxışı.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- Brend paleti ---------------------------------------------------------

BG_TOP = (26, 20, 16)
BG_BOTTOM = (43, 33, 24)
GOLD = (245, 179, 1)
GOLD_SOFT = (212, 160, 45)
CREAM = (245, 238, 224)
BODY = (226, 208, 176)
MUTED = (150, 136, 118)
GREEN = (46, 125, 78)

W, H = 1080, 1350
MARGIN = 88

FONT_DIR = Path("C:/Windows/Fonts")
FONT_BOLD = FONT_DIR / "segoeuib.ttf"
FONT_REG = FONT_DIR / "segoeui.ttf"


@dataclass(frozen=True)
class Column:
    """Kontent sütunu — etiket mətni və vurğu rəngi."""

    label: str
    accent: tuple[int, int, int]


COLUMNS = {
    "fakt": Column("BAL HAQQINDA", GOLD),
    "mif": Column("DOĞRU / YANLIŞ", GOLD),
    "hekaye": Column("LAÇINDAN", GREEN),
    "kampaniya": Column("AVQUST SÜZÜMÜ", GOLD),
    "sosial": Column("MÜŞTƏRİ RƏYİ", GREEN),
    "mehsul": Column("MƏHSUL", GOLD),
}


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Mətni piksel enine görə sətirlərə bölür. `\n` açıq sətir sonu sayılır."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        line = ""
        for word in paragraph.split():
            trial = f"{line} {word}".strip()
            if font.getlength(trial) <= max_w:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def _block_height(
    text: str, font: ImageFont.FreeTypeFont, max_w: int, line_gap: float
) -> int:
    return len(_wrap(text, font, max_w)) * int(font.size * line_gap)


def _draw_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    max_w: int,
    fill: tuple[int, int, int],
    line_gap: float = 1.32,
) -> int:
    """Mətni çəkir və növbəti sərbəst y koordinatını qaytarır."""
    step = int(font.size * line_gap)
    for line in _wrap(text, font, max_w):
        if line:
            draw.text((x, y), line, font=font, fill=fill)
        y += step
    return y


def _gradient_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        color = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    return img


def _hexagon(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    return [
        (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
        for a in range(30, 360, 60)
    ]


def _draw_honeycomb(img: Image.Image, r: int = 62, alpha: int = 20) -> None:
    """Sağ üst küncdə solğun pətək naxışı — brend imzası."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    dx = math.sqrt(3) * r
    dy = 1.5 * r
    row = 0
    cy = -r
    while cy < H * 0.42:
        offset = (dx / 2) if row % 2 else 0
        cx = W * 0.52 + offset
        while cx < W + dx:
            draw.polygon(_hexagon(cx, cy, r), outline=(*GOLD, alpha), width=3)
            cx += dx
        cy += dy
        row += 1
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))


def make_post(
    column: str,
    headline: str,
    body: str,
    cta: str = "Sifariş üçün DM yazın",
    out_path: str | Path = "albali/out/post.png",
) -> Path:
    """Bir feed postu yaradır və faylın yolunu qaytarır."""
    if column not in COLUMNS:
        raise ValueError(f"Naməlum sütun: {column!r}. Mövcud: {sorted(COLUMNS)}")
    col = COLUMNS[column]

    img = _gradient_bg()
    _draw_honeycomb(img)
    draw = ImageDraw.Draw(img)

    f_brand = _font(FONT_BOLD, 34)
    f_origin = _font(FONT_REG, 22)
    f_label = _font(FONT_BOLD, 25)
    f_head = _font(FONT_BOLD, 74)
    f_body = _font(FONT_REG, 36)
    f_cta = _font(FONT_BOLD, 32)

    # Başlıq zolağı: brend + mənşə
    draw.text((MARGIN, 78), "AL BALI", font=f_brand, fill=GOLD)
    draw.text((MARGIN, 122), "LAÇIN · OĞULDƏRƏ · 2441 m", font=f_origin, fill=MUTED)

    # Məzmun bloku başlıq zolağı ilə CTA zolağı arasında şaquli mərkəzləşdirilir,
    # yoxsa uzun və qısa mətnlərdə tarazlıq pozulur.
    bar_h = 116
    text_w = W - MARGIN * 2
    pad_x, pad_y = 22, 12
    pill_h = f_label.size + pad_y * 2

    gap_pill_head, gap_head_rule, gap_rule_body = 58, 34, 52
    content_h = (
        pill_h
        + gap_pill_head
        + _block_height(headline, f_head, text_w, 1.18)
        + gap_head_rule
        + 5
        + gap_rule_body
        + _block_height(body, f_body, text_w, 1.44)
    )
    zone_top, zone_bottom = 210, H - bar_h - 40
    y = zone_top + max(0, (zone_bottom - zone_top - content_h) // 2)

    # Sütun etiketi (pill)
    label = col.label
    lw = int(f_label.getlength(label))
    draw.rounded_rectangle(
        [MARGIN, y, MARGIN + lw + pad_x * 2, y + pill_h],
        radius=8,
        fill=col.accent,
    )
    draw.text((MARGIN + pad_x, y + pad_y - 2), label, font=f_label, fill=BG_TOP)
    y += pill_h + gap_pill_head

    # Başlıq
    y = _draw_text_block(draw, headline, f_head, MARGIN, y, text_w, CREAM, 1.18)

    # Ayırıcı xətt
    y += gap_head_rule
    draw.line([(MARGIN, y), (MARGIN + 140, y)], fill=col.accent, width=5)
    y += gap_rule_body

    # Mətn
    _draw_text_block(draw, body, f_body, MARGIN, y, text_w, BODY, 1.44)

    # Alt CTA zolağı
    draw.rectangle([0, H - bar_h, W, H], fill=(18, 14, 11))
    draw.line([(0, H - bar_h), (W, H - bar_h)], fill=col.accent, width=4)
    cta_y = H - bar_h + (bar_h - f_cta.size) // 2 - 4
    draw.text((MARGIN, cta_y), cta, font=f_cta, fill=CREAM)
    draw.text(
        (W - MARGIN - f_cta.getlength("@al.bali.az"), cta_y),
        "@al.bali.az",
        font=f_cta,
        fill=GOLD,
    )

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Al Balı post generatoru")
    parser.add_argument("--demo", action="store_true", help="nümunə postlar yarat")
    args = parser.parse_args()

    if args.demo:
        made = [
            make_post(
                "fakt",
                "1 kq bal üçün\narılar 4 milyon\nçiçək gəzir",
                "Bir arı ömrü boyu cəmi bir çay qaşığı bal hazırlayır.\n\n"
                "Laçın dağlarında, 2441 metr yüksəklikdə həmin çiçəklər "
                "kəklikotu, yovşan və dağ nanəsidir. Balın dadındakı fərq "
                "buradan gəlir.",
                out_path="albali/out/nümunə-fakt.png",
            ),
            make_post(
                "kampaniya",
                "Avqust süzümünə\nsayılı günlər qaldı",
                "Keçən süzümdən stokda cəmi 30 kq bal qalıb.\n\n"
                "Yeni süzüm avqustun ortasında pətəkdən çıxacaq. "
                "Sifarişinizi indidən qeyd etdirin.",
                cta="Pre-order üçün DM yazın",
                out_path="albali/out/nümunə-kampaniya.png",
            ),
        ]
        for p in made:
            print(f"yaradıldı: {p}")


if __name__ == "__main__":
    main()
