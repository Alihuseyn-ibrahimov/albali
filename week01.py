"""Al Balı — 1-ci həftənin kontent paketi (2026-08-01 … 2026-08-07).

İşlətmə:
    py -3 albali/week01.py

Nə edir:
  1. 7 postun şəklini `albali/out/hefte-01/` qovluğuna yazır (1080x1350 PNG —
     Instagram-a bu fayllar gedəcək)
  2. Təsdiq üçün `albali/out/hefte-01/tesdiq.html` səhifəsini qurur
     (şəkillər base64 ilə içəridədir, brauzerdə açılır)

Qrammatika düzəlişindən sonra `POSTS` siyahısını dəyiş və skripti yenidən işlət.
"""

from __future__ import annotations

import base64
import html
import io
from datetime import date, timedelta
from pathlib import Path

from PIL import Image

from post_generator import COLUMNS, make_post

OUT_DIR = Path(__file__).parent / "out" / "hefte-01"
START = date(2026, 8, 1)

WEEKDAYS_AZ = [
    "bazar ertəsi",
    "çərşənbə axşamı",
    "çərşənbə",
    "cümə axşamı",
    "cümə",
    "şənbə",
    "bazar",
]
MONTHS_AZ = {8: "avqust"}

# --- Hashtag dəstləri -----------------------------------------------------

TAGS_MAARIF = (
    "#bal #təbiibal #dağbalı #balınfaydaları #sağlamqidalanma #arıçılıq "
    "#təbiiməhsul #laçın #azərbaycan #honey"
)
TAGS_SATIS = (
    "#bal #balsifarişi #təbiibal #laçınbalı #pətəkbalı #şanıbal #dağbalı "
    "#bakı #azərbaycan #onlinesifariş"
)
TAGS_HEKAYE = (
    "#laçın #oğuldərə #qarabağ #laçınbalı #arıçılıq #dağbalı #təbiibal "
    "#azərbaycan #doğmatorpaq #honey"
)


# --- Həftənin kontenti ----------------------------------------------------
# Hər post: sütun, şəkil başlığı, şəkil mətni, CTA, caption, hashtaglar.
# `yoxla` — istifadəçinin arıçı kimi təsdiqləməli olduğu iddia.

