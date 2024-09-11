import re
import json
from datetime import datetime
import os

# Имя входного файла
input_file = 'doc.md'

# Имя выходного файла
output_file = '_itemprop.json'

# Чтение содержимого входного файла
with open(input_file, 'r', encoding='utf-8') as file:
    content = file.read()

# Функция для извлечения itemprop значений из текста
def extract_itemprops(text):
    return list(set(re.findall(r'itemprop="([^"]+)"', text)))

# Разделение содержимого на подразделы
# Обновленное регулярное выражение, которое учитывает различные варианты нумерации
sections = re.split(r'- \d+\.\s*(?:Подраздел\s*)?"([^"]+)"\.?', content)[1:]

# Создание списка словарей для каждого подраздела
sections_data = []
for i in range(0, len(sections), 2):
    section_name = sections[i].strip()
    section_content = sections[i+1] if i+1 < len(sections) else ""
    itemprops = extract_itemprops(section_content)
    if itemprops:  # Добавляем секцию только если в ней есть itemprop
        sections_data.append({
            "section": section_name,
            "itemprops": itemprops
        })

# Создание словаря с метаданными и списком подразделов
output_data = {
    "meta": {
        "created_at": datetime.now().isoformat(),
        "source_file": os.path.basename(input_file)
    },
    "sections": sections_data
}

# Запись данных в JSON файл
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(output_data, file, ensure_ascii=False, indent=2)

print(f"Данные успешно записаны в {output_file}")