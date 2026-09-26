# MikroCAM

PCB CAM + CNC kontrol + fiber lazer CAM. Açık kaynak (MIT), GitHub'da herkese açık.

- **Hedef taban:** FlatCAM Evo. MikroCAM reposu `mekatrol/flatcam`'in fork'u olarak açılacak
  (`docs/ROADMAP.md` → Hazırlık).
- **Bu dizin:** FlatCAM beta 8.994'ün Python 3.13 / PyQt6 / NumPy 2 / Shapely 2 portu (bkz.
  `README.md`). Ayrı repoda altın referans olarak kalacak; yeni özellik buraya yazılmaz.

## Bağlayıcı kurallar

`.specify/memory/constitution.md` her değişiklikte geçerlidir; spec-kit dışındaki küçük işler de
buna dahildir. Özet:

- Yeni özellik mantığı `mikrocam/` paketine yazılır (feature 001 ile oluşturulacak).
  `app_Main.py`, `camlib.py` ve diğer legacy dosyalara yalnızca hata düzeltmesi ve kısa bağlantı
  kodu eklenir.
- Katman yönü: legacy → `mikrocam.ui` → `mikrocam.bridge` → `mikrocam.<alan>` → `mikrocam.core`.
  `core` ve alan paketleri PyQt6 veya legacy import etmez; legacy'yi yalnızca `bridge` import eder.
- En az iki somut kullanımı olmayan bir soyutlama eklenmez. Yeni bağımlılık gerekçe ve lisans ister.
- Hedef CPython 3.13.x'tir; daha yeni sözdizimi kullanılmaz.
- FlatCAM-Plus'ın non-commercial modüllerinin kaynak kodu açılmaz ve kopyalanmaz (temiz oda);
  FlatCAM-Plus git remote'u olarak eklenmez.

## Komutlar (PowerShell, bu dizindeki 8.994 portu için; Evo reposunda feature 001 ile güncellenir)

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tests/smoke_app.py   # masaüstü/OpenGL gerektirir
.\.venv\Scripts\python.exe FlatCAM.py
```

## İş akışı

- Yeni özellik: `docs/ROADMAP.md`'den sıradaki dilimi seç ve şu akışı izle: `/speckit-specify` →
  `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`.
- Hata düzeltmesi veya davranışı değiştirmeyen refactor için spec gerekmez; önce hatayı yeniden
  üreten bir test yazılır.
