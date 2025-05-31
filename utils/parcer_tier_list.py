import requests
from bs4 import BeautifulSoup

def parse_genshin_tier_list(target_character=None):
    url = "https://genshin-info.ru/top-personazhej/"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('div', {'id': 'c0'}).find('table', class_='table')
        table_c = soup.find('div', {'id': 'c'}).find('table', class_='table')
        
        if not table or not table_c:
            return "НЕИЗВЕСТНО","НЕИЗВЕСТНО"
        
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')][1:]
        tier_data = {}
        
        headers_c = [th.get_text(strip=True) for th in table_c.find('thead').find_all('th')][1:]
        tier_data_c = {}
        
        for row in table.find('tbody').find_all('tr'):
            tier = row.find('th', class_='charactersTier__rating').get_text(strip=True)
            tier_data[tier] = {role: [] for role in headers}
            
            cells = row.find_all('td')
            
            for i, role in enumerate(headers):
                for card in cells[i].find_all('a', class_='itemcard'):
                    name = card.get('title', '').strip()
                    if name:
                        tier_data[tier][role].append(name)
                        
        for row in table_c.find('tbody').find_all('tr'):
            tier = row.find('th', class_='charactersTier__rating').get_text(strip=True)
            tier_data_c[tier] = {role: [] for role in headers_c}
            
            cells = row.find_all('td')
            
            for i, role in enumerate(headers_c):
                for card in cells[i].find_all('a', class_='itemcard'):
                    name = card.get('title', '').strip()
                    if name:
                        tier_data_c[tier][role].append(name)
                        
        if target_character:
            target = target_character.strip().lower()
            # Специальная обработка для Путешественника
            if "путешественник" in target:
                for tier, roles in tier_data_c.items():
                    for role, characters in roles.items():
                        if any(target == char.lower() for char in characters):
                            print(tier, "\n", translate_role(role))
                            return tier, translate_role(role)
            # Обычный поиск для других персонажей
            for tier, roles in tier_data.items():
                for role, characters in roles.items():
                    if any(target == char.lower() for char in characters):
                        return tier, translate_role(role)

        return "НЕИЗВЕСТНО", "НЕИЗВЕСТНО"

    except Exception:
        return "НЕИЗВЕСТНО", "НЕИЗВЕСТНО"


def translate_role(role):
    """Перевод ролей на русский"""
    role_translations = {
        "Support": "Саппорт",
        "Sub-DPS": "Саб ДД",
        "DPS": "Дамагер"
    }
    return role_translations.get(role, role)
