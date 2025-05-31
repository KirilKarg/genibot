# Стандартные библиотеки
import logging
import os

# Сторонние библиотеки
from telethon import events, Button

# Собственные модули
from handlers.base import BaseHandler  # базовый класс для обработчиков

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)


class CallbackHandler(BaseHandler):
    """Обработчик инлайн-кнопок и callback-запросов"""

    def __init__(self, client, generate_elements_buttons,
                 generate_characters_buttons, characters):
        super().__init__(client)
        self.generate_elements_buttons = generate_elements_buttons
        self.generate_characters_buttons = generate_characters_buttons
        self.characters = characters
        self._register_handlers()

    async def _handle_element_selection(self, element, event=None, edit=True):
        """Обработка выбора элемента"""
        buttons = self.generate_characters_buttons(element)
        if edit:
            if element.lower() == "путешественник":
                await event.edit(f"Стихии путешественника:", buttons=buttons)
            else:
                await event.edit(f"Персонажи стихии {element.capitalize()}:", buttons=buttons)
        else:
            if element.lower() == "путешественник":
                await self._send_with_delay(event.chat_id, f"Стихии путешественника:", buttons=buttons)
            else:
                await self._send_with_delay(event.chat_id, f"Персонажи стихии {element.capitalize()}:", buttons=buttons)

    def _register_handlers(self):
        """Регистрация обработчиков callback-запросов"""

        @self.register_handler(event_type=events.CallbackQuery)
        async def handle_callback(event):
            """Главный обработчик callback-запросов"""
            data = event.data.decode('utf-8')

            if data == "characters":
                buttons = [self.generate_elements_buttons()[i:i+2]
                           for i in range(0, len(self.generate_elements_buttons()), 2)]
                await event.edit("Выберите стихию персонажа:", buttons=buttons)

            elif data.startswith("element:"):
                element = data.split(":")[1]
                await self._handle_element_selection(element, event=event)

            elif data.startswith("char:"):
                char_name = data.split(":")[1]
                await self.send_char_info(event, char_name)

            elif data.startswith("leveling:"):
                char_name = data.split(":")[1]

                await self._send_sticker(event.chat_id, "кли бьют молотком")
                await event.respond("🔒 Данный раздел находится в разработке.\n"
                                    "Приносим извинения за неудобства! Попробуйте позже.")

            elif data.startswith("artwep:"):
                char_name = data.split(":")[1]

                await self._send_sticker(event.chat_id, "кли бьют молотком")
                await event.respond("🔒 Данный раздел находится в разработке.\n"
                                    "Приносим извинения за неудобства! Попробуйте позже.")
