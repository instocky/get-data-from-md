import json
import requests
from bs4 import BeautifulSoup

# Константы для цветного вывода
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Словарь страниц
PAGES = {
    'common': 'Основные сведения',
    'struct': 'Структура и органы управления образовательной организацией',
    'document': 'Документы',
    'education': 'Образование',
    'eduStandart': 'Образовательные стандарты и требования',
    'managers': 'Руководство',
    'employees': 'Педагогический состав',
    'objects': 'Материально-техническое обеспечение и оснащённость образовательного процесса. Доступная среда',
    'grants': 'Стипендии и меры поддержки обучающихся',
    'paid_edu': 'Платные образовательные услуги',
    'budget': 'Финансово-хозяйственная деятельность',
    'vacant': 'Вакантные места для приёма (перевода) обучающихся',
    'inter': 'Международное сотрудничество',
    'catering': 'Организация питания в образовательной организации',
}

def read_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Ошибка: Файл {filename} не найден.")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка: Невозможно декодировать JSON из файла {filename}.")
        return None

def color_print(text, color):
    print(f"{color}{text}{RESET}")

def match_slug_to_section(slug):
    return PAGES.get(slug, "Неизвестная секция")

def analyze_page(url, section_name, itemprops):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        found_items = []
        missing_items = []

        for prop in itemprops:
            if soup.find(attrs={"itemprop": prop}):
                found_items.append(prop)
            else:
                missing_items.append(prop)

        print(f"\nАнализ страницы: {url}")
        print(f"\nСекция: {section_name}\n")

        print("Найденные itemprop:")
        for item in found_items:
            color_print(f"✅ {item}", GREEN)

        print("\nОтсутствующие itemprop:")
        for item in missing_items:
            color_print(f"❌ {item}", RED)

        print(f"\nИтого: {len(found_items)} найдено, {len(missing_items)} отсутствует")

    except requests.RequestException as e:
        print(f"Ошибка при запросе к {url}: {e}")

def main():
    itemprop_data = read_json_file('_itemprop.json')
    if itemprop_data is None:
        print("Невозможно продолжить выполнение без данных JSON.")
        return
    
    base_url = 'https://kamkb.ru/sveden/'
    for slug, section_name in PAGES.items():
        url = base_url + slug
        section_data = next((s for s in itemprop_data['sections'] if s['section'] == section_name), None)
        if section_data:
            analyze_page(url, section_name, section_data['itemprops'])
        else:
            print(f"Предупреждение: Данные для секции '{section_name}' не найдены в JSON.")

if __name__ == "__main__":
    main()