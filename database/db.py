import aiosqlite
import os
from dotenv import load_dotenv

env_loaded = load_dotenv("env.env")
    
DB_NAME = 'geni.db'
REGISTRATION_ENABLED = os.getenv("REG_ENABLE") == "True"
DEBUG_MOD = os.getenv("DEBUG_MOD") == "True"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as conn:
        # Существующая таблица users
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                tg_username TEXT,
                role TEXT CHECK(role IN ('user', 'vip', 'admin', 'god')) DEFAULT 'user',
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')

        # Новая таблица logs
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                level TEXT CHECK(level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
                module TEXT,
                message TEXT,
                extra_data TEXT
            )
        ''')

        # Индексы для быстрого поиска
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)')

        # Триггер для ограничения количества записей (последние 1000)
        await conn.execute('''
            CREATE TRIGGER IF NOT EXISTS limit_logs
            AFTER INSERT ON logs
            BEGIN
                DELETE FROM logs 
                WHERE id IN (
                    SELECT id FROM logs 
                    ORDER BY id DESC 
                    LIMIT -1 OFFSET 1000
                );
            END;
        ''')

        await conn.commit()


async def add_log(level: str, module: str, message: str, extra_data: dict = None):
    """Добавление записи в логи"""
    if DEBUG_MOD:
        async with aiosqlite.connect(DB_NAME) as conn:
            await conn.execute('''
                INSERT INTO logs (level, module, message, extra_data)
                VALUES (?, ?, ?, ?)
            ''', (
                level.upper(),
                module,
                message,
                str(extra_data) if extra_data else None
            ))
            await conn.commit()


async def get_logs(
    limit: int = 100,
    level: str = None,
    module: str = None,
    start_date: str = None,
    end_date: str = None
):
    """Получение логов с фильтрами"""
    query = "SELECT * FROM logs WHERE 1=1"
    params = []

    if level:
        query += " AND level = ?"
        params.append(level.upper())

    if module:
        query += " AND module LIKE ?"
        params.append(f"%{module}%")

    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)

    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    async with aiosqlite.connect(DB_NAME) as conn:
        cursor = await conn.execute(query, params)
        return await cursor.fetchall()
    
async def register_user(user_id, username, tg_username=None):
    if not REGISTRATION_ENABLED:
        raise Exception("Регистрация временно отключена")

    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute('''
            INSERT INTO users (user_id, username, tg_username, role)
            VALUES (?, ?, ?, COALESCE(
                (SELECT role FROM users WHERE user_id = ?), 
                'user'
            ))
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                tg_username = excluded.tg_username
        ''', (user_id, username, tg_username, user_id))
        await conn.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.execute('''
            SELECT user_id, username, tg_username, role, 
                   registered_at, is_active 
            FROM users WHERE user_id = ?
        ''', (user_id,)) as cursor:
            return await cursor.fetchone()


async def update_user_role(user_id, new_role):
    allowed_roles = ('user', 'vip', 'admin', 'god')
    if new_role not in allowed_roles:
        raise ValueError("Недопустимая роль")

    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute('''
            UPDATE users SET role = ? WHERE user_id = ?
        ''', (new_role, user_id))
        await conn.commit()


async def find_user(identifier):
    """
    Поиск пользователя по ID или username
    Args:
        identifier (str): Может быть числовым ID (str из цифр) или username
    Returns:
        tuple | None: Данные пользователя или None если не найден
    """
    async with aiosqlite.connect(DB_NAME) as conn:
        # Если identifier состоит только из цифр - ищем по ID
        if identifier.isdigit():
            async with conn.execute('''
                SELECT user_id, username, tg_username, role, 
                       registered_at, is_active 
                FROM users WHERE user_id = ?
            ''', (int(identifier),)) as cursor:
                return await cursor.fetchone()

        # Если это username - добавляем @ при необходимости
        username = identifier.lower().lstrip('@')
        formatted_username = f"@{username}"

        # Регистронезависимый поиск
        async with conn.execute('''
            SELECT user_id, username, tg_username, role, 
                   registered_at, is_active 
            FROM users 
            WHERE tg_username = ? COLLATE NOCASE
        ''', (formatted_username,)) as cursor:
            return await cursor.fetchone()
