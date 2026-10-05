# Tasarım tutarlılık incelemesi

Tarih: 2026-10-02. İncelenen çıktı mimari ve uygulama planıdır; ürün geliştirmesinin tamamlandığı iddia edilmez. Bu inceleme spec-kit analysis biçimindeki tutarlılık kontrolüdür; bir `/speckit-analyze` komutunun çalıştırıldığı iddiası değildir.

## Sonuç

24 gereksinim, 40 kabul senaryosu ve 4 feature dilimi arasında kapsam bağlantısı kuruldu. Görev sayıları: ortak başlangıç 2, V1 13, V2 10, V3 8, V4 7; toplam 40. Her feature üç hikâye sınırı ve kırktan az görev şartı içindedir.

Native LightBurn uyumluluğu bilinen bir yazılım özelliği gibi varsayılmadı. G02/C05/D04 gerçek uygulama kanıtları için açık görevlerdir. PDF ilk kapsama alındı; yerel dar renderer denemesi ile desteklendi. Bu karar, PDF vektör import'u gerektirmiyor.

## Çözülen tasarım noktaları

| Konu | Son karar |
|---|---|
| Gerber bağımlılığı | Dosya tabanlı görsel akışı bağımsız; Gerber ek kaynak |
| SVG ile raster aynı mı | Kaynaklar farklı okunur, tek ana maskede birleşir |
| Kaynak mı çıktı mı birebir | Split eşitliği son ana maskeye göre; kaynak render testi ayrı |
| Fiziksel ölçü ve DPI tam bölünmüyor | İçeriği esnetmeden ceil canvas ve açık padding |
| Boş satır/group | İndeks korunur; boş group planlı fakat Output kapalı |
| Üst üste birleştirme | Bool kazıma maskesi OR'u; opak resim alpha overlay'i değil |
| N=1 uyumluluğu | Maskede birebir eşitlik; mevcut olmayan legacy raster byte eşitliği iddiası yok |
| Karışık sıra | Sabit bit tersleme; rastgele veya termal olarak optimal iddiası yok |
| Birden fazla tur | Bütün gruplar tamamlanıp tekrar başlar; katman başına tekrar değil |
| Yön ve beyaz satır atlama | Mantıksal plan ile gerçek LightBurn yürütümü ayrıldı; capability testleri |
| Bekleme | Gerçek native destek yoksa reddet; kayıtta koru |
| Kaynak taşınması | Kaynak bytes ve ana maske recipe'de gömülü |
| Yeniden açmada farklı renderer | Ana maske yeniden çizilmez; ayar değişikliği açık yeniden üretim |
| Aynı maskede değişen DPI | Maske hash'i yanında grid ve revision eşleşmesi gerekir |

## Gerçekleştirilen belge ve örnek kontrolleri

- Bütün yerel Markdown bağlantılarının hedefleri kontrol edildi; kırık link bulunmadı.
- Markdown code fence'leri dengeli; doldurulmamış şablon alanı bulunmuyor.
- `contracts/reference-cases.json` parse edildi ve partition/mixed sıra/tur/dwell/ölçü örnekleri matematiksel olarak doğrulandı.
- N=1..8 için H=0..1024 ve beş ilave H değeri üzerinden toplam 8240 partition örneğinde eksik/çift satır olmadığı doğrulandı.
- Ayrıca 40 farklı N/boyut örneğinde sentetik maskelerle birleşim, piksel sayımı ve girdinin değişmemesi doğrulandı. Bunlar planın matematiksel örnekleridir; gelecekteki uygulama modülünün testleri değildir.
- 24 FR kimliğinin tamamı test matrisinde mevcut; 40 T kimliği ve 40 görev kimliği benzersiz.
- `git diff --check` kontrolünde whitespace hatası yok. Bu kontrollerin geçmesi uygulama testlerinin geçtiği anlamına gelmez.

Yerel PDF/SVG probe sonuçları [araştırmada](research.md) ve [test matrisinde](validation.md) kayıtlıdır. Referans uygulamanın test paketi, yalnız belge değiştiği için bu turda çalıştırılmadı.

## Teslim edilen dosyalar

- [README.md](README.md): giriş ve okuma sırası.
- [spec.md](spec.md): kapsam, davranışlar ve kabul koşulları.
- [plan.md](plan.md): mimari, modüller, bağımlılıklar ve anayasa kontrolü.
- [data-model.md](data-model.md): veri tipleri, koordinatlar, kayıt ve hash.
- [contracts/api.md](contracts/api.md): public API ve hatalar.
- [contracts/reference-cases.json](contracts/reference-cases.json): makine tarafından okunabilir referanslar.
- [lightburn-contract.md](lightburn-contract.md): native export ve uyumluluk kapıları.
- [tasks.md](tasks.md): sıralı uygulama görevleri.
- [validation.md](validation.md): test matrisi ve gerçek kanıt ayrımı.
- [ui-tr.md](ui-tr.md): Türkçe alanlar, yardım ve hata metinleri.
- [research.md](research.md): kaynaklar, yerel probe ve açık uyumluluk işleri.
- [handoff.md](handoff.md): uygulayıcı modele verilecek talimat.
- [analysis.md](analysis.md): bu inceleme.
- [docs/ROADMAP.md](../../ROADMAP.md): K6 kararı ve 0.2A görsel iş akışı dalı.

Mevcut uygulama kodu, dependency dosyaları, çalışma dalı ve kullanıcıya ait `docs/branding/` içeriği değiştirilmedi.
