# MikroCAM marka dosyaları

| Dosya | Açıklama |
| --- | --- |
| `splash.png` | Açılış ekranı, 720×320. `assets/resources/splash.png` ve `assets/resources/dark_resources/splash.png` yerine geçer. |
| `splash@2x.png` | Aynı görselin HiDPI sürümü, 1440×640. |
| `make_splash.py` | Görseli üreten betik. Bakır izler Shapely geometrisidir, camgöbeği çizgi bu izlerin buffer'ından elde edilen izolasyon yoludur, amber çizgiler bakırsız alanın lazer taramasıdır. |

Sol alt köşe boş bırakılmıştır, çünkü `QSplashScreen.showMessage()` yükleme mesajlarını
oraya gri renkte yazar.

## Yeniden üretme

Fontlar SIL Open Font License 1.1 ile lisanslıdır. Repoya eklenmezler; aşağıdaki adreslerden
indirilip bir klasöre konur:

- Chakra Petch (Bold, SemiBold, Medium): <https://github.com/google/fonts/tree/main/ofl/chakrapetch>
- JetBrains Mono (değişken font, `JetBrainsMono[wght].ttf` dosyası `JetBrainsMono.ttf` adıyla kaydedilir):
  <https://github.com/google/fonts/tree/main/ofl/jetbrainsmono>

```powershell
.\.venv\Scripts\python.exe docs\branding\make_splash.py <font_klasoru> docs\branding
```

Betik yalnızca Shapely ve Pillow kullanır. Shapely `requirements.txt`'te sabitlenmiştir; Pillow ise
matplotlib'in bağımlılığı olarak sanal ortama zaten kurulur.
