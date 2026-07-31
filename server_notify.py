"""Al Balı gündəlik post bildirişi — SERVERDƏ işləyir (cron ilə).

Yer: /opt/albali/notify.py (68.183.210.59)
Cron: hər gün 20:25 (server UTC-dədir, Bakı = UTC+4 → cron 25 16)

Nə edir:
  1. `schedule.json`-dan bugünkü postu tapır
  2. Şəkli və caption mətnini Telegram-a göndərir (kopyalayıb dərc etmək üçün)
  3. Nəticəni loga yazır

Telegram açarı `/opt/albali/.env`-dən oxunur — koda YAZILMIR.
Gözlənilən dəyişənlər:
    ALBALI_TELEGRAM_TOKEN    — Laçın hava botu (ayrıca bot, PR monitorinq botu DEYİL)
    ALBALI_TELEGRAM_CHAT_ID  — hədəf çat (`--cat-tap` ilə tapıla bilər)

Çat id-ni tapmaq üçün: telefondan həmin bota istənilən mesaj yaz, sonra serverdə
    python3 /opt/albali/notify.py --cat-tap
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta, timezone
from datetime import datetime
from pathlib import Path

BASE = Path("/opt/albali")
ENV_PATH = BASE / ".env"
SCHEDULE = BASE / "schedule.json"
MEDIA = BASE / "media"
BAKU = timezone(timedelta(hours=4))
API = "https://api.telegram.org/bot{token}/{method}"


def _load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip("'\"")
    return env


def _post(token: str, method: str, fields: dict[str, str], file: Path | None = None):
    """Telegram API çağırışı. Fayl varsa multipart, yoxsa sadə form."""
    url = API.format(token=token, method=method)
    if file is None:
        data = urllib.parse.urlencode(fields).encode()
        req = urllib.request.Request(url, data=data)
    else:
        boundary = "----albali-boundary-7f3a"
        parts: list[bytes] = []
        for k, v in fields.items():
            parts.append(
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
            )
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; '
            f'filename="{file.name}"\r\nContent-Type: image/jpeg\r\n\r\n'.encode()
        )
        parts.append(file.read_bytes())
        parts.append(f"\r\n--{boundary}--\r\n".encode())
        body = b"".join(parts)
        req = urllib.request.Request(url, data=body)
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def bugunku_post(plan: list[dict], bu_gun: date) -> dict | None:
    for item in plan:
        if item["tarix"] == bu_gun.isoformat():
            return item
    return None


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Al Balı gündəlik post bildirişi")
    ap.add_argument(
        "--tarix",
        help="YYYY-MM-DD — bugünkü tarix əvəzinə bu günün postunu göndər (test/təkrar üçün)",
    )
    ap.add_argument(
        "--cat-tap",
        action="store_true",
        help="bota yazılmış son mesajlardan çat id-lərini tap və çap et",
    )
    args = ap.parse_args()

    env = _load_env(ENV_PATH)
    token = env.get("ALBALI_TELEGRAM_TOKEN")
    if not token:
        print(
            f"XƏTA: {ENV_PATH} faylında ALBALI_TELEGRAM_TOKEN yoxdur.\n"
            "Bildiriş göndərilmədi — PR monitorinq botu qəsdən işlədilmir.",
            file=sys.stderr,
        )
        return 1

    if args.cat_tap:
        r = json.loads(
            urllib.request.urlopen(
                API.format(token=token, method="getUpdates"), timeout=30
            )
            .read()
            .decode()
        )
        me = json.loads(
            urllib.request.urlopen(API.format(token=token, method="getMe"), timeout=30)
            .read()
            .decode()
        ).get("result", {})
        print(f"bot: @{me.get('username')}")
        taplilar = {}
        for u in r.get("result", []):
            msg = u.get("message") or u.get("channel_post") or {}
            c = msg.get("chat") or {}
            if c.get("id"):
                taplilar[c["id"]] = f"{c.get('type')} · {c.get('title') or c.get('first_name')}"
        if not taplilar:
            print("Çat tapılmadı — telefondan bota bir mesaj yaz, sonra təkrar işlət.")
            return 1
        for cid, tesvir in taplilar.items():
            print(f"ALBALI_TELEGRAM_CHAT_ID={cid}   ({tesvir})")
        return 0

    chat_id = env.get("ALBALI_TELEGRAM_CHAT_ID")
    if not chat_id:
        print(
            f"XƏTA: {ENV_PATH} faylında ALBALI_TELEGRAM_CHAT_ID yoxdur.\n"
            "Tapmaq üçün: python3 /opt/albali/notify.py --cat-tap",
            file=sys.stderr,
        )
        return 1

    if not SCHEDULE.exists():
        print(f"XƏTA: cədvəl yoxdur — {SCHEDULE}", file=sys.stderr)
        return 1

    plan = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    bu_gun = date.fromisoformat(args.tarix) if args.tarix else datetime.now(BAKU).date()
    post = bugunku_post(plan, bu_gun)
    if post is None:
        print(f"{bu_gun} üçün post yoxdur — cədvəl bitib. Yeni həftə lazımdır.")
        # Cədvəl bitibsə xatırlatma göndər ki, səssizcə dayanmasın.
        _post(
            token,
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": (
                    f"🍯 Al Balı — {bu_gun} üçün planda post yoxdur.\n\n"
                    "Kontent cədvəli bitib. Növbəti həftənin postlarını hazırlamaq lazımdır."
                ),
            },
        )
        return 0

    sekil = MEDIA / post["sekil"]
    basliq = (
        f"🍯 <b>Al Balı — bugünkü post</b>\n"
        f"{post['gun']} · {post['sutun']}\n\n"
        f"Şəkli yüklə, mətni kopyala və Instagram-da paylaş."
    )

    if sekil.exists():
        r = _post(
            token,
            "sendPhoto",
            {"chat_id": chat_id, "caption": basliq, "parse_mode": "HTML"},
            file=sekil,
        )
    else:
        r = _post(
            token,
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": basliq + f"\n\n⚠️ Şəkil tapılmadı: {post['sekil']}",
                "parse_mode": "HTML",
            },
        )
    if not r.get("ok"):
        print(f"XƏTA (şəkil): {r}", file=sys.stderr)
        return 1

    # Caption ayrıca mesajda — kopyalamaq üçün təmiz olsun deyə.
    r2 = _post(token, "sendMessage", {"chat_id": chat_id, "text": post["caption"]})
    if not r2.get("ok"):
        print(f"XƏTA (caption): {r2}", file=sys.stderr)
        return 1

    print(f"OK — {bu_gun} postu göndərildi ({post['sekil']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
