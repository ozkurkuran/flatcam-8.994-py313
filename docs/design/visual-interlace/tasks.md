# Uygulama görevleri

Bu görevler henüz yapılmadı. Bu belge turunda mimari hazırlanmıştır. V1–V4 birer ayrı feature'dır; her biri hedef Evo deposunda kendi spec-kit numarasını alır. Sıra numarası roadmap'teki mevcut sayıları yeniden numaralandırmaz.

Her görevin bitişi ilgili test/kanıtla gösterilir. Test görevi, koruduğu davranışın uygulama görevinden önce gelir. Testler mevcut olmayan modül yüzünden ilk kez hata verebilir; kod geldikten sonra beklenen davranışı gerçekten ölçtükleri denetlenir.

## Ortak başlangıç

- [ ] **G01** Hedef Evo deposunda `CLAUDE.md`, anayasa, roadmap 2/4/5 ve mevcut LaserJob/Placement tiplerini incele. `docs/design/visual-interlace/target-integration.md` içine gerçek host panel, worker ve proje serializer girişlerini, dosya yollarını ve mevcut alan tiplerini yaz. Referans 8.994'e yeni özellik bağlama. Bitiş: yeni model/serializer kopyası oluşturulmayacağı açık olmalı.
- [ ] **G02** [LightBurn keşif prosedürünü](lightburn-contract.md) uygula. `tests/reference/lightburn/<profile_id>/manifest.json` ve gerçek kaydedilmiş küçük projeleri oluştur. Hedef sürüm yoksa yalnız bu entegrasyonun doğrulanamadığını kaydet; V1/V2'de bağımsız işleri sürdür. Bitiş: bitmap kodlaması, ölçü/origin, sıra, Pass-Through, boş satır ve katman kapasitesi alanları kanıtlı.

G02, V1 kodundan önce başlatılır; V3 exporter yazımından önce bitmelidir. G02'nin belirsiz sonucu planı veya bütün kaynak importer'larını durdurmaz.

## V1 visual-mask-interlace

Hikâyeler: **V1-US1** resmi ölçülendirip maske hazırlama; **V1-US2** tamamlayıcı geçişleri inceleme; **V1-US3** PNG ve iş/proje kaydıyla çalışmaya devam etme. Bağımlılık: G01, roadmap 2/4/5.

