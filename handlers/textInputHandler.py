# Стандартные библиотеки
import logging

# Сторонние библиотеки
from telethon import Button
from fuzzywuzzy import fuzz

# Собственные модули
from data import loader
from utils import parcer_tier_list  # Парсер тир листов для персонажей
from handlers.base import BaseHandler  # базовый класс для обработчиков


CHARACTERS_MONIKER = loader.load_moniker_with_characters()

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)


class TextInputHandler(BaseHandler):
    """Обработчик текстового ввода для поиска персонажей"""

    # Константы класса
    SIMILARITY_THRESHOLD = 70
    
    ELEMENTS = {"пиро", "крио", "гидро", "электро", "анемо", "гео", "дендро"}

    def __init__(self, client, start_handler, characters, callback_handler, persistent_keyboard):
        super().__init__(client, persistent_keyboard)
        self.callback_handler = callback_handler
        self.characters = characters
        self.start_handler = start_handler
        self._preprocessed_names = self._preprocess_character_names()
        self._register_handlers()

    def _preprocess_character_names(self):
        """Предварительная обработка имен персонажей для поиска"""
        return {name.lower(): name for name in self.characters}

    def _find_exact_match(self, input_text):
        """Поиск точного совпадения по имени"""
        return self._preprocessed_names.get(input_text)

    async def _send_character_rating(self, event, char_name):
        """Отправка рейтинга персонажа"""
        tier, role = parcer_tier_list.parse_genshin_tier_list(char_name)
        if tier != "НЕИЗВЕСТНО":
            await self._send_with_delay(
                event.chat_id,
                f"Рейтинг: {tier}\nРоль: {role}",
                0.5
            )
            
    async def _handle_error(self, event, error_message):
        """Обработка ошибок"""
        await self._send_with_delay(
            event.chat_id,
            "⚠️ Произошла ошибка при загрузке информации",
            0.5,
            buttons=self.persistent_keyboard
        )

    def is_traveler(self, text):
        words = text.split()
        is_traveler_return = False
        only_traveler = True
        element = None
        if "путешественник" in words:
            is_traveler_return = True
            only_traveler = len(words) == 1
            

        # Нечеткий поиск при отсутствии точного совпадения
        if not is_traveler_return:
            found_char = self._find_closest_character(text)
            is_traveler_return = bool(found_char)

        if is_traveler_return and (not only_traveler):
            pass
                
        return is_traveler_return, element
    
    def _find_closest_character(self, input_text):
        """Нечеткий поиск ближайшего совпадения"""
        best_match = None
        best_score = 0

        for name in self.characters:
            base_score = fuzz.ratio(input_text, name.lower())
            first_word_score = fuzz.ratio(input_text, name.split()[0].lower())
            current_score = max(base_score, first_word_score)

            if current_score > best_score:
                best_score = current_score
                best_match = name

        return best_match if best_score >= self.SIMILARITY_THRESHOLD else None

    def _find_moniker_closest_character(self, input_text):
        """Нечеткий поиск ближайшего совпадения"""
        best_match = None
        best_score = 0

        for name in CHARACTERS_MONIKER:
            base_score = fuzz.ratio(input_text, name.lower())
            first_word_score = fuzz.ratio(input_text, name.split()[0].lower())
            current_score = max(base_score, first_word_score)

            if current_score > best_score:
                best_score = current_score
                best_match = CHARACTERS_MONIKER[name]

        return best_match if best_score >= self.SIMILARITY_THRESHOLD else None
    
    def _register_handlers(self):
        """Регистрация обработчиков текстовых сообщений"""

        @self.register_handler(
            pattern_black_list=[
                r'/start',
                r'^👋 Привет! Нужна помощь\.?$',
                r'Список персонажей'
                ]
            )
        async def handle_text_input(event):
            """Основной обработчик текстового ввода"""

            if (event.text.startswith('/')):
                return

            if "привет" in event.text.lower():
                if self.start_handler:  # Если есть доступ к StartHandler
                    await self.start_handler._send_welcome_sequence(event.chat_id, short_version=True)
                return
            
            is_travaler, element = self.is_traveler(event.text.lower())
            
            if is_travaler:
                if self.callback_handler:
                    if element == None:
                        await self.callback_handler._handle_element_selection(element="путешественник",event=event,edit=False)
                    else:
                        print(element)
                        await self.send_char_info(event, f"путешественник {element}")
                return
            
            input_text = event.text.strip().lower()

            # Поиск точного совпадения
            found_char = self._find_exact_match(input_text)
            is_fuzzy_match = False

            # Нечеткий поиск при отсутствии точного совпадения
            if not found_char:
                found_char = self._find_closest_character(input_text)
                is_fuzzy_match = bool(found_char)

            # Обработка случая, когда персонаж не найден по основному имени
            if not found_char:
                found_char = self._find_moniker_closest_character(input_text)
                is_fuzzy_match = bool(found_char)

            # Обработка случая, когда персонаж не найден ни по одному имени
            if not found_char:
                return await self._send_character_not_found(event)
            
            if is_fuzzy_match:
                await self._send_with_delay(
                    event.chat_id,
                    f"🔍 Возможно, вы имели в виду **{found_char}**?",
                    0.5
                )

            # Отправка информации о найденном персонаже
            await self.send_char_info(event, found_char)

    async def _send_character_not_found(self, event, name = "коза смотрит"):
        """Отправка сообщения о ненайденном персонаже"""
        await self._send_sticker(event.chat_id, "коза смотрит")
        await self._send_with_delay(
            event.chat_id,
            "❌ Информация не найдена. Попробуйте уточнить имя или выберите из меню:",
            1,
            buttons=[[Button.inline("🔍 Поиск персонажей", b"characters")]]
        )
