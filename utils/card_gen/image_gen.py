from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import json

global_path = "materials"

element_translation = {
    'пиро': 'pyro',
    'гидро': 'hydro',
    'крио': 'cryo',
    'анемо': 'anemo',
    'электро': 'electro',
    'гео': 'geo',
    'дендро': 'dendro'
}

books_day = {
    "ПН, ЧТ, ВС": {
        "book_freedom": "Учения о\nСВОБОДЕ",
        "book_prosperity": "Учения о\nПРОЦВЕТАНИИ",
        "book_frailty": "Учения о\nБРЕННОСТИ",
        "book_manual": "Учения о\nНАСТАВЛЕНИИ",
        "book_impartiality": "Учения о\nБЕСПРИСТРАСТНОСТИ",
        "book_rivalry": "Учения о\nСОПЕРНИЧЕСТВЕ"
    },
    "ВТ, ПТ, ВС": {
        "book_resistance": "Учения о\nБОРЬБЕ",
        "book_diligence": "Учения об\nУСЕРДИИ",
        "book_finesse": "Учения об\nИЗЯЩЕСТВЕ",
        "book_wit": "Учения об\nОСТРОУМИИ",
        "book_justice": "Учения о\nСПРАВЕДЛИВОСТИ",
        "book_incineration": "Учения о\nСЖИГАНИИ"
    },
    "СР, СБ, ВС": {
        "book_poetry": "Учения о\nПОЭЗИИ",
        "book_gold": "Учения о\nЗОЛОТЕ",
        "book_light": "Учения о\nСВЕТЕ",
        "book_honesty": "Учения о\nЧЕСТНОСТИ",
        "book_order": "Учения о\nПОРЯДКЕ",
        "book_discord": "Учения о\nРАЗДОРЕ"
    }
}

with open('data/boss.json', encoding='utf-8') as f:
    boss_name = json.load(f)


def find_boss_by_nameBD(nameBD: str):
    for boss in boss_name["еженедельный"] + boss_name["ежедневный"]:
        if boss["nameBD"] == nameBD:
            return boss
    return None

def load_images(path_list):
    """Загружает список изображений с обработкой ошибок"""
    images = []
    for path in path_list:
        try:
            img = Image.open(path).convert("RGBA")
            images.append(img)
        except Exception as e:
            images.append(None)  # или можно создать пустое изображение
    return images


def find_book_key(book_code: str) -> tuple:
    """
    Находит расписание и название книги по её коду
    Возвращает кортеж: (расписание_дней, название_книги)
    """
    for schedule, books in books_day.items():
        if book_code in books:
            return (schedule, books[book_code])
    return (None, None)


