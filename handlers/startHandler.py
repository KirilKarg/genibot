# Стандартные библиотеки
import logging

# Сторонние библиотеки
from telethon import Button

# Собственные модули
from handlers.base import BaseHandler  # базовый класс для обработчиков

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)

WELCOME_MESSAGES = {
    'full': [
        ("Приветствую тебя! 👋", 0.2),
        ("Я - бот-гид по миру Тейвата", 0.6),
        ("Пока что мой функционал ограничен...", 0.6),
        ("Но новые функции не заставят себя ждать!", 0.8),
        ("Такс", 0.2),
        ("Я могу отправить информацию просто по названию", 0.8),
        ("Введи имя персонажа, название оружия или сета артефактов", 0.8),
        ("У меня также есть меню  😄", 0.6),
        ("Вот список того, с чем я могу помочь:", 0.8)
    ],
    'short': [
        ("Приветствую тебя! 👋", 0.2),
        ("Я могу отправить информацию просто по названию", 0.8),
        ("Введи имя персонажа, название оружия или сета артефактов", 0.8),
        ("У меня также есть меню  😄", 0.6),
        ("Вот список того, с чем я могу помочь:", 0.8)
    ]
}


class StartHandler(BaseHandler):
    """Обработчик стартовых команд и регистрации"""

    def __init__(self, client, generate_elements_buttons, persistent_keyboard):
        super().__init__(client, persistent_keyboard)
        self.generate_elements_buttons = generate_elements_buttons
        self._register_handlers()
        # <- Логируем инициализацию
        logger.info("Регистрируем обработчики StartHandler...")

    async def _send_welcome_sequence(self, chat_id, short_version=False, no_message = False):
        """Отправка приветственных сообщений с анимацией"""

        # Формирование интерактивного меню
        inline_buttons = [
            [Button.inline("Персонажи", b"characters")],
            [Button.inline("Оружие", b"weapons")],
            [Button.inline("Артефакты", b"artifacts")]
        ]
        if not no_message:
            messages = WELCOME_MESSAGES['short' if short_version else 'full']

            await self._send_sticker(chat_id, "яэ мико стучит")
            await self._send_with_delay(chat_id, messages[0][0], 0.5)

            # Отправка основной части сообщений
            for text, delay in messages[1:-2]:
                await self._send_with_delay(chat_id, text, delay)

            # Отправка заключительных сообщений с кнопками
            await self._send_with_delay(chat_id, messages[-2][0], messages[-2][1], self.persistent_keyboard)
            await self._send_with_delay(chat_id, messages[-1][0], messages[-1][1], inline_buttons)
        else:
            await self._send_with_delay(chat_id, "Держи:", 0.5, Button.inline("Персонажи", b"characters"))




    def _register_handlers(self):
        """Регистрация обработчиков событий"""

        @self.register_handler(pattern='/start')
        async def handle_start(event):
            """Обработчик команды /start"""
            await self._send_welcome_sequence(event.chat_id)

        @self.register_handler(pattern='^👋 Привет! Нужна помощь\.?$')
        async def handle_greeting(event):
            """Обработчик кнопки приветствия"""
            await self._send_welcome_sequence(event.chat_id, short_version=True)

        @self.register_handler(pattern='Список персонажей')
        async def handle_greeting(event):
            """Обработчик кнопки приветствия"""
            await self._send_welcome_sequence(event.chat_id, no_message=True)


