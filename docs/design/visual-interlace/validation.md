# Kabul ve test matrisi

Bu dosya **yazılacak testleri** tarif eder. Uygulama testleri bu belge turunda çalıştırılmış değildir. Yapılan plan doğrulamaları en sonda ayrı kaydedilir.

## Test katmanları

Saf maske/plan testleri Qt, OpenGL, LightBurn veya donanım istemez. Importer ve proje entegrasyonu ayrı test grubudur. Qt PDF testinde `QT_QPA_PLATFORM=offscreen` kullanılır. Native proje uyumluluğu ayrıca gerçek LightBurn aç/kaydet/Preview denemesine bağlıdır; görüntü karşılaştırması tek başına hareket sırası kanıtı değildir.

| Test | Girdi veya olay | Beklenen sonuç | Gereksinim |
|---|---|---|---|
| T01 | 600×360, 508 DPI | 0,05 mm pitch, 30×18 mm canvas | FR-005,008 |
| T02 | Tam piksele bölünmeyen mm ölçüsü | Ceil grid, esnetme yok, padding <1 piksel | FR-005,008 |
| T03 | Alpha=0/128/255 ve siyah/beyaz RGB | Beyaz compositing ve deterministik gri dönüşümü | FR-002 |
| T04 | Eşik sınırı 127/128/129, invert ve padding | Belirlenmiş `< threshold`; padding her zaman beyaz | FR-002,005 |
| T05 | NaN, infinity, negatif/0 ölçü, aşırı piksel | Erken açık hata; kaynak değişmez | FR-005,024 |
| T06 | PNG/JPEG/BMP/TIFF/WebP/GIF fixture'ları | Doğru RGBA, page/frame ve EXIF yönü | FR-001,002 |
| T07 | Paletli saydam resim, CMYK/ICC örneği | Görünüm doğru normalize; sRGB kararı kayıtlı | FR-002 |
| T08 | Bozuk dosya, yanıltıcı uzantı, bomba boyut | Decode öncesi/sonrası limit; başarı yerine hata | FR-001,024 |
| T09 | N=3,H=10 | `[0,3,6,9] [1,4,7] [2,5,8]` | FR-007,009 |
| T10 | N=1..8, H=0..1024 | Satır birleşimi range(H), çift üyelik yok | FR-006,007,009 |
| T11 | bool/kesir/aralık dışı N, negatif H | Hata; H=0 yalnız saf partition'da geçerli | FR-006 |
| T12 | N=1 farklı maskeler | Ana maskeyle pixel-identical; input değişmez | FR-010 |
| T13 | Beyaz, siyah, checkerboard, tek piksel, rastgele maskeler | Parça OR=M, uint16 toplama=M, aynı shape/grid | FR-007,008,009 |
| T14 | N=1..8 mixed, farklı H | Sabit sıra tablosu, yine tam bir kez üyelik | FR-011 |
| T15 | Boş satırlar ve N=2/3/4 | Orijinal r paritesi değişmez; grup numarası kullanılmaz | FR-012,015 |
| T16 | Tek parça/birleşim/zoom preview | Kaynakla aynı grid; downsample üretim verisini değiştirmez | FR-013,023 |
| T17 | PNG encode/decode | 0/255 ve pixel-identical; byte sıkıştırması önemsiz | FR-008,016 |
| T18 | Kaynak taşınıp JSON iş açılması | Gömülü maske, tüm ayarlar ve sıralar aynı | FR-016 |
| T19 | Eski recipe, gelecek schema, bozuk hash | Eskiye N=1 migration; diğerlerinde açık hata | FR-016,021 |
| T20 | Proje kaydet/aç ve iş kaydet/aç | Ortak payload korunur, dış yol bağımlılığı yok | FR-016 |
| T21 | GUI kaynak/ölçü/eşik değişikliği | Worker sonucu doğru revizyonda gösterilir | FR-005,013 |
| T22 | İptal veya eski worker geç bitiyor | Yeni iş/dosya bozulmaz; export stale planı reddeder | FR-024 |
| T23 | pitch <, =, > spot; spot bilinmiyor | Yalnız küçükse bilgi; bilinmiyorsa varsayım yok | FR-017 |
| T24 | SVG stroke/fill/delik/clip/mask/viewBox | Golden görünüm ve doğru mm sınırı | FR-003 |
| T25 | SVG dış referans, eksik font, animasyon | Açık hata; sessiz eksik çizim kabul edilmez | FR-003,021 |
| T26 | PDF iki sayfa, döndürülmüş/karışık içerik | Doğru sayfa, mm boyutu ve yön | FR-004 |
| T27 | PDF modülü yok, şifreli/bozuk dosya | Uygulama açılır, ilgili kaynak anlamlı hata verir | FR-004,021 |
| T28 | Aynı işin bitmap/SVG/PDF sürümü | Tek kaynak-independent bölücü, doğru ölçü | FR-001,003,004 |
| T29 | Gerber delikleri ve açık ROI | İstenen alan maskesi, Gerber zorunluluğu yok | FR-001,002 |
| T30 | G02 `.lbrn2` fixture'ı ve yeni export | Gömülü görüntü, katman bağlantısı ve mm doğru | FR-014,022 |
| T31 | Bilinmeyen profil/katman limit aşımı | Export reddi; sessiz alan veya tur kaybı yok | FR-021 |
| T32 | N=3 mixed sıra | Etkin Image katman sırası 0,2,1 | FR-011,014 |
| T33 | H=2,N=8; boş grup; asimetrik köşeler | Tuval aynı, boş katman Output kapalı, ayna/kayma yok | FR-008,012,014 |
| T34 | LightBurn Open->Save->Open->Preview | N=1..8 için piksel satır/ölçü/sıra korunur | FR-014,015,022 |
| T35 | Beyaz satır, iki yön, üstten alta örnek | Gerçek skip/yön profile kaydedilir; bilinmeyen garanti edilmez | FR-012,015,023 |
| T36 | Eksik güç/hız recipe, boş maske | Export kapalı; kullanıcı işi yine kaydedebilir | FR-021 |
| T37 | Export yazım hatası/iptal | Eski destination aynı byte'larda kalır | FR-024 |
| T38 | N=3,R=2 ve farklı boş gruplar | Etkin pikseller toplam R kez; sıra 0,1,2,0,1,2 | FR-018 |
| T39 | N=3,mixed,R=3,vary=True | `[0,2,1] [1,0,2] [2,1,0]`, kayıt sonrası aynı | FR-019 |
| T40 | Dwell, boş geçiş ve tur sınırı | Etkin geçişler arasında bekleme; sonda yok; unsupported export reddi | FR-020,021,023 |

