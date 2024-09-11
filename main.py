import re
import json
from datetime import datetime
import os

# Имя входного файла
input_file = 'doc.md'

# Имя выходного файла
output_file = 'itemprop.json'

# Чтение содержимого входного файла
with open(input_file, 'r', encoding='utf-8') as file:
    content = file.read()

# Извлечение всех значений itemprop с помощью регулярного выражения
itemprop_values = re.findall(r'itemprop="([^"]+)"', content)

# Удаление дубликатов путем преобразования списка в множество и обратно в список
unique_itemprop_values = list(set(itemprop_values))

# Создание списка словарей для каждого уникального значения itemprop
itemprop_list = [{"itemprop": value} for value in unique_itemprop_values]

# Создание словаря с метаданными и списком itemprop
output_data = {
    "meta": {
        "created_at": datetime.now().isoformat(),
        "source_file": os.path.basename(input_file)
    },
    "itemprop_values": itemprop_list
}

# Запись данных в JSON файл
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(output_data, file, ensure_ascii=False, indent=2)

print(f"Данные успешно записаны в {output_file}")