POSTS: list[dict] = [
    {
        "column": "fakt",
        "headline": "Bal xarab olmayan\nyeganə qidadır",
        "body": (
            "Misir piramidalarında tapılan 3000 illik bal hələ də yeməli olub.\n\n"
            "Səbəbi: balda su az, turşuluq isə yüksəkdir — bakteriya belə "
            "mühitdə yaşaya bilmir."
        ),
        "cta": "Sifariş üçün DM yazın",
        "caption": (
            "Arxeoloqlar Misir piramidalarında 3000 il əvvələ aid bal küpləri "
            "tapıblar — və o bal hələ də xarab olmamışdı. 🍯\n\n"
            "Bunun sirri sadədir: balın tərkibində su çox azdır, turşuluğu isə "
            "yüksəkdir. Bakteriya belə mühitdə yaşaya bilmir. Yəni bal "
            "özü-özünü qoruyur.\n\n"
            "Bir şərtlə — bala su və ya nəm qarışmasın. Ona görə balı həmişə "
            "quru qaşıqla götürün və qapağını bərk bağlayın.\n\n"
            "Laçın dağlarından gələn balımız da elə belədir: təmiz saxlansa, "
            "illərlə dadını itirmir.\n\n"
            "Sifariş üçün DM yazın 📩"
        ),
        "tags": TAGS_MAARIF,
        "yoxla": "Misir piramidalarındakı 3000 illik bal iddiası — geniş yayılıb, "
        "amma postda yazmazdan əvvəl təsdiqləməyini istəyirəm.",
    },
    {
        "column": "hekaye",
        "headline": "Bu balın arxasında\nbir qayıdış var",
        "body": (
            "Oğuldərə — Laçının dağ kəndi. Uzun illərdən sonra bu yamaclarda "
            "yenidən arı pətəkləri quruldu.\n\n"
            "Hər bankanın arxasında torpağa qayıdış dayanır."
        ),
        "cta": "Sifariş üçün DM yazın",
        "caption": (
            "Oğuldərə — Laçın dağlarında, dəniz səviyyəsindən 2441 metr "
            "yüksəklikdə bir kənd. ⛰️\n\n"
            "Uzun illər bu yamaclarda arı pətəyi yox idi. İndi yenidən var.\n\n"
            "Al Balı bizim üçün sadəcə məhsul deyil — doğma torpağa qayıdışın "
            "kiçik bir nişanəsidir. Hər banka balın arxasında o yamaclarda "
            "keçən yay, çiçək qoxusu və zəhmət dayanır.\n\n"
            "Balın dadı qədər, hardan gəldiyi də önəmlidir.\n\n"
            "Sifariş üçün DM yazın 📩"
        ),
        "tags": TAGS_HEKAYE,
        "yoxla": None,
    },
    {
        "column": "kampaniya",
        "headline": "Avqust süzümünə\nsayılı günlər qaldı",
        "body": (
            "Keçən süzümdən stokda cəmi 30 kq bal qalıb.\n\n"
            "Yeni süzüm avqustun ortasında pətəkdən çıxacaq. Sifarişinizi "
            "indidən qeyd etdirin."
        ),
        "cta": "Pre-order üçün DM yazın",
        "caption": (
            "Arılarımız yayı Laçın yamaclarında keçirdi — avqust süzümünə "
            "sayılı günlər qalıb. 🐝\n\n"
            "İki xəbərimiz var:\n\n"
            "🍯 Keçən süzümdən stokda cəmi 30 kq bal qalıb. Bitəndən sonra "
            "yeni süzümü gözləmək lazım gələcək.\n"
            "🍯 Yeni süzüm avqustun ortasında pətəkdən çıxır. İstəyənlər "
            "sifarişini indidən qeyd etdirə bilər.\n\n"
            "Pre-order verənlərin sifarişi süzüm bitən kimi ilk növbədə "
            "göndəriləcək.\n\n"
            "Sifariş və pre-order üçün DM yazın 📩"
        ),
        "tags": TAGS_SATIS,
        "yoxla": "30 kq və «avqustun ortası» rəqəmləri sənin verdiyin "
        "məlumatdır — postda açıq yazılır, dəqiqliyini bir daha yoxla.",
    },
    {
        "column": "mif",
        "headline": "Şanı bal həmişə\nsüzmə baldan\nyaxşıdır?",
        "body": (
            "Yanlış. İkisi də eyni pətəkdən gəlir — fərq yalnız formadadır.\n\n"
            "Şanı bal mumu ilə birlikdə, süzmə bal isə mumdan ayrılmış halda "
            "olur."
        ),
        "cta": "Sifariş üçün DM yazın",
        "caption": (
            "❓ Ən çox soruşulan sual: şanı (pətək) bal süzmə baldan daha "
            "keyfiyyətlidir?\n\n"
            "Cavab: xeyr. İkisi də eyni pətəkdən, eyni arılardan gəlir. "
            "Fərq yalnız formadadır.\n\n"
            "🍯 Şanı bal — pətəkdən çıxdığı kimi, mumu ilə birlikdə. Mumu da "
            "yeyilir.\n"
            "🍯 Süzmə bal — həmin bal, mumdan ayrılmış halda. Çaya qatmaq və "
            "yeməkdə işlətmək üçün rahatdır.\n\n"
            "Yəni seçim keyfiyyət məsələsi deyil — zövq və istifadə "
            "məsələsidir.\n\n"
            "Siz hansını seçirsiniz, şanı yoxsa süzmə? Şərhdə yazın 👇\n\n"
            "Sifariş üçün DM yazın 📩"
        ),
        "tags": TAGS_MAARIF,
        "yoxla": "Arıçı kimi bu izahı təsdiqlə — şanı və süzmə bal arasındakı "
        "fərqi biz belə izah edirik, sən başqa cür deyirsənsə dəyişək.",
    },
    {
        "column": "fakt",
        "headline": "Siz balı necə\nişlədirsiniz?",
        "body": (
            "Kimisi səhər çörəklə yeyir, kimisi ilıq çaya qatır, kimisi "
            "soyuqdəymədə limonla qarışdırır.\n\n"
            "Sizin üsulunuz hansıdır?"
        ),
        "cta": "Şərhdə yazın",
        "caption": (
            "Balın min bir işlədilmə yolu var. 🍯\n\n"
            "Müştərilərimiz arasında ən çox rast gəldiyimiz üç üsul:\n\n"
            "1️⃣ Səhər çörək və yağla — ən klassiki\n"
            "2️⃣ İlıq çaya qatmaq (qaynar yox — qaynar su balın faydasını "
            "azaldır)\n"
            "3️⃣ Soyuqdəymədə limon və zəncəfillə birlikdə\n\n"
            "Bəs siz? Balı ən çox necə işlədirsiniz — şərhdə yazın, ən maraqlı "
            "üsulu növbəti postda paylaşacağıq 👇\n\n"
            "Sifariş üçün DM yazın 📩"
        ),
        "tags": TAGS_MAARIF,
        "yoxla": None,
    },
    {
        "column": "mehsul",
        "headline": "İki formada,\nüç ölçüdə",
        "body": (
            "Şanı (pətək) bal və süzmə bal — 250 qr, 500 qr və 1 kq "
            "qablaşdırmalarda.\n\n"
            "Metrolara çatdırılma ödənişsizdir."
        ),
        "cta": "Qiymət üçün DM yazın",
        "caption": (
            "Al Balı iki formada və üç ölçüdə təqdim olunur: 🍯\n\n"
            "🐝 Şanı (pətək) bal — pətəkdən çıxdığı kimi, mumu ilə\n"
            "🐝 Süzmə bal — mumdan ayrılmış, axıcı\n\n"
            "Hər ikisi 250 qr, 500 qr və 1 kq qablaşdırmalarda mövcuddur.\n\n"
            "📍 Metrolara çatdırılma ödənişsizdir.\n"
            "🍯 Hazırda stokda 30 kq bal var, avqust süzümü isə ayın ortasında "
            "gəlir.\n\n"
            "Qiymət və sifariş üçün DM yazın 📩"
        ),
        "tags": TAGS_SATIS,
        "yoxla": "Qablaşdırma ölçüləri köhnə postlarınızdan götürülüb "
        "(250 qr / 500 qr / 1 kq) — hələ də doğrudurmu? Qiymət qərara uyğun "
        "olaraq postda yazılmır, yalnız DM-də verilir.",
    },
    {
        "column": "fakt",
        "headline": "2441 metr\nniyə fərq yaradır?",
        "body": (
            "Yüksək dağ çəmənlərində çiçək növü daha çoxdur, kənd təsərrüfatı "
            "kimyası isə yoxdur.\n\n"
            "Balın ətri və dadı birbaşa buradan gəlir."
        ),
        "cta": "Sifariş üçün DM yazın",
        "caption": (
            "Balın dadı arıdan yox, çiçəkdən gəlir. 🌿\n\n"
            "Arılarımız Laçında, 2441 metr yüksəklikdə işləyir. Bu hündürlükdə "
            "iki şey dəyişir:\n\n"
            "🪻 Çiçək müxtəlifliyi artır — kəklikotu, yovşan, dağ nanəsi və "
            "adını belə bilmədiyimiz onlarla dağ çiçəyi\n"
            "🚫 Kənd təsərrüfatı kimyası yoxdur — nə dərman, nə gübrə\n\n"
            "Ona görə dağ balının ətri daha güclü, dadı daha mürəkkəb olur. "
            "Bir qaşıq balda bütöv bir yamacın qoxusu var.\n\n"
            "Sifariş üçün DM yazın 📩"
        ),
        "tags": TAGS_HEKAYE,
        "yoxla": "Çiçək adlarını (kəklikotu, yovşan, dağ nanəsi) təsdiqlə — "
        "Oğuldərə yamaclarında həqiqətən bunlar varmı?",
    },
]