- [ ] **A01 [V1-US1]** `tests/unit/test_visual_grid.py` ve `test_visual_normalize.py`: ölçü/padding, 508 DPI, alpha, eşik, ters renk, NaN/negatif boyut ve immutable veri testlerini önce yaz. Kabul: T01,T02,T03,T04,T05.
- [ ] **A02 [V1-US1]** `mikrocam/core/visual.py`, `core/interlace_job.py` tiplerini [veri sözleşmesine](data-model.md) göre ekle; mevcut Placement/LaserJob tiplerini kullan. Kabul: modeller Qt/legacy/Pillow import etmiyor.
- [ ] **A03 [V1-US1]** `tests/integration/test_bitmap_source.py`: 1-bit, palette-alpha, RGBA, RGB/JPEG, EXIF yönü, TIFF ve animasyon kare seçimi, bozuk/çok büyük dosya örneklerini yaz. Kabul: T06,T07,T08.
- [ ] **A04 [V1-US1]** `importers/bitmap.py`, `importers/source_validation.py`, `laser/normalize.py` uygula. Pillow'ı `requirements-visual.txt` içinde sabitle, license notice ekle. Kabul: A01/A03 geçer; 1-bit eş ölçekte piksel kaybı yok.
- [ ] **A05 [V1-US2]** `tests/unit/test_interlace_partition.py`, `test_interlace_masks.py`, `test_interlace_order.py`, `test_interlace_direction.py` yaz. JSON referanslarını fixture'a kopyala. Kabul: T09–T15; tüm N ve seçilmiş/geniş H aralıkları.
- [ ] **A06 [V1-US2]** `laser/interlace.py`: row partition, mixed sıra, yön metadata'sı, boş grup sayımı ve lazy maskeyi uygula. Kabul: A05 geçer; N tam maskesi bellekte tutulmaz.
- [ ] **A07 [V1-US2]** `laser/preview.py`, `ui/visual_preview.py`: ana maske/tek geçiş/renkli birleşim ve geçiş listesini ekle. Kabul: T16; üretim bitmap'i preview'den türetilmez.
- [ ] **A08 [V1-US3]** `tests/integration/test_visual_recipe.py`, `test_visual_project_roundtrip.py`, `test_mask_png.py` yaz. Kaynak taşınması, hash, eski kayıt ve başarısız yazım dahil. Kabul: T17–T20.
- [ ] **A09 [V1-US3]** `laser/png_codec.py`, `laser/recipe_io.py` ve JSON schema dosyasını uygula. Gömülü kaynak/ana maske ve N=1 migration ekle. Kabul: A08; yeni `.mcam` formatı yok.
- [ ] **A10 [V1-US1]** `bridge/visual_workflow.py`, `ui/visual_interlace_panel.py`: tek dosya açma, mm/DPI/eşik, sayfa/kare seçimi ve maskeyi hazırlama bağla. Mevcut menüde en fazla kısa bağlantı ekle. Kabul: T21; uygulamaya özel iş mantığı UI'de yok.
- [ ] **A11 [V1-US3]** G01'de bulunan gerçek serializer girişine `bridge/visual_project.py` bağla; proje kaydet/aç ve bağımsız JSON iş kaydını doğrula. Kabul: kaynak olmadan aynı maskenin açılması, yeni FlatCAM nesne sınıfı gerekmemesi.
- [ ] **A12 [V1-US2]** İptal, revizyon kontrolü, spot notu ve bellek limitini tamamla. `tests/integration/test_visual_workflow.py` içinde eski worker sonucunu reddet. Kabul: T22,T23.
- [ ] **A13 [V1-US3]** UI duman testi, import sınırı ve legacy büyüme kontrolünü çalıştır; `docs/visual-interlace.md` kullanım belgesini yaz. Kabul: bitmap->N PNG->recipe/proje->yeniden aç uçtan uca çalışır. Native export henüz tamamlandı denmez.

## V2 visual-svg-pdf

Hikâyeler: **V2-US1** SVG görünümünü kullanma; **V2-US2** PDF sayfasını kullanma; **V2-US3** mevcut Gerber/Geometry nesnesini isteğe bağlı kaynak yapma. Bağımlılık: V1. V2-US3 mevcut Gerber bridge'ine bağlıdır; dosya açma için gerekli değildir.

