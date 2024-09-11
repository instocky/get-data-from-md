import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

# Константы для цветного вывода
GREEN = '\033[92m'
RED = '\033[91m'
ORANGE = '\033[93m'
RESET = '\033[0m'

# Базовый URL
BASE_URL = 'https://kotelbk.ru/sveden/'
BASE_URL = 'https://academicol.ru/sveden/'
BASE_URL = 'https://kamkb.ru/sveden/'

# Получаем домен из BASE_URL
DOMAIN = urlparse(BASE_URL).netloc

# Словарь страниц
PAGES = {
    'common': 'Основные сведения',
    'struct': 'Структура и органы управления образовательной организацией',
    'document': 'Документы',
    'education': 'Образование',
    'eduStandarts': 'Образовательные стандарты и требования',
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

def generate_html_report(results):
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Отчет по анализу {DOMAIN}</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .found {{ color: green; }}
            .missing {{ color: red; }}
            .page {{ margin-bottom: 20px; border-bottom: 1px solid #ccc; }}
        </style>
    </head>
    <body>
        <h1>Отчет по анализу {DOMAIN}</h1>
        <p>Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        {''.join(results)}
    </body>
    </html>
    """
    return html_content

def analyze_page(url, section_name, itemprops):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        found_items = []
        missing_items = []
        hidden_items = []

        for prop in itemprops:
            if prop in ['parent', 'child']:
                continue

            element = soup.find(attrs={"itemprop": prop})
            if element:
                if element.has_attr('class') and 'hidden' in element.get('class') and element.text.strip() == "Данные обновляются":
                    hidden_items.append(prop)
                else:
                    found_items.append(prop)
            else:
                missing_items.append(prop)

        # Обновленный вывод в консоль
        print(f"\nАнализ страницы: {url}")
        print(f"\nСекция: {section_name}\n")
        print("Найденные itemprop:")
        for item in found_items:
            color_print(f"✅ {item}", GREEN)
        if hidden_items:
            print("\nСкрытые itemprop:")
            for item in hidden_items:
                color_print(f"🔸 {item}", ORANGE)
        if missing_items:
            print("\nОтсутствующие itemprop:")
            for item in missing_items:
                color_print(f"❌ {item}", RED)
        print(f"\nИтого: {len(found_items)} найдено, {len(hidden_items)} скрыто, {len(missing_items)} отсутствует")

        # Обновленный HTML-фрагмент для отчета
        html_content = f"""
        <div class="page">
            <h2>Анализ страницы: {url}</h2>
            <h3>Секция: {section_name}</h3>
            <h4>Найденные itemprop:</h4>
            <ul>
                {''.join(f'<li class="found">✅ {item}</li>' for item in found_items)}
            </ul>
        """
        if hidden_items:
            html_content += f"""
            <h4>Скрытые itemprop:</h4>
            <ul>
                {''.join(f'<li class="hidden">🔸 {item}</li>' for item in hidden_items)}
            </ul>
            """
        if missing_items:
            html_content += f"""
            <h4>Отсутствующие itemprop:</h4>
            <ul>
                {''.join(f'<li class="missing">❌ {item}</li>' for item in missing_items)}
            </ul>
            """
        html_content += f"""
            <p>Итого: {len(found_items)} найдено, {len(hidden_items)} скрыто, {len(missing_items)} отсутствует</p>
        </div>
        """
        return html_content

    except requests.RequestException as e:
        error_message = f"Ошибка при запросе к {url}: {e}"
        print(error_message)
        return f"<div class='page'><p style='color: red;'>{error_message}</p></div>"

def main():
    itemprop_data = read_json_file('_itemprop.json')
    if itemprop_data is None:
        print("Невозможно продолжить выполнение без данных JSON.")
        return
    
    results = []
    for slug, section_name in PAGES.items():
        url = BASE_URL + slug
        section_data = next((s for s in itemprop_data['sections'] if s['section'] == section_name), None)
        if section_data:
            result = analyze_page(url, section_name, section_data['itemprops'])
            results.append(result)
        else:
            print(f"Предупреждение: Данные для секции '{section_name}' не найдены в JSON.")

    # Генерируем и сохраняем HTML-отчет
    html_report = generate_html_report(results)
    report_filename = f"itemprop_report_{DOMAIN}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(html_report)
    print(f"\nОтчет сохранен в файл: {report_filename}")

if __name__ == "__main__":
    main()