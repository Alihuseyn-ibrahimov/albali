"""Composio API-nin dərc endpoint-ini YOXLAYIR (fərz etmir).

Serverdə işləyir. Açar `/opt/albali/.env`-dən oxunur, heç yerə çap edilmir.

    python3 /opt/albali/composio_probe.py

Nə edir: bir neçə ehtimal olunan endpoint formasını sınayır, hansının işlədiyini
tapır və @al.bali.az bağlantısının serverdən görünüb-görünmədiyini təsdiqləyir.
HEÇ NƏ DƏRC ETMİR — yalnız oxuma sorğuları göndərir.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV_PATH = Path("/opt/albali/.env")


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    if not ENV_PATH.exists():
        return env
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip("'\"")
    return env


def cagir(url: str, key: str, method: str = "GET", body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("x-api-key", key)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        govde = e.read().decode()[:400]
        return e.code, govde
    except Exception as e:  # şəbəkə/DNS
        return None, str(e)


def main() -> int:
    env = load_env()
    key = env.get("COMPOSIO_API_KEY")
    if not key:
        print(f"XƏTA: {ENV_PATH} faylında COMPOSIO_API_KEY yoxdur.", file=sys.stderr)
        return 1

    baza_namizedleri = [
        "https://backend.composio.dev/api/v3",
        "https://backend.composio.dev/api/v1",
    ]

    print("=== 1. Hansı baza URL cavab verir? ===")
    isleyen_baza = None
    for baza in baza_namizedleri:
        for yol in ("/connected_accounts", "/connectedAccounts"):
            status, cavab = cagir(f"{baza}{yol}", key)
            print(f"  {baza}{yol} -> {status}")
            if status == 200 and isleyen_baza is None:
                isleyen_baza = (baza, yol, cavab)

    if not isleyen_baza:
        print("\nHeç bir baza URL 200 vermədi. Açar yanlış ola bilər və ya API dəyişib.")
        return 1

    baza, yol, cavab = isleyen_baza
    print(f"\n✓ İşləyən baza: {baza}")

    print("\n=== 2. @al.bali.az bağlantısı görünürmü? ===")
    items = cavab.get("items") or cavab.get("data") or []
    if isinstance(items, dict):
        items = items.get("items", [])
    tapildi = False
    for it in items if isinstance(items, list) else []:
        toolkit = (it.get("toolkit") or {})
        ad = toolkit.get("slug") or it.get("appName") or it.get("appUniqueId")
        if ad and "instagram" in str(ad).lower():
            tapildi = True
            print(f"  ✓ instagram bağlantısı: id={it.get('id')} status={it.get('status')}")
    if not tapildi:
        print("  ✗ instagram bağlantısı tapılmadı — açar başqa hesaba aid ola bilər.")
        print(f"  (cəmi {len(items) if isinstance(items, list) else 0} bağlantı göründü)")

    print("\n=== 3. Dərc alətinin sxemi əlçatandırmı? ===")
    for yol_ in (
        "/tools/INSTAGRAM_POST_IG_USER_MEDIA",
        "/tools?tool_slugs=INSTAGRAM_POST_IG_USER_MEDIA",
    ):
        status, _ = cagir(f"{baza}{yol_}", key)
        print(f"  {baza}{yol_} -> {status}")

    print("\nNəticə: yuxarıdakı 200 qaytaran yollar dərc skriptində işlədiləcək.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