- [ ] **B01 [V2-US1]** İzole hedef ortamda `resvg_py==0.5.0` Windows/Python 3.13 wheel kurulumunu ve statik çizim/clipping renderını doğrula. `requirements-visual.txt`, `THIRD_PARTY_LICENSES/` ve araştırma kanıtını güncelle. Kabul: derleyici gerektirmeyen kurulum, paketleme denemesi ve license kaydı; başarısızsa sessiz renderer değişimi yok.
- [ ] **B02 [V2-US1]** `tests/integration/test_svg_source.py`: mm/px/viewBox, stroke, delik, transform, clipPath, mask, transparency, metin ve gömülü bitmap örneklerini yaz. Harici referans/dinamik/eksik font hatalarını ekle. Kabul: T24,T25.
- [ ] **B03 [V2-US1]** `importers/svg.py` ve source validation genişletmesini uygula. Ana maske pipeline'ını yeniden kullan. Kabul: B02; kaynak DPI ile çıktı pitch'i karıştırılmıyor.
- [ ] **B04 [V2-US2]** `tests/integration/test_pdf_source.py`: iki sayfa, farklı fiziksel ölçü, döndürülmüş sayfa, vektör+görüntü, bozuk/şifreli dosya ve modül eksikliği testlerini yaz. Kabul: T26,T27; tam piksele bölünmeyen ölçüler dahil.
- [ ] **B05 [V2-US2]** `bridge/pdf_source.py`: lazy Qt PDF load, sayfa seçimi, fiziksel viewport ve NumPy RGBA çıktısını uygula. Kabul: B04; Qt nesnesi core/laser'a geçmiyor.
- [ ] **B06 [V2-US1]** `bridge/visual_workflow.py`, `ui/visual_interlace_panel.py`: bitmap/SVG/PDF file dispatch ve PDF sayfa seçiciyi ekle. Kabul: T28; seçilen sayfa preview ve exportta aynı.
- [ ] **B07 [V2-US2]** `tests/integration/test_visual_sources_equivalence.py`: aynı basit çizimin PNG/SVG/PDF kaynaklarından beklenen mm/grid boyutunu ve interlace birleşimini karşılaştır. Kabul: kaynak render toleransı ile birebir split doğruluğu ayrı assert edilir.
- [ ] **B08 [V2-US3]** `tests/integration/test_gerber_visual_bridge.py`: mevcut top copper poligonları, delikleri ve kullanıcı ROI'si ile maske testi yaz. Kabul: T29; Gerber yokken dosya iş akışı çalışır.
- [ ] **B09 [V2-US3]** `bridge/gerber_source.py` uygula. Mevcut izolasyon/temizleme geometrisini kaynak olarak al; yeni PCB CAM algoritması ekleme. Normal/ters alan seçiminde açık ROI ve kullanıcı önizlemesi kullan. Kabul: B08; Gerber'e özgü işlem interlace içine girmiyor.
- [ ] **B10 [V2-US2]** SVG/PDF lazy import, Qt PDF lisans/paketleme ve donanımsız offscreen duman testini çalıştır. Kabul: bitmap+SVG+PDF tek pipeline üzerinden kaydedilip açılır; PDF vektör çıkarma kapsamı eklenmez.

## V3 lightburn-image-project

Hikâyeler: **V3-US1** native proje üretme; **V3-US2** sıra/ölçü/piksel eşleşmesini doğrulama; **V3-US3** uyumluluk sınırlarını kullanıcıya doğru bildirme. Bağımlılık: V1, G02; genel görsel ürün teslimi için V2 de tamamlanır.

- [ ] **C01 [V3-US1]** `tests/integration/test_lightburn_export.py` ve `test_lightburn_profile.py`: G02 fixture'larından beklenen native alan, katman referansı, bitmap decode ve kapasite testlerini önce yaz. Kabul: T30,T31.
- [ ] **C02 [V3-US1]** `laser/lightburn_profile.py`: ilk kanıtlı profil verisini ve `validate_export` hata sonuçlarını yaz. Device/version/fixture digest zorunlu. Kabul: doğrulanmamış profile export engelli.
- [ ] **C03 [V3-US1]** `laser/lightburn_export.py`: 1 tur, N=1..8, ortak placement ve gömülü görüntülerle atomik native yazımı uygula. Kabul: C01; N=1 piksel eşitliği ve N=3 ölçüleri doğru.
- [ ] **C04 [V3-US2]** `tests/integration/test_lightburn_semantics.py`: mixed sıra, Output kapalı boş grup, crop edilmemiş tuval, Negative kapalı ve geçiş başına tekrar=1 testlerini ekle. Kabul: T32,T33.
- [ ] **C05 [V3-US2]** Hedef LightBurn'de Open->Save->Open->Preview kabul prosedürünü yürüt. Sürüm/device, 13×10 ve 600×360 örnekleri, beyaz satır atlama ve scan yönü kanıtlarını manifeste yaz. Kabul: T34,T35; yazılım uyumluluğu XML testinden ayrı kanıtlı.
- [ ] **C06 [V3-US3]** `ui/visual_interlace_panel.py` export ayarları/raporu, bilinmeyen profil, eksik recipe ve boş maskeyi bağla. Kabul: T36; kullanıcıdan güç/hız tahmini yapılmıyor.
- [ ] **C07 [V3-US3]** `tests/integration/test_lightburn_export_failure.py`: iptal, disk yazma hatası, hash uyuşmazlığı ve desteklenmeyen yön isteğinde önceki dosyanın korunmasını test et. Kabul: T37.
- [ ] **C08 [V3-US2]** V1+V2+V3 uçtan uca demo: PNG/SVG/PDF'den `.lbrn2` üret, hedefte aç, settings ve görselleri karşılaştır. `docs/lightburn-compatibility.md` doğrulanmış destek tablosunu ekle. Kabul: ana ürün hedefi tamam; makine ateşleme gerekmez.

