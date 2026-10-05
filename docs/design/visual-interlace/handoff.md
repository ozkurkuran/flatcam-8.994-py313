# Uygulayıcı modele devir talimatı

Aşağıdaki metin GPT 6.1 Sol gibi bir kodlama modeline doğrudan görev olarak verilebilir. Model seçimi veya çoklu ajan kullanımı gerektirmez.

## Başlangıç görevi

```text
MikroCAM'e kaynak biçiminden bağımsız görsel interlace ve LightBurn proje export'u ekle.

Önce hedef deponun CLAUDE.md/AGENTS.md kurallarını ve
.specify/memory/constitution.md dosyasını oku. Çalıştığın repo FlatCAM 8.994 referans
portuysa uygulama kodunu buraya bağlama; Evo hedefini belirle. docs/design/visual-interlace/
altındaki README.md, spec.md, plan.md, data-model.md, contracts/api.md,
lightburn-contract.md, tasks.md ve validation.md dosyalarını sırayla oku.

G01 ile mevcut Placement, LaserJob, worker ve proje serializer API'lerini belirle.
G02 LightBurn dosya biçimi/uyumluluk keşfini erken başlat. Kullanıcının LightBurn
sürümünü ve cihaz profilini kaydet; bilinmeyen XML alanı uydurma. G02 için uygulama
erişimi yoksa doğrulanabilecek V1/V2 işlerini sürdür; native export'u tamamlandı sayma.

V1, V2, V3, V4'ü ayrı feature olarak uygula; spec-kit numaralarını hedef deponun
sırasından al. Başka özellik veya genel altyapı ekleme. Her davranışın testini önce yaz,
sonra en küçük doğru uygulamayı yap. Görev kutusunu ancak kabul koşulu geçtiğinde işaretle.

Ana kabul örneği:
- 600x360 1-bit görüntü, 508 DPI, N=3.
- 3 çıktı görüntüsü, her biri 600x360 ve 30x18 mm.
- Grup 0: 0,3,6,...; grup 1: 1,4,7,...; grup 2: 2,5,8,... satırları.
- Diğer satırlar beyaz. Tuval, konum ve ölçek değişmez.
- True=kazıma maskelerinin OR'u kaynak ana maskeyle birebir aynı.
- Her siyah piksel bir turda tam bir kez işlenir.
- Tek lbrn2 içinde ayrı Image katmanları ve gömülü görseller.
- Hedef LightBurn'de Open/Save/Open/Preview ile doğrulanmış çıktı.

PNG/JPEG/BMP/TIFF/WebP/GIF, SVG ve PDF'den seçili tek sayfa kaynak olabilir.
KiCad veya Gerber zorunlu değildir. PDF için bridge içinde QtPdf sayfa rasterleme
planlanmıştır; OCR veya PDF vektör çıkarma ekleme. SVG renderer seçimi ve kurulum
kapısı research.md içindedir. Katman/paket sınırlarını bozma.

İşin sonunda değişen dosyaları, geçen testleri, gerçek LightBurn test edilen
sürüm/device bilgisini ve kalan doğrulanmamış davranışları açıkça raporla.
```

## Yanlış uygulamayı önleyen kurallar

1. Kaynağı N kez ayrı ayrı rasterleme. Bir ana maske üret; ondan parçala.
2. `source[k::N]` dizisini küçük resim olarak export etme. Aynı W×H boş canvas'a yalnız o satırları yerleştir.
3. DPI'ı N'e bölme, pitch'i N ile çarpma. Boş satırlar grup aralığını zaten oluşturur.
4. Her parçanın boş kenarını kırpma. Her resimde aynı tuval ve aynı konum vardır.
5. Boş satırları çıkarıp yeniden indeksleme. Parite ve grup üyeliği kaynak r'den gelir.
6. Siyah=0 PNG byte'larını OR yapıp birleşim doğrulama. Pozitif bool maskeleri kullan.
7. R turu katman başına R tekrar diye yazma. `0,1,2,0,1,2` ile `0,0,1,1,2,2` farklıdır.
8. Mixed sırayı rastgele üretme. `bit_reverse_v1` ve tur kaydırma sözleşmesini uygula.
9. Recipe yüklenince renderer'ı otomatik yeniden çalıştırma. Gömülü ana maskeyi doğrula ve kullan.
10. Her `.lbrn2` alanını tahminle yazma. G02 fixture'ı ve hedef uygulama round-trip'i gerekir.
11. Delay'i JSON/XML comment'ine yazıp uygulanıyor deme. Capability yoksa export reddedilir.
12. UI preview'ünü gerçek galvo yolu diye sunma. Gerçek skip/bidir profil kanıtı ister.
13. SVG/PDF okumayı legacy geometri parser'ına zorla bağlama. Görsel görünüm korunmalıdır.
14. Tekrar kullanılan bir maske dizisini yerinde değiştirme. Snapshot/read-only sözleşmesini koru.
15. Referans portu, kullanıcının ilgisiz değişikliklerini veya kaynak görsellerini değiştirme.

## Karar verme sınırı

Rutin sınıf/fonksiyon yerleşimini bu belgelerdeki sınırlar içinde çöz. Yeni genel framework, yeni FlatCAM nesne tipi, yeni proje uzantısı veya bir başka renderer ancak somut testin mevcut kararı yetersiz göstermesiyle değerlendirilir. Desteklenmeyen özelliği sessizce kaldırma; ilgili görevi eksik ve gerekçeli bırak.

İlk işe başlarken kullanıcıdan bütün planı yeniden onaylamasını isteme. Eksik LightBurn sürümü veya dosya fixture'ı yalnız ilgili test/entegrasyon için istenir. Bağımsız çekirdek ve importer işlerini sürdür.
