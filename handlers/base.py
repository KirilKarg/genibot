# Стандартные библиотеки
import logging
import asyncio
from functools import wraps

# Сторонние библиотеки
from telethon import events, Button
from telethon.tl.types import InputDocument

# Внутренние модули
from utils import auth
from data import loader
from utils.card_gen import image_gen  # генератор карточек
from utils import parcer_tier_list  # Парсер тир листов для персонажей

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)

sticker_list = loader.load_sticker()

class BaseHandler:
    """Базовый класс для обработчиков событий бота"""

    def __init__(self, client, persistent_keyboard=None):
        self.client = client
        self.persistent_keyboard = persistent_keyboard

    def _auth_required(self, handler):
        """Декоратор для проверки регистрации пользователя"""
        @wraps(handler)
        async def wrapper(event, *args, **kwargs):

            is_button_click = hasattr(event, 'data') and event.data

            if not is_button_click:
                # Проверяем, является ли событие текстовым сообщением, которое начинается с / или содержит "привет"
                is_text_command = hasattr(event, 'text') and (
                    event.text.startswith('/') or "привет" in event.text.lower())
                # Выполняем действия если это не команда и не инлайн-кнопка
                if not is_text_command:
                    logger.info(f"Событие {event.text}")
                    user_id = event.sender_id 
                    user_name = event.sender.username
                    user_role = await auth.is_vip(event)
                    
                    if not user_role:
                        logger.info(f"Была произведена попытка входа\nID: {user_id}\nUserName: {user_name}")
                        await self._send_sticker(event.chat_id, "альбедо выглядывает")
                        await self._send_message(
                            event.chat_id,
                            f"⛔ В настоящий момент доступ к этому функционалу доступен только ограниченному кругу лиц!",
                            buttons=self.persistent_keyboard
                        )
                        return
            return await handler(event, *args, **kwargs)
        return wrapper

    async def _send_message(self, chat_id, text, buttons=None):
        """Универсальный метод отправки сообщений"""
        await self.client.send_message(
            entity=chat_id,
            message=text,
            buttons=buttons,
            reply_to=False
        )

    async def _send_sticker(self, chat_id, name):
        """Универсальный метод отправки сообщений"""
        sticker = InputDocument(
            id=sticker_list[name]["id"],
            access_hash=sticker_list[name]["hash"],
            file_reference=b''
        )
        await self.client.send_message(
            entity=chat_id,
            file=sticker,
            reply_to=False
        )
    async def _send_with_delay(self, chat_id, text, delay=0.6, buttons=None):
        """Отправка сообщения с задержкой и индикатором набора"""
        async with self.client.action(chat_id, 'typing'):
            await asyncio.sleep(delay)
            await self._send_message(chat_id, text, buttons)

    def register_handler(self, pattern=None, pattern_black_list=None, event_type=events.NewMessage):
        """Фабрика для регистрации обработчиков событий"""
        def decorator(handler):
            @self._auth_required
            @wraps(handler)
            async def wrapped_handler(event):
                # Проверяем, есть ли текст события в черном списке
                if pattern_black_list and event.text:
                    from re import match
                    for black_pattern in pattern_black_list:
                        if match(black_pattern, event.text):
                            logger.debug(
                                f"Игнорируем событие по паттерну: {black_pattern}")
                            return None
                if hasattr(event, 'text'):
                    logger.info(f"Событие {event.text}")
                else:
                    if hasattr(event, 'data'):
                        logger.info(f"Нажата кнопка: {event.data.decode()}")
                return await handler(event)

            self.client.add_event_handler(
                wrapped_handler,
                event_type(pattern=pattern) if pattern else event_type()
            )
            return wrapped_handler
        return decorator

    async def send_error(self, chat_id, text, sticker="райден упала"):
        await self._send_sticker(chat_id, sticker)
        await self._send_with_delay(chat_id, text, 0.8)

    async def send_tier_list(self,chat_id,name):
        # Отправка рейтинга и роли
        tier, role = parcer_tier_list.parse_genshin_tier_list(name)
        if tier != "НЕИЗВЕСТНО":
            await self._send_with_delay(
                chat_id,
                f"Рейтинг: {tier}\nРоль: {role}",
                0.5
            )

    async def send_char_descript(self, chat_id, char_data):
        # Отправка описания
        if description := char_data.get('description', {}).get('desc', []):
            for line in description:
                await self._send_with_delay(chat_id, line, 0.7)
        else:
            await self._send_with_delay(
                chat_id,
                "Описание персонажа пока недоступно",
                0.5
            )

    async def send_char_info(self, event, char_name):
        """Обработка запроса информации о персонаже"""
        char_data = self.characters.get(char_name)
        if not char_data:
            await self.send_error(event.chat_id, "Возникла ошибка .-.", sticker="альбедо выглядывает")
            return await event.answer("⚠️ Персонаж не найден")

        try:
            # Отправка разделителя
            await self._send_with_delay(event.chat_id, "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", 0.3)

            # Генерация и отправка карточки персонажа
            buffer = image_gen.generate_character_card(
                char_name,
                char_data["materials"],
                char_data['element']
            )
            buffer.name = "character_card.jpg"

            await self.client.send_file(
                event.chat_id,
                buffer,
                caption=f"{char_name.capitalize()} ({char_data['element'].capitalize()})",
                force_document=False
            )

            await self.send_tier_list(event.chat_id, char_name)
            await self.send_char_descript(event.chat_id, char_data)

            # Формирование кнопок действий
            buttons = [
                [Button.inline("🔧 Советы по прокачке",
                               f"leveling:{char_name}")],
                [Button.inline("⚔️ Оружие и артефакты",
                               f"artwep:{char_name}")]
            ]

            await self._send_with_delay(
                event.chat_id,
                "Выберите дополнительную информацию:",
                0.5,
                buttons=buttons
            )

        except Exception as e:
            logger.error(f"Ошибка обработки персонажа {char_name}: {str(e)}")
            print(e)
            await self.send_error(event.chat_id,"Возникла ошибка .-.")
