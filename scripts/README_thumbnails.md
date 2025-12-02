# Создание миниатюр для галереи скриншотов

Для оптимизации загрузки страницы рекомендуется создать уменьшенные версии (thumbnails) скриншотов.

## Автоматическое создание миниатюр

Используйте скрипт `create_thumbnails.py`:

```bash
python scripts/create_thumbnails.py
```

**Требования:**
- Python 3.x
- Pillow библиотека: `pip install Pillow`

Скрипт создаст миниатюры размером 300x200px в формате JPEG:
- `screenshot_thumb.png` (из `screenshot.png`)
- `screenshot_2_thumb.png` (из `screenshot_2.png`)
- `screenshot_3_thumb.png` (из `screenshot_3.png`)
- `screenshot_4_thumb.png` (из `screenshot_4.png`)

## Ручное создание миниатюр

Если автоматический скрипт недоступен, создайте миниатюры вручную:

1. Откройте каждый скриншот в графическом редакторе
2. Измените размер до 300x200px (или пропорционально, сохраняя соотношение сторон)
3. Сохраните как:
   - `docs/assets/images/screenshot_thumb.png`
   - `docs/assets/images/screenshot_2_thumb.png`
   - `docs/assets/images/screenshot_3_thumb.png`
   - `docs/assets/images/screenshot_4_thumb.png`

## Fallback

Если миниатюры не созданы, галерея будет использовать полные изображения. Это работает, но увеличивает время загрузки страницы.

