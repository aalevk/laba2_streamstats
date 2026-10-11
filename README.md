StreamStats

StreamStats — программа для анализа файлов с событиями в форматах CSV и JSONL.
Программа подсчитывает общее количество событий, количество событий каждого уровня и каждого источника, находит пять источников с наибольшим количеством ошибок и определяет время первого и последнего события.

Запуск

Установить зависимости:
python3 -m pip install -e ".[dev]"

Запустить анализ CSV-файла:
streamstats analyze events.csv --format csv --output report.json

Запустить анализ JSONL-файла:
streamstats analyze events.jsonl --format jsonl --output report.json

Для пропуска некорректных записей используется параметр --skip-invalid. Результат анализа сохраняется в JSON-файл.

Тестирование

Запустить тесты:
python3 -m pytest -q

Проверить стиль кода:
ruff check src/streamstats tests