## Genel doğruluk örnekleme sınırı

“Tüm H” sonsuz bir test aralığı değildir. Matematiksel dayanak bölüm-kalan teoremidir: her r için tek `k=r%N` vardır. Otomatik test bunun yanında N=1..8 ve H=0..1024'ü kapsamlı tarar; 1025,4095,4096,4097 ve 100003 gibi büyük/sınır değerlerini de ekler. Maskelerde sabit seed ile küçük farklı W,H örnekleri kullanılır; büyük H partition testinde dev bitmap oluşturulmaz.

Kesişim testi yalnız toplam satır sayısına bakmaz. Her r'nin sayımı tam 1 olmalı. Piksel testi bool toplamının taşmaması için en az uint16 kullanır. Siyah=0 PNG byte'larında `OR` yapmak yerine True=kazıma maskelerine dönülür.

## Referans veri seti

- 13×10 asimetrik maske: dört köşeyi farklı işaretle, en üst/en alt satırda tek siyah piksel ekle. Ayna, bir satır kayma ve otomatik kırpmayı yakalar.
- 600×360 kullanıcı örneğinin sentetik eşdeğeri: aynı tam boyut ve 508 DPI; telifli görsel gerekmez.
- Sadece satır 0,2,5,9 dolu H=10 maske: boş satır sonrası indekslerin kaymaması.
- 10×10 tamamen beyaz/siyah/checkerboard ve H<N maskesi.
- 30×18 mm SVG/PDF: rectangle, delik, ince stroke, açık beyaz kenar. Piksel kökeni ve gerçek ölçü bilinir.
- Tam piksele bölünmeyen 30,013×18,017 mm kaynak: padding ve ölçek ayrımı.
- Kaynak bitmap'i ve renderer beklenen çıktısı ayrı fixture; render toleransını interlace eşitliğine taşımayın.

## Doğrulama komutları

Hedef repoda gerçek modüller eklendikten sonra ilgili feature için:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit -q
$env:QT_QPA_PLATFORM = 'offscreen'
.\.venv\Scripts\python.exe -m pytest tests/integration -q
.\.venv\Scripts\python.exe -m pytest -q
```

Mevcut hedef repo import-sınır/legacy büyüme komutları ve GUI duman testi ayrıca çalışır. LightBurn fixture doğrulaması CI'da otomatik yapılır; gerçek uygulama Preview kabulü sürüm değişiminde tekrar edilir. Fiziksel lazer testi bu dosya üretim özelliğinin otomatik test önkoşulu değildir.

## 2026-10-02 plan kanıtı

- Referans ortam: CPython 3.13.13, PyQt6/Qt 6.11.0, Pillow 12.3.0, NumPy 2.5.3.
- QtSvg ile bellekte oluşturulan basit 30×18 mm çizim 600×360 render edildi; beklenen iç/dış pikseller doğrulandı.
- Qt PDF ile bellekte oluşturulan 30×18 mm tek sayfa 600×360 render edildi; pageCount=1, Status.Ready, siyah/beyaz kontrol pikselleri doğru. Okunan boyut yaklaşık 29,999999×17,999999 mm; bu PDF sayı yuvarlamasıdır.
- `resvg_py` kurulumu ve renderer golden testleri bu turda yapılmadı; B01/B02 görevidir.
- Hedef LightBurn sürümü/device profili ve gerçek `.lbrn2` kabulü bu turda doğrulanmadı; G02/C05 görevidir.
- Bu denemeler uygulama kodu yazıldığı veya yukarıdaki 40 kabul testinin geçtiği anlamına gelmez.
