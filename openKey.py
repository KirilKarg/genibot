import json
from cryptography.fernet import Fernet

# Функция для загрузки ключа из файла
def load_key() -> bytes:
    with open("sec.key", "rb") as key_file:
        return key_file.read()

def load_and_decrypt_token() -> str:
    key = load_key()
    fernet = Fernet(key)
    # Читаем зашифрованный токен из JSON-файла
    with open("config.json", "r") as json_file:
        data = json.load(json_file)
        encrypted_token = data["encrypted_"]
    # Расшифровываем токен
    decrypted_token = fernet.decrypt(encrypted_token.encode()).decode()
    return decrypted_token