def draw_centered_text(draw, center_x, start_y, text, font, fill="black", line_spacing=10):
    """
    Рисует многострочный текст с центрированием по X координате
    :param draw: Объект ImageDraw
    :param center_x: Центральная координата X для текста
    :param start_y: Начальная позиция Y для первой строки
    :param text: Текст для рисования (может содержать \n)
    :param font: Шрифт для использования
    :param fill: Цвет текста
    :param line_spacing: Расстояние между строками
    """
    y_position = start_y
    for line in text.split('\n'):
        # Получаем размеры текущей строки
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Рассчитываем позицию для центрирования
        x_position = center_x - (text_width // 2)

        # Рисуем текст
        draw.text((x_position, y_position), line, font=font, fill=fill)

        # Обновляем позицию Y для следующей строки
        y_position += text_height + line_spacing

def generate_character_card(character_name,character_material,element):
    if "путешественник" in str(character_name).lower():
        bg_path = f'materials/background/traveler/background_{element_translation[element]}.png'
        avatar_path = f'materials/avatar/traveler_avatar.png'
        if character_material["region"] == "mondstadt":
            book_path = [
                f"materials/book/mondstadt/book_freedom_1.png",
                f"materials/book/mondstadt/book_freedom_2.png",
                f"materials/book/mondstadt/book_resistance_2.png",
                f"materials/book/mondstadt/book_poetry_2.png",
                f"materials/book/mondstadt/book_freedom_3.png",
                f"materials/book/mondstadt/book_resistance_3.png",
                f"materials/book/mondstadt/book_poetry_3.png",
            ]
        elif character_material["region"] == "liyue":
            book_path = [
                f"materials/book/liyue/book_prosperity_1.png",
                f"materials/book/liyue/book_prosperity_2.png",
                f"materials/book/liyue/book_diligence_2.png",
                f"materials/book/liyue/book_gold_2.png",
                f"materials/book/liyue/book_prosperity_3.png",
                f"materials/book/liyue/book_diligence_3.png",
                f"materials/book/liyue/book_gold_3.png",
            ]
        elif character_material["region"] == "inazuma":
            book_path = [
                f"materials/book/inazuma/book_frailty_1.png",
                f"materials/book/inazuma/book_frailty_2.png",
                f"materials/book/inazuma/book_finesse_2.png",
                f"materials/book/inazuma/book_light_2.png",
                f"materials/book/inazuma/book_frailty_3.png",
                f"materials/book/inazuma/book_finesse_3.png",
                f"materials/book/inazuma/book_light_3.png",
            ]
        elif character_material["region"] == "sumeru":
            book_path = [
                f"materials/book/sumeru/book_manual_1.png",
                f"materials/book/sumeru/book_manual_2.png",
                f"materials/book/sumeru/book_wit_2.png",
                f"materials/book/sumeru/book_honesty_2.png",
                f"materials/book/sumeru/book_manual_3.png",
                f"materials/book/sumeru/book_wit_3.png",
                f"materials/book/sumeru/book_honesty_3.png",
            ]
        elif character_material["region"] == "fontaine":
            book_path = [
                f"materials/book/fontaine/book_impartiality_1.png",
                f"materials/book/fontaine/book_impartiality_2.png",
                f"materials/book/fontaine/book_justice_2.png",
                f"materials/book/fontaine/book_order_2.png",
                f"materials/book/fontaine/book_impartiality_3.png",
                f"materials/book/fontaine/book_justice_3.png",
                f"materials/book/fontaine/book_order_3.png",
            ]
        elif character_material["region"] == "natlan":
            book_path = [
                f"materials/book/natlan/book_rivalry_1.png",
                f"materials/book/natlan/book_rivalry_2.png",
                f"materials/book/natlan/book_incineration_2.png",
                f"materials/book/natlan/book_discord_2.png",
                f"materials/book/natlan/book_rivalry_3.png",
                f"materials/book/natlan/book_incineration_3.png",
                f"materials/book/natlan/book_discord_3.png",
            ]
    else:
        bg_path = f'materials/background/background_{element_translation[element]}.png'
        avatar_path = f'materials/avatar/{element_translation[element]}/{character_material["name"]}_avatar.png'

        book_path = [
            f'materials/book/{character_material["region"]}/{character_material["material_book_elevation"]}_1.png',
            f'materials/book/{character_material["region"]}/{character_material["material_book_elevation"]}_2.png',
            f'materials/book/{character_material["region"]}/{character_material["material_book_elevation"]}_3.png'
        ]
    
    region_path = f'materials/region/{character_material["region"]}.png'
    week_boss_path = f'materials/week_boss/{character_material["week_boss"]}.png'
    week_boss_material_path = f'materials/week_boss/{character_material["material_week_boss"]}.png'
    day_boss_path = f'materials/day_boss/{character_material["day_boss"]}.png'
    day_boss_material_path = f'materials/day_boss/{character_material["material_day_boss"]}.png'
    flower_path = f'materials/flower/{character_material["flower"]}.png'
    
    star_path = f'materials/{character_material["star"]}star.png'

    corona_path = f"materials/corona.png"
    

    crystal_path = [
        f"materials/crystal/{character_material['crystal']}_1.png",
        f"materials/crystal/{character_material['crystal']}_2.png",
        f"materials/crystal/{character_material['crystal']}_3.png"
    ]

    material_enemy_talent_path = [
        f"materials/enemy_material/{character_material['material_enemy_talent']}_1.png",
        f"materials/enemy_material/{character_material['material_enemy_talent']}_2.png",
        f"materials/enemy_material/{character_material['material_enemy_talent']}_3.png"
    ]

    material_enemy_elevation_path = [
        f"materials/enemy_material/{character_material['material_enemy_elevation']}_1.png",
        f"materials/enemy_material/{character_material['material_enemy_elevation']}_2.png",
        f"materials/enemy_material/{character_material['material_enemy_elevation']}_3.png"
    ]

    # Загрузка шрифтов
    font_name = ImageFont.truetype("utils/card_gen/Vollda-Bold.otf", 68)
    font_name_2 = ImageFont.truetype("utils/card_gen/Vollda-Bold.otf", 22)
    # Загрузка изображений
    try:
        background = Image.open(bg_path).convert("RGBA")
        
        avatar = Image.open(avatar_path).convert("RGBA")

        region = Image.open(region_path).convert("RGBA")

        star = Image.open(star_path).convert("RGBA")

        if "пиро" not in character_name:
            week_boss = Image.open(
                week_boss_path).convert("RGBA")
        
        week_boss_material = Image.open(
            week_boss_material_path).convert("RGBA")

        if "путешественник" not in character_name:
            day_boss = Image.open(day_boss_path).convert("RGBA")
            
            day_boss_material = Image.open(
                day_boss_material_path).convert("RGBA")
        
        flower = Image.open(flower_path).convert("RGBA")
        
        crystal = load_images(crystal_path)
        
        material_enemy_talent = load_images(
            material_enemy_talent_path)
        
        material_enemy_elevation = load_images(
            material_enemy_elevation_path)
        
        book = load_images(book_path)

        corona = Image.open(corona_path).convert("RGBA")
        
    except Exception as e:
        print(f"Ошибка загрузки изображений: {e}")
        return None

    if "путешественник" in character_name:
        book_day, book_desc = "  ВСЕ ДНИ", "ВСЕГО\nПОНЕМНОГУ"
    else:
        book_day, book_desc = find_book_key(
            character_material['material_book_elevation'])

    # Создание нового изображения
    card = background.copy()

    # Размещение аватара 
    card.paste(avatar, (20, 188), avatar)
    card.paste(region, (10, 18), region)
    card.paste(star, (188, 120), star)

    if "путешественник" not in character_name:
        card.paste(day_boss, (586, 188), day_boss)
        card.paste(day_boss_material, (745, 188), day_boss_material)

    if "пиро" not in character_name:
        card.paste(week_boss, (586, 532), week_boss)
    card.paste(week_boss_material, (996, 601), week_boss_material)

    card.paste(flower, (956, 194), flower)

    card.paste(crystal[0], (747, 286), crystal[0])
    card.paste(crystal[1], (809, 286), crystal[1])
    card.paste(crystal[2], (875, 286), crystal[2])

    card.paste(material_enemy_talent[0], (949, 286), material_enemy_talent[0])
    card.paste(material_enemy_talent[1], (1022, 286), material_enemy_talent[1])
    card.paste(material_enemy_talent[2], (1094, 286), material_enemy_talent[2])

    if "путешественник" in character_name:
        card.paste(material_enemy_elevation[0],
                   (750, 827), material_enemy_elevation[0])
        card.paste(material_enemy_elevation[1],
                   (827, 827), material_enemy_elevation[1])
        card.paste(material_enemy_elevation[2],
                   (905, 827), material_enemy_elevation[2])
        
        card.paste(book[0], (756, 600), book[0])
        card.paste(book[1], (833, 600), book[1])
        card.paste(book[2], (916, 600), book[2])
        card.paste(book[3], (756, 715), book[3])
        card.paste(book[4], (833, 715), book[4])
        card.paste(book[5], (916, 715), book[5])
        card.paste(book[6], (999, 715), book[6])
    else:
        card.paste(material_enemy_elevation[0],
                (750, 719), material_enemy_elevation[0])
        card.paste(material_enemy_elevation[1],
                (827, 719), material_enemy_elevation[1])
        card.paste(material_enemy_elevation[2],
                (905, 719), material_enemy_elevation[2])
        
        card.paste(book[0], (756, 600), book[0])
        card.paste(book[1], (833, 600), book[1])
        card.paste(book[2], (916, 600), book[2])

    card.paste(corona, (1076, 601), corona)

    # Добавление текста с количеством
    draw = ImageDraw.Draw(card)

    font = ImageFont.truetype("arial.ttf", 24)

    # Текст с количеством материалов
    text_book_day = book_day
    text_book_day_position = (1033, 542)  # Позиция рядом с материалом
    text_book_desc = book_desc
    text_book_desc_position = (767, 545)  # Позиция рядом с материалом
    text_position_name = (190, 35) 

    if "путешественник" not in character_name:
        day_boss_data = find_boss_by_nameBD(character_material["day_boss"])
        text_day_boss = day_boss_data["name"] if day_boss_data else "Неизвестно"

    if "пиро" not in character_name:
        week_boss_data = find_boss_by_nameBD(character_material["week_boss"])

        text_week_boss = week_boss_data["name"] if week_boss_data else "Неизвестно"
    
    text_day_boss_position = (659, 326)  # Позиция рядом с материалом
    text_week_boss_position = (659, 670)  # Позиция рядом с материалом

    # Рисуем текст с обводкой (для лучшей читаемости)
    draw.text(text_book_day_position, text_book_day, font=font, fill="white",
              stroke_width=2, stroke_fill="black")
    draw.text(text_book_desc_position, text_book_desc, font=font_name_2, fill="black")
    if "путешественник" not in character_name:
        draw.text(text_position_name, character_name.capitalize(), font=font_name,
                fill="white", stroke_width=2, stroke_fill="black")
    else:
        draw.text(text_position_name, f"{element.capitalize()} ГГ", font=font_name,
                  fill="white", stroke_width=2, stroke_fill="black")
        
    if "путешественник" not in character_name:
        draw_centered_text(draw,
                        text_day_boss_position[0],  # center_x
                        text_day_boss_position[1],  # start_y
                        text_day_boss,
                        font=font_name_2,
                        fill="black")

    if "пиро" not in character_name:
        draw_centered_text(draw,
                        text_week_boss_position[0],  # center_x
                        text_week_boss_position[1],  # start_y
                        text_week_boss,
                        font=font_name_2,
                        fill="black")
    # Конвертируем RGBA в RGB (JPEG не поддерживает прозрачность)
    rgb_card = card.convert("RGB")
    # Сохраняем в оперативную память
    buffer = BytesIO()
    card.save(buffer, format="PNG")
    buffer.seek(0)

    rgb_card.close()
    card.close()  # закрываем вручную, т.к. card создан через .copy()

    return buffer
