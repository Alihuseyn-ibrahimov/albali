# Al Balı Bot — Vakansiya Postları (n8n workflow)

Bu qovluq "Al Balı Bot" (@albaliaz_bot) ilə bağlıdır. Vakansiya elanlarının
Notion → Telegram (təsdiq) → LinkedIn axını **kodla deyil, n8n workflow** ilə
idarə olunur (server: `n8n.prdostu.com`, workflow adı: **"LinkedIn - Vakansiya
Postları"**, ID: `SxpMFtGWuzuRbVPy`). Bu fayl həmin n8n workflow üçün qaydaları
sənədləşdirir ki, gələcək sessiyalar eyni səhvləri təkrarlamasın.

## Post formatı — MÜTLƏQ bu nümunəyə uyğun olsun

Hər **qurum (şirkət) üçün BİR post**, içində bütün vakansiyalar sıralanmış:

```
📢 VAKANSİYA

{Şirkət adı} aşağıdakı vakansiyalar üzrə işə qəbul elan edir:

1. {Vəzifə} - {Şöbə}
Təcrübə: {təcrübə tələbi, yoxdursa "Tələb olunmur"}
Təhsil tələbi: {ali təhsil/ixtisas tələbi, varsa}

2. {Vəzifə} - {Şöbə}
...

{Müraciət linki, varsa}
Son müraciət: {tarix}.
```

Qaydalar:
- **Sıralama**: vəzifə səviyyəsinə görə böyükdən kiçiyə — Baş (4) > Aparıcı (3) >
  Böyük (2) > digər/Mütəxəssis (1).
- **Bir qurum = bir post**. Eyni "Yeni" statuslu dövrədə bir neçə fərqli qurum
  varsa, hər qurum üçün AYRI post hazırlanır (heç vaxt bir postda qarışdırılmır).
- Post mətni **deterministik Code node ilə** qurulur (Notion sahələrindən birbaşa
  birləşdirmə) — LLM-ə (Groq) ehtiyac yoxdur, çünki mətn artıq Notion-da hazırdır,
  sadəcə format lazımdır.
- **Heç bir poster/şəkil yaradılmır.** Yalnız düz mətn Telegram-a göndərilir.

## Bilinən nasazlıq: Groq (LLM) mətn korrupsiyası

Əvvəllər tək-tək vakansiya üçün Groq (llama-3.3-70b-versatile) ilə LinkedIn
mətni generasiya edən addım var idi. Bu, Azərbaycan hərflərini (ə,ı,ö,ü,ş,ç,ğ)
transportda korrupt edib **çin yazısına bənzər simvollara** çevirirdi (məs.
"mütəxəssis" → "m眉t蓹x蓹ssis"). Kök səbəb konkret aşkarlanmayıb (server/HTTP
tərəfində UTF-8→GBK səhv decode ehtimalı), amma iki nəticə çıxarılıb:

1. **Mümkünsə LLM-dən (Groq) tam imtina et** — bu workflow üçün post mətni
   Notion sahələrindən deterministik şəkildə (Code node) qurulmalıdır, LLM-ə
   ehtiyac yoxdur.
2. Əgər gələcəkdə hər hansı səbəbdən yenidən LLM istifadə olunacaqsa, xüsusi
   hərfləri JSON-da ASCII placeholder kodlarla göndərtdirib (məs. `[e2]`→ə,
   `[i1]`→ı, `[o2]`→ö, `[u2]`→ü, `[s2]`→ş, `[c2]`→ç, `[g2]`→ğ, böyük hərflər
   üçün `[E2] [I1] [O2] [U2] [S2] [C2] [G2]`), sonra Code/Set node-da
   `.split(kod).join(hərf)` ilə geri çevirmək lazımdır — çünki bu ASCII kodlar
   transportda korrupt olmur. `\uXXXX` JSON escape formatı işləmədi (LLM
   düzgün icra etmədi/instruksiyanı ötürmək texniki cəhətdən çətin oldu).

## Digər qərarlar

- Poster/şəkil generasiyası (`li-image/generate` xarici servisi) workflow-dan
  tamamilə çıxarılıb — nə Telegram-a, nə LinkedIn-ə şəkil getmir, sırf mətn.
- Notion "Vakansiyalar" bazasında Status axını:
  `Yeni` → (post Telegram-a göndərilən kimi n8n avtomatik `Emal olunur` yazır)
  → təsdiqdən sonra `Paylaşıldı` / `İmtina edildi`.
- **Təkrar göndərmənin qarşısını alma:** post Telegram-a düşən kimi həmin
  qrupun bütün səhifələri `Emal olunur`-a keçirilir ("Təsdiqi Yadda Saxla" →
  "PageId Siyahısı (Gözləmə)" → "Status Dövrü (Gözləmə)" → "Statusu Yaz
  (Gözləmə)" node zənciri). Workflow yalnız `Status = Yeni` olanları tutduğu
  üçün növbəti 15-dəqiqəlik dövrədə həmin post TƏKRAR gəlmir — istifadəçi
  təsdiqi istədiyi vaxt, tələsmədən verə bilər.
- **Statusu əl ilə dəyişmə.** `Emal olunur` = "Telegram-da təsdiq gözləyir"
  deməkdir; onu əl ilə `Yeni`-yə qaytarmaq postun təkrar göndərilməsinə səbəb
  olur.
- Schedule Trigger node ("Cədvəl (15 dəq)") hər 15 dəqiqədən bir Notion-u
  yoxlayır, `Yeni` olanları avtomatik emal edir — əl ilə işə salmağa ehtiyac
  yoxdur, amma test üçün `execute_workflow` (production mode) ilə dərhal
  tetiklənə bilər.
