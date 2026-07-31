"""Al Balı Instagram post şablonu — 1440x1440 (1:1) vizual generator.

Rənglər və loqo **mövcud postlardan** götürülüb ki, yeni paylaşımlar köhnə
lentdən kəskin fərqlənməsin:

    fon #FEFDCD · yaşıl #37B400 · narıncı #DC810F   (2026-07-31-də piksel
    səviyyəsində nümunələnib), loqo `assets/logo.png` — 2025-08-21 tarixli
    postdan kəsilib, fonu şəffaflaşdırılıb.

İstifadə:
    py -3 albali/post_generator.py --demo
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- Brend paleti (mövcud postlardan nümunələnib) -------------------------

BG = (254, 253, 205)  # #FEFDCD krem-sarı
GREEN = (55, 180, 0)  # #37B400 başlıq yaşılı
GREEN_DEEP = (40, 132, 0)  # kiçik mətn üçün daha oxunaqlı yaşıl
ORANGE = (220, 129, 15)  # #DC810F vurğu narıncısı
INK = (79, 74, 42)  # isti tünd — əsas mətn
GOLD = (247, 197, 30)
GOLD_SOFT = (252, 226, 130)
WHITE = (255, 255, 255)

SIZE = 1440
MARGIN = 110
LOGO_W = 210

HERE = Path(__file__).parent
LOGO_PATH = HERE / "assets" / "logo.png"

# Şrift seçimi: Century Gothic və Trebuchet həndəsi görünüşcə brendə daha yaxın
# idi, LAKİN hər ikisində «ə» glifi yoxdur — mətn boş qutu kimi çıxırdı
# (2026-07-31-də render müqayisəsi ilə aşkarlandı). Segoe UI tam dəstəkləyir.
FONT_DIR = Path("C:/Windows/Fonts")
FONT_BOLD = FONT_DIR / "segoeuib.ttf"
FONT_REG = FONT_DIR / "segoeui.ttf"


@dataclass(frozen=True)
class Column:
    """Kontent sütunu — etiket mətni və pill rəngi."""

    label: str
    accent: tuple[int, int, int]


COLUMNS = {
    "fakt": Column("BAL HAQQINDA", GREEN),
    "mif": Column("DOĞRU / YANLIŞ", GREEN),
    "hekaye": Column("LAÇINDAN", GREEN_DEEP),
    "kampaniya": Column("AVQUST SÜZÜMÜ", ORANGE),
    "sosial": Column("MÜŞTƏRİ RƏYİ", GREEN_DEEP),
    "mehsul": Column("MƏHSUL", ORANGE),
}


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Mətni piksel eninə görə sətirlərə bölür. `\n` açıq sətir sonu sayılır."""
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


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    y: int,
    max_w: int,
    fill: tuple[int, int, int],
    line_gap: float,
) -> int:
    """Mətni mərkəzə hizalayıb çəkir, növbəti sərbəst y-i qaytarır."""
    step = int(font.size * line_gap)
    for line in _wrap(text, font, max_w):
        if line:
            draw.text((SIZE // 2, y), line, font=font, fill=fill, anchor="ma")
        y += step
    return y


def _hexagon(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    return [
        (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
        for a in range(30, 360, 60)
    ]


def _draw_honeycomb(img: Image.Image) -> None:
    """Künclərdə pətək dəstələri — köhnə postlardakı bəzək məntiqi."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    r = 62
    dx, dy = math.sqrt(3) * r, 1.5 * r

    # Dəstələr künclərdən kənara sürüşdürülüb ki, mətn sahəsinə girməsin.
    clusters = [(-70, -50, 2), (SIZE + 70, SIZE + 50, 2)]
    for cx0, cy0, rows in clusters:
        for row in range(-rows, rows + 1):
            offset = (dx / 2) if row % 2 else 0
            for col in range(-rows, rows + 1):
                cx = cx0 + col * dx + offset
                cy = cy0 + row * dy
                if not (-r * 2 < cx < SIZE + r * 2 and -r * 2 < cy < SIZE + r * 2):
                    continue
                draw.polygon(
                    _hexagon(cx, cy, r - 5),
                    fill=(*GOLD_SOFT, 90),
                    outline=(*GOLD, 120),
                    width=4,
                )

    img.alpha_composite(overlay)


def _paste_logo(img: Image.Image) -> int:
    """Loqonu sağ üstə yerləşdirir, altındakı sərbəst y-i qaytarır."""
    if not LOGO_PATH.exists():
        return MARGIN
    logo = Image.open(LOGO_PATH).convert("RGBA")
    h = round(logo.height * LOGO_W / logo.width)
    logo = logo.resize((LOGO_W, h), Image.LANCZOS)
    img.alpha_composite(logo, (SIZE - MARGIN - LOGO_W, 56))
    return 56 + h


def make_post(
    column: str,
    headline: str,
    body: str,
    cta: str = "Sifariş üçün DM yazın",
    out_path: str | Path = "albali/out/post.png",
) -> Path:
    """Bir feed postu (1:1) yaradır və faylın yolunu qaytarır."""
    if column not in COLUMNS:
        raise ValueError(f"Naməlum sütun: {column!r}. Mövcud: {sorted(COLUMNS)}")
    col = COLUMNS[column]

    img = Image.new("RGBA", (SIZE, SIZE), (*BG, 255))
    _draw_honeycomb(img)
    logo_bottom = _paste_logo(img)
    draw = ImageDraw.Draw(img)

    f_label = _font(FONT_BOLD, 34)
    f_head = _font(FONT_BOLD, 84)
    f_body = _font(FONT_REG, 44)
    f_cta = _font(FONT_BOLD, 38)
    f_handle = _font(FONT_REG, 32)

    text_w = SIZE - MARGIN * 2
    pad_x, pad_y = 34, 18
    pill_h = f_label.size + pad_y * 2
    gap_pill_head, gap_head_body = 54, 46

    content_h = (
        pill_h
        + gap_pill_head
        + _block_height(headline, f_head, text_w, 1.24)
        + gap_head_body
        + _block_height(body, f_body, text_w, 1.5)
    )
    zone_top = logo_bottom + 40
    zone_bottom = SIZE - 190
    y = zone_top + max(0, (zone_bottom - zone_top - content_h) // 2)

    # Sütun etiketi — mərkəzdə yaşıl/narıncı pill
    label = col.label
    lw = int(f_label.getlength(label))
    x0 = (SIZE - (lw + pad_x * 2)) // 2
    draw.rounded_rectangle(
        [x0, y, x0 + lw + pad_x * 2, y + pill_h], radius=pill_h // 2, fill=col.accent
    )
    draw.text((SIZE // 2, y + pad_y - 4), label, font=f_label, fill=WHITE, anchor="ma")
    y += pill_h + gap_pill_head

    # Başlıq — yaşıl, mərkəzdə
    y = _draw_centered(draw, headline, f_head, y, text_w, GREEN, 1.24)
    y += gap_head_body

    # Mətn — isti tünd, oxunaqlı
    _draw_centered(draw, body, f_body, y, text_w, INK, 1.5)

    # Alt sətir: çağırış + hesab adı
    draw.text((SIZE // 2, SIZE - 152), cta, font=f_cta, fill=ORANGE, anchor="ma")
    draw.text(
        (SIZE // 2, SIZE - 96), "@al.bali.az", font=f_handle, fill=GREEN_DEEP, anchor="ma"
    )

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, "PNG", optimize=True)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Al Balı post generatoru")
    parser.add_argument("--demo", action="store_true", help="nümunə postlar yarat")
    args = parser.parse_args()

    if args.demo:
        made = [
            make_post(
                "fakt",
                "1 kq bal üçün arılar\n4 milyon çiçək gəzir",
                "Bir arı ömrü boyu cəmi bir çay qaşığı bal hazırlayır.\n\n"
                "Laçın dağlarında, 2441 metr yüksəklikdə həmin çiçəklər "
                "kəklikotu, yovşan və dağ nanəsidir.",
                out_path=HERE / "out" / "nümunə-fakt.png",
            ),
            make_post(
                "kampaniya",
                "Avqust süzümünə\nsayılı günlər qaldı",
                "Keçən süzümdən stokda cəmi 30 kq bal qalıb.\n\n"
                "Yeni süzüm avqustun ortasında pətəkdən çıxacaq.",
                cta="Pre-order üçün DM yazın",
                out_path=HERE / "out" / "nümunə-kampaniya.png",
            ),
        ]
        for p in made:
            print(f"yaradıldı: {p}")


if __name__ == "__main__":
    main()