def _date_label(d: date) -> str:
    return f"{d.day} {MONTHS_AZ[d.month]}, {WEEKDAYS_AZ[d.weekday()]}"


def _preview_data_uri(png_path: Path, width: int = 520, quality: int = 80) -> str:
    """Şəkli kiçildib JPEG data URI-yə çevirir (təsdiq səhifəsi üçün)."""
    img = Image.open(png_path).convert("RGB")
    ratio = width / img.width
    img = img.resize((width, round(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _card(index: int, post: dict, png_path: Path) -> str:
    d = START + timedelta(days=index)
    label = COLUMNS[post["column"]].label
    caption = html.escape(post["caption"]).replace("\n", "<br>")
    tags = html.escape(post["tags"])
    check = ""
    if post["yoxla"]:
        check = (
            '<p class="check"><span class="check-label">Təsdiqini gözləyir</span>'
            f'{html.escape(post["yoxla"])}</p>'
        )
    char_count = len(post["caption"]) + len(post["tags"]) + 2
    return f"""
<article class="day" id="gun-{index + 1}">
  <header class="day-head">
    <span class="day-num">{index + 1}</span>
    <div class="day-meta">
      <h2>{html.escape(_date_label(d))}</h2>
      <span class="pillar">{html.escape(label)}</span>
    </div>
  </header>
  <div class="day-body">
    <figure class="shot">
      <img src="{_preview_data_uri(png_path)}" alt="{html.escape(post['headline'])}">
      <figcaption>{html.escape(png_path.name)} · 1080×1350</figcaption>
    </figure>
    <div class="copy">
      <h3 class="copy-label">Caption</h3>
      <p class="caption">{caption}</p>
      <p class="tags">{tags}</p>
      <p class="count">{char_count} simvol · Instagram limiti 2200</p>
      {check}
    </div>
  </div>
</article>"""


TEMPLATE = """<title>Al Balı — 1-ci həftənin kontenti</title>
<style>
  :root {
    --ground: #FAF8F4;
    --surface: #FFFFFF;
    --ink: #241F18;
    --muted: #6F665A;
    --rule: #E4DCCE;
    --accent: #9C6B14;
    --flag-bg: #F6EADC;
    --flag-ink: #8A4118;
    --shadow: 0 1px 2px rgba(36, 31, 24, .06), 0 8px 24px rgba(36, 31, 24, .05);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --ground: #16130E;
      --surface: #1F1B15;
      --ink: #EFE8DA;
      --muted: #9C9284;
      --rule: #342D23;
      --accent: #D9A340;
      --flag-bg: #2B2015;
      --flag-ink: #E0A277;
      --shadow: 0 1px 2px rgba(0, 0, 0, .4), 0 8px 24px rgba(0, 0, 0, .3);
    }
  }
  :root[data-theme="light"] {
    --ground: #FAF8F4; --surface: #FFFFFF; --ink: #241F18; --muted: #6F665A;
    --rule: #E4DCCE; --accent: #9C6B14; --flag-bg: #F6EADC; --flag-ink: #8A4118;
    --shadow: 0 1px 2px rgba(36, 31, 24, .06), 0 8px 24px rgba(36, 31, 24, .05);
  }
  :root[data-theme="dark"] {
    --ground: #16130E; --surface: #1F1B15; --ink: #EFE8DA; --muted: #9C9284;
    --rule: #342D23; --accent: #D9A340; --flag-bg: #2B2015; --flag-ink: #E0A277;
    --shadow: 0 1px 2px rgba(0, 0, 0, .4), 0 8px 24px rgba(0, 0, 0, .3);
  }

  body {
    background: var(--ground);
    color: var(--ink);
    font: 400 17px/1.6 Georgia, "Times New Roman", serif;
    padding: 0 24px 96px;
  }
  .wrap { max-width: 1000px; margin: 0 auto; }

  .label {
    font: 600 12px/1 -apple-system, "Segoe UI", system-ui, sans-serif;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
  }

  /* --- intro --- */
  .intro { padding: 72px 0 40px; border-bottom: 1px solid var(--rule); }
  .intro h1 {
    font-size: clamp(30px, 5vw, 46px);
    line-height: 1.12;
    font-weight: 400;
    text-wrap: balance;
    margin: 14px 0 20px;
  }
  .intro p { color: var(--muted); max-width: 62ch; margin-bottom: 14px; }
  .intro strong { color: var(--ink); font-weight: 700; }

  .facts {
    display: flex; flex-wrap: wrap; gap: 8px 28px;
    margin-top: 28px; padding-top: 22px; border-top: 1px solid var(--rule);
    font: 400 15px/1.5 -apple-system, "Segoe UI", system-ui, sans-serif;
    color: var(--muted);
  }
  .facts b {
    color: var(--ink); font-weight: 600;
    font-variant-numeric: tabular-nums;
  }

  /* --- day card --- */
  .day {
    background: var(--surface);
    border: 1px solid var(--rule);
    border-radius: 4px;
    box-shadow: var(--shadow);
    margin-top: 40px;
    overflow: hidden;
  }
  .day-head {
    display: flex; align-items: baseline; gap: 18px;
    padding: 22px 28px;
    border-bottom: 1px solid var(--rule);
  }
  .day-num {
    font: 700 15px/1 -apple-system, "Segoe UI", system-ui, sans-serif;
    font-variant-numeric: tabular-nums;
    color: var(--accent);
    border: 1.5px solid var(--accent);
    border-radius: 50%;
    width: 30px; height: 30px;
    display: grid; place-items: center;
    flex: none;
  }
  .day-meta { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px; }
  .day-meta h2 { font-size: 21px; font-weight: 400; }
  .pillar {
    font: 600 11px/1 -apple-system, "Segoe UI", system-ui, sans-serif;
    letter-spacing: .1em; text-transform: uppercase;
    color: var(--accent);
    border: 1px solid var(--rule);
    border-radius: 3px;
    padding: 5px 8px;
  }

  .day-body {
    display: grid;
    grid-template-columns: minmax(0, 260px) minmax(0, 1fr);
    gap: 32px;
    padding: 28px;
    align-items: start;
  }
  .shot img {
    width: 100%; height: auto; display: block;
    border-radius: 3px;
    border: 1px solid var(--rule);
  }
  .shot figcaption {
    margin-top: 10px;
    font: 400 12px/1.4 ui-monospace, "Cascadia Mono", Consolas, monospace;
    color: var(--muted);
    word-break: break-all;
  }

  .copy { display: flex; flex-direction: column; gap: 16px; min-width: 0; }
  .copy-label {
    font: 600 12px/1 -apple-system, "Segoe UI", system-ui, sans-serif;
    letter-spacing: .12em; text-transform: uppercase; color: var(--muted);
  }
  .caption {
    font-size: 17px; line-height: 1.65;
    max-width: 60ch;
  }
  .tags {
    font: 400 14px/1.7 -apple-system, "Segoe UI", system-ui, sans-serif;
    color: var(--accent);
    word-spacing: .18em;
    max-width: 60ch;
  }
  .count {
    font: 400 13px/1 -apple-system, "Segoe UI", system-ui, sans-serif;
    font-variant-numeric: tabular-nums;
    color: var(--muted);
  }
  .check {
    background: var(--flag-bg);
    color: var(--flag-ink);
    border-left: 3px solid currentColor;
    padding: 14px 16px;
    font-size: 15.5px; line-height: 1.55;
    max-width: 60ch;
  }
  .check-label {
    display: block;
    font: 700 11px/1 -apple-system, "Segoe UI", system-ui, sans-serif;
    letter-spacing: .1em; text-transform: uppercase;
    margin-bottom: 7px;
  }

  .outro {
    margin-top: 56px; padding-top: 28px;
    border-top: 1px solid var(--rule);
    color: var(--muted);
    font-size: 15.5px;
    max-width: 62ch;
  }
  .outro h2 {
    font-size: 20px; font-weight: 400; color: var(--ink); margin-bottom: 12px;
  }
  .outro li { margin: 0 0 8px 20px; }
  .outro code {
    font: 400 13.5px/1 ui-monospace, "Cascadia Mono", Consolas, monospace;
    color: var(--accent);
    background: var(--flag-bg);
    padding: 2px 5px; border-radius: 3px;
  }

  @media (max-width: 760px) {
    body { padding: 0 18px 72px; }
    .day-body { grid-template-columns: minmax(0, 1fr); gap: 24px; padding: 22px; }
    .shot { max-width: 300px; }
  }
</style>

<div class="wrap">
  <section class="intro">
    <span class="label">Al Balı · təsdiq üçün</span>
    <h1>1-ci həftənin kontenti</h1>
    <p>Aşağıdakı yeddi post <strong>hələ dərc olunmayıb</strong>. Şəkilləri
      və mətnləri oxu, qrammatika səhvi və ya dəyişmək istədiyin yer varsa de —
      düzəldib yenidən göndərəcəm. Təsdiqdən sonra hər gün bir post
      paylaşılacaq.</p>
    <p>Qumral çərçivəli qeydlər <strong>sənin təsdiqini gözləyən iddialardır</strong>.
      Arıçı sənsən — mən uydurma rəqəm və ya fakt yazmaq istəmirəm.</p>
    <div class="facts">
      <span><b>7</b> post</span>
      <span><b>1&nbsp;–&nbsp;7 avqust</b></span>
      <span>sifariş kanalı <b>yalnız DM</b></span>
      <span>stok <b>30 kq</b></span>
      <span>başlanğıc <b>328 izləyici</b></span>
    </div>
  </section>

  {{CARDS}}

  <section class="outro">
    <h2>Bu həftədə çatışmayan nə var</h2>
    <ul>
      <li><b>Real müştəri rəyi.</b> «Sosial sübut» sütunu üçün 2-3 həqiqi müştəri
        mesajı lazımdır. Uydurma rəy yazmıram — sən göndərsən, 2-ci həftəyə
        salarıq.</li>
      <li><b>Qiymət postlarda yazılmır</b> — sənin qərarın. Süzmə 1 kq 50 ₼,
        şanı 1 kq 70 ₼, kiçik qablaşdırmalar qrama mütənasib. Cavablar
        <code>albali/dm_cavablari.md</code> faylında hazırdır. Tək qeyd: 250 qr
        variantları 12.50 ₼ və 17.50 ₼ çıxır — yuvarlaqlaşdırmaq istəyirsənsə de.</li>
      <li><b>Təsərrüfatdan canlı kadr.</b> Bir dənə də olsa yeni foto/video
        göndərə bilsən, həftədə bir dəfə dizayn əvəzinə real kadr işlədərik —
        bu, etibarı ciddi artırır.</li>
    </ul>
  </section>
</div>
"""


def build() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cards = []
    for i, post in enumerate(POSTS):
        d = START + timedelta(days=i)
        png = OUT_DIR / f"{d:%m-%d}-{post['column']}.png"
        make_post(
            column=post["column"],
            headline=post["headline"],
            body=post["body"],
            cta=post["cta"],
            out_path=png,
        )
        cards.append(_card(i, post, png))
        print(f"şəkil: {png.name}")

    page = OUT_DIR / "tesdiq.html"
    page.write_text(TEMPLATE.replace("{{CARDS}}", "\n".join(cards)), encoding="utf-8")
    print(f"təsdiq səhifəsi: {page}")
    return page


if __name__ == "__main__":
    build()