## V4 interlace-cycle-controls

Hikâyeler: **V4-US1** tam tur tekrarı; **V4-US2** tur sırası değişimi; **V4-US3** desteklenen profilde geçişler arası bekleme. Bağımlılık: V3. Kontrollerin gerçek native desteği ayrı ayrı tamamlanır.

- [ ] **D01 [V4-US1]** `tests/unit/test_interlace_cycles.py`: R turda her piksel R kez, etkin/boş geçişler ve kapasite sınırı; `0,1,2,0,1,2` oracle'ını yaz. Kabul: T38.
- [ ] **D02 [V4-US1]** `laser/interlace.py` plan genişlemesi ve `lightburn_export.py` R*N ayrı katman yazımını uygula. Profilin ölçülmüş kapasitesini aşma. Kabul: D01 ve hedefte iki tur Preview sırası doğru.
- [ ] **D03 [V4-US2]** `tests/unit/test_interlace_cycle_order.py` ile tura göre grup kimliği kaydırmasını ve recipe round-trip'i test et; sonra `laser/interlace.py`, `recipe_io.py` davranışını tamamla. Kabul: T39 ve sözleşmedeki üç örnek sıra.
- [ ] **D04 [V4-US3]** G02 prosedürünü native dwell için genişlet. `tests/reference/lightburn/<profile_id>/` içine before/after ayar dosyası ve Preview kanıtı ekle. Kabul: gerçek süre/bekleme davranışı kanıtlı veya yetenek açıkça unsupported.
- [ ] **D05 [V4-US3]** `tests/unit/test_interlace_dwell.py` ve `tests/integration/test_lightburn_dwell.py` yaz; sonra doğrulanmış profil alanını uygula. Kabul: T40; `max(etkin_geçiş-1,0)*delay`, lazer kapalı, son geçişte ek dwell yok. Destek yoksa hata yolu test edilir ve bu altözellik tamamlandı sayılmaz.
- [ ] **D06 [V4-US1]** `ui/visual_interlace_panel.py` tur/sıra/bekleme kontrollerini capability'ye göre etkinleştir; etkin geçiş sayısını ve toplam dwell'i göster. Kabul: desteklenmeyen kayıt kaybolmadan açılır; export gerekçesi açıklanır.
- [ ] **D07 [V4-US2]** Hedef uygulamada kayıt/aç, iki tur ve mixed sıra kabul testlerini çalıştır; destek tablosu ve Türkçe kullanım metinlerini güncelle. Kabul: her iddia profile özgü kanıtlı, eski tek tur çıktısı değişmemiş.

## Sıralama ve bağımsız çalışma

```text
G01 -> V1 -> V2
G02 ------> V3 -> V4
        V1 -> V3
V1 + V2 + V3 -> ilk tam görsel LightBurn teslimi
```

G02 dış uygulama erişimi ister; dosya biçimi varsayımıyla atlanmaz. SVG ve PDF görevleri birbirini beklemek zorunda değildir, fakat aynı bridge/UI dosyaları düzenlenirken değişiklikler sırayla birleştirilir. Bu belge alt ajan çalıştırma talimatı değildir.

## Her feature için kapanış

- İlgili unit/integration testleri, mevcut regresyonlar, import-sınır ve legacy büyüme kontrolleri geçer.
- UI değiştiyse duman testi yapılır. LightBurn değiştiyse ilgili gerçek uygulama kabul testi yapılır.
- Public kod type hint, İngilizce isim/docstring ve `_()` ile çevrilen UI metni kullanır.
- README/uyumluluk tablosu değişen kapsamı açıklar; eksik özellik tamamlandı işaretlenmez.
- Geçen kontrol yeni kod/failure yokken sırf sayı artırmak için tekrar tekrar çalıştırılmaz.
