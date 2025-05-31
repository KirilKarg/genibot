# Сторонник библиотеки
import os
from telethon import TelegramClient, Button
import asyncio
import aioconsole
from tabulate import tabulate

# Собственные модули
import openKey
from data import loader
from handlers.startHandler import StartHandler
from handlers.textInputHandler import TextInputHandler
from handlers.callbackHandler import CallbackHandler

# База данных
from database import db
from database.db import add_log

bot_token, api_key, api_hash = openKey.load_and_decrypt_token().split("\n")

bot_running = True
current_client = None

CHARACTERS = loader.load_characters()

ELEMENTS = loader.load_elements_with_characters()

async def reload_data():
    global CHARACTERS, ELEMENTS
    CHARACTERS = loader.load_characters()
    ELEMENTS = loader.load_elements_with_characters()
    await add_log("DEBUG", __name__,"Данные успешно обновлены!")

client = TelegramClient('bot_session', int(api_key), api_hash)

def generate_elements_buttons():
    elements = list(ELEMENTS.keys())
    return [Button.inline(e.capitalize(), f"element:{e}") for e in elements]

def generate_characters_buttons(element):
    characters = ELEMENTS.get(element, [])
    buttons = []
    for char in characters:
        buttons.append([Button.inline(f"{char.capitalize()}", f"char:{char}")])
    buttons.append([Button.inline("← Назад", "characters")])
    return buttons

PERSISTENT_KEYBOARD = [
    [Button.text("👋 Привет! Нужна помощь", resize=True)],
    [Button.text("Список персонажей", resize=True)]
]

async def init_handlers(client):
    """Инициализация всех обработчиков"""
    objStartHandler = StartHandler(
        client=client,
        generate_elements_buttons=generate_elements_buttons,
        persistent_keyboard=PERSISTENT_KEYBOARD
    )
    objCallbackHandler = CallbackHandler(
        client=client,
        generate_elements_buttons=generate_elements_buttons,
        generate_characters_buttons=generate_characters_buttons,
        characters=CHARACTERS
    )
    TextInputHandler(
        client=client,
        characters=CHARACTERS,
        start_handler=objStartHandler,
        callback_handler=objCallbackHandler,
        persistent_keyboard=PERSISTENT_KEYBOARD
    )

    await add_log("DEBUG", __name__, "Все обработчкики успешно загружены.")

async def command_line_interface():
    """Асинхронный интерфейс для управления ботом через консоль"""
    global bot_running, current_client
    while bot_running:
        try:
            command = await aioconsole.ainput(">>> ")
            if command.strip().lower() == "exit":
                print("Инициировано завершение работы...")
                await current_client.disconnect()
                bot_running = False

            elif command.strip().lower() == "restart":
                print("Перезагрузка датасетов...")
                await reload_data()
                print("Перезапуск бота...")
                await current_client.disconnect()
                await main()
                
            elif command.strip().lower() == "status":
                print("Бот активен" if client.is_connected()
                            else "Бот отключен")
                
            elif command.strip().lower().split()[0] == "user":
                print(f"Информация о пользователе:\n{await db.find_user(command.strip().lower().split()[1])}")

            elif command.strip().lower().split()[0] == "logs":
                await showLogs(command.strip().lower().split())

        except (EOFError, KeyboardInterrupt):
            break

async def showLogs(list_arg:list):
    headers = ["Номер","Дата","Уровень","Модуль","Сообщение","Доп. информация"]
    data = []
    if len(list_arg) == 2:
        data = await db.get_logs(limit=list_arg[1])
    elif len(list_arg) == 3:
        data = await db.get_logs(limit=list_arg[1], level=list_arg[2])
    elif len(list_arg) == 4:
        data = await db.get_logs(limit=list_arg[1], level=list_arg[2], module=list_arg[3])
    else:
        data = await db.get_logs()

    print(tabulate(data[::-1], headers=headers, tablefmt="grid"))
    
async def start_bot():
    """Запуск бота с новой сессией"""
    global current_client
    current_client = TelegramClient('bot_session', int(api_key), api_hash)
    await init_handlers(current_client)
    await current_client.start(bot_token=bot_token)
    await add_log("INFO", __name__, "Бот успешно запущен!")
    print("Бот успешно запущен!")
    #print(categories["characters"].data['беннет'])
    await current_client.run_until_disconnected()

async def main():
    await db.init_db()
    os.makedirs('materials', exist_ok=True)
    
    # Запускаем бота и интерфейс параллельно
    await asyncio.gather(
        start_bot(),
        command_line_interface()
    )

if __name__ == '__main__':
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Аварийное отключение!")
    finally:
        if loop.is_running():
            loop.close()
        print("Бот полностью остановлен")
