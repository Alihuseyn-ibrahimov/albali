"""Al Balı gündəlik post bildirişi — SERVERDƏ işləyir (cron ilə).

Yer: /opt/albali/notify.py (68.183.210.59)
Cron: hər gün 20:25 (server UTC-dədir, Bakı = UTC+4 → cron 25 16)

Nə edir:
  1. `schedule.json`-dan bugünkü postu tapır
  2. Şəkli və caption mətnini Telegram-a göndərir (kopyalayıb dərc etmək üçün)
  3. Nəticəni loga yazır

Telegram açarı `/opt/saas_core/.env`-dən oxunur — koda YAZILMIR.
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
ENV_PATH = Path("/opt/saas_core/.env")
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
    args = ap.parse_args()

    env = _load_env(ENV_PATH)
    token = env.get("TELEGRAM_TOKEN")
    chat_id = env.get("TELEGRAM_ALERT_CHAT_ID") or env.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("XƏTA: TELEGRAM_TOKEN və ya chat id tapılmadı", file=sys.stderr)
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
