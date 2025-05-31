# Стандартные библиотеки
import logging

# Сторонние библиотеки
from telethon import Button
from fuzzywuzzy import fuzz

# Собственные модули
from data import loader
from utils import parcer_tier_list  # Парсер тир листов для персонажей
from utils.card_gen import image_gen  # генератор карточек
from handlers.base import BaseHandler  # базовый класс для обработчиков


CHARACTERS_MONIKER = loader.load_moniker_with_characters()

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)


class TextInputHandler(BaseHandler):
    """Обработчик текстового ввода для поиска персонажей"""

    # Константы класса
    SIMILARITY_THRESHOLD = 70
    DESCRIPTION_INITIAL_DELAY = 1.2
    DESCRIPTION_STANDARD_DELAY = 0.7

    def __init__(self, client, start_handler, callback_handler, characters, persistent_keyboard):
        super().__init__(client, persistent_keyboard)
        self.characters = characters
        self.callback_handler = callback_handler  # Сохраняем ссылку на CallbackHandler
        self.start_handler = start_handler  # Сохраняем ссылку на StartHandler
        self._preprocessed_names = self._preprocess_character_names()
        self._register_handlers()

    def _preprocess_character_names(self):
        """Предварительная обработка имен персонажей для поиска"""
        return {name.lower(): name for name in self.characters}

    def _find_exact_match(self, input_text):
        """Поиск точного совпадения по имени"""
        return self._preprocessed_names.get(input_text)

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

    def _find_traveler_character(self, input_text):
        """Нечеткий поиск Путешественника по имени и прозвищам"""
        traveler_names = ["путешественник",
                          "traveler", "главный герой", "протагонист"]
        traveler_monikers = {
            "люмин": "Путешественник",
            "итер": "Путешественник",
            "путник": "Путешественник",
            "герой": "Путешественник",
            "протагонист": "Путешественник",
            "traveler": "Путешественник",
            "главный герой": "Путешественник",
            "гг": "Путешественник"
        }

        best_score = 0
        best_match = None

        # Проверяем стандартные имена
        for name in traveler_names:
            current_score = fuzz.ratio(input_text.lower(), name.lower())
            if current_score > best_score:
                best_score = current_score
                best_match = "Путешественник"

        # Проверяем прозвища
        for moniker in traveler_monikers:
            current_score = fuzz.ratio(input_text.lower(), moniker.lower())
            if current_score > best_score:
                best_score = current_score
                best_match = traveler_monikers[moniker]

        return best_match if best_score >= self.SIMILARITY_THRESHOLD else None

    async def _send_character_card(self, event, char_name):
        """Отправка карточки персонажа"""
        char_data = self.characters[char_name]
        try:
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
        except Exception as e:
            logger.error(f"Ошибка генерации карточки {char_name}: {str(e)}")
            raise

    async def _send_character_rating(self, event, char_name):
        """Отправка рейтинга персонажа"""
        tier, role = parcer_tier_list.parse_genshin_tier_list(char_name)
        if tier != "НЕИЗВЕСТНО":
            await self._send_with_delay(
                event.chat_id,
                f"Рейтинг: {tier}\nРоль: {role}",
                0.5
            )

    async def _send_character_description(self, event, char_data):
        """Отправка описания персонажа"""
        if description := char_data.get('description', {}).get('desc', []):
            for i, line in enumerate(description):
                delay = self.DESCRIPTION_INITIAL_DELAY if i < 2 else self.DESCRIPTION_STANDARD_DELAY
                await self._send_with_delay(event.chat_id, line, delay)
        else:
            await self._send_with_delay(
                event.chat_id,
                "Описание персонажа пока недоступно",
                0.5
            )

    async def _send_character_actions(self, event, char_name):
        """Отправка интерактивных кнопок действий"""
        buttons = [
            [Button.inline("🔧 Советы по прокачке", f"leveling:{char_name}")],
            [Button.inline("⚔️ Оружие и артефакты", f"artwep:{char_name}")]
        ]
        await self._send_message(
            event.chat_id,
            "Выберите дополнительную информацию:",
            buttons=buttons
        )

    async def _send_character_info(self, event, char_name, show_suggestion=False):
        """Основной метод отправки информации о персонаже"""
        try:
            # Отправка разделителя
            await self._send_with_delay(event.chat_id, "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", 0.3)

            # Уведомление о предположении
            if show_suggestion:
                await self._send_with_delay(
                    event.chat_id,
                    f"🔍 Возможно, вы имели в виду **{char_name}**?",
                    0.5
                )

            char_data = self.characters[char_name]
            await self._send_character_card(event, char_name)
            await self._send_character_rating(event, char_name)
            await self._send_character_description(event, char_data)
            await self._send_character_actions(event, char_name)

        except KeyError:
            error_msg = f"Персонаж {char_name} не найден в базе данных"
            logger.error(error_msg)
            await self._handle_error(event, error_msg)

        except Exception as e:
            error_msg = f"Ошибка обработки персонажа {char_name}: {str(e)}"
            logger.error(error_msg)
            await self._handle_error(event, error_msg)

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
        if "путешественник" in words:
            is_traveler_return = len(words) == 1

        # Нечеткий поиск при отсутствии точного совпадения
        if not is_traveler_return:
            found_char = self._find_traveler_character(text)
            is_traveler_return = bool(found_char)

        return is_traveler_return

    def _register_handlers(self):
        """Регистрация обработчиков текстовых сообщений"""

        @self.register_handler(
            pattern_black_list=[
                r'/start',
                r'^👋 Привет! Нужна помощь\.?$'
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

            if self.is_traveler(event.text.lower()):
                if self.callback_handler:
                    await self.callback_handler.handle_element_selection(chat_id=event.chat_id, element="путешественник")
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

            # Отправка информации о найденном персонаже
            await self._send_character_info(event, found_char, show_suggestion=is_fuzzy_match)

    async def _send_character_not_found(self, event):
        """Отправка сообщения о ненайденном персонаже"""
        await self._send_with_delay(
            event.chat_id,
            "❌ Персонаж не найден. Попробуйте уточнить имя или выберите из меню:",
            1,
            buttons=[[Button.inline("🔍 Поиск персонажей", b"characters")]]
        )
