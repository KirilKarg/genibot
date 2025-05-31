import fandom
import requests
import os
import time
from urllib.parse import unquote

# Настройка
fandom.set_wiki("genshin-impact")
fandom.set_lang("ru")  # Русская версия вики


def download_character_images(character_name, output_dir="images"):
    """Скачивает изображения персонажа с вики"""
    try:
        # Получаем страницу персонажа
        page = fandom.page(character_name)

        # Создаем папку для сохранения
        os.makedirs(output_dir, exist_ok=True)

        # Фильтруем только нужные изображения
        target_images = [
            img for img in page.images
            if character_name.lower() in unquote(img).lower() and 'icon' not in img.lower()
        ]

        if not target_images:
            print(f"Не найдено изображений для персонажа {character_name}")
            return False

        print(f"Найдено {len(target_images)} изображений для скачивания...")

        # Скачиваем изображения с задержкой между запросами
        # Ограничим 5 изображениями для примера
        for i, img_url in enumerate(target_images[:5]):
            try:
                filename = os.path.join(
                    output_dir,
                    f"{character_name}_{i+1}.{img_url.split('.')[-1].split('?')[0]}"
                )

                print(f"Загрузка ({i+1}/{len(target_images)}): {img_url}")

                response = requests.get(img_url, stream=True, timeout=10)
                response.raise_for_status()

                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                print(f"Успешно сохранено: {filename}")
                time.sleep(1)  # Задержка между запросами

            except Exception as img_error:
                print(f"Ошибка при загрузке {img_url}: {str(img_error)}")
                continue

        return True

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return False


# Пример использования
download_character_images("Фурина")
