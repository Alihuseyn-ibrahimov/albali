# Al Balı — Instagram kontent generatoru

Brend üçün Instagram postlarını avtomatik yaradan alət. Rəng palitrası və loqo
brendin mövcud postlarından götürülür ki, yeni paylaşımlar lentlə uyğun olsun.

## Əsas imkanlar
- **Post vizual generatoru** (`post_generator.py`) — brend rəngləri və loqosu ilə 1:1 və 4:5 formatlı şəkillər
- **Həftəlik kontent paketi** (`week01.py`) — 7 günlük postlar + təsdiq üçün HTML səhifə
- **DM cavab şablonları** (`dm_cavablari.md`)
- Server bildirişləri (`server_notify.py`)

## Texnologiyalar
Python · Pillow

## İşə salma
```bash
pip install pillow
python post_generator.py --demo
python week01.py
```
