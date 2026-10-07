# Dependency Graph Visualizer (Вариант №22)

Инструмент визуализации графа зависимостей для менеджера пакетов.
Формат пакетов — Cargo (Rust). Готовые менеджеры пакетов и сторонние
библиотеки для получения зависимостей **не используются**: данные
читаются напрямую из sparse-индекса Cargo средствами стандартной
библиотеки Python. Реализация — Python 3, без внешних зависимостей.

## Общее описание

Приложение по имени пакета и его версии строит полный граф
зависимостей (с транзитивными), не учитывает пакеты, чьи имена
содержают подстроку фильтра, корректно обрабатывает циклы, умеет
показывать порядок загрузки зависимостей и сохраняет визуализацию
в форматах PlantUML и PNG. Поддерживается режим тестового
репозитория: граф задаётся текстовым файлом, пакеты называются
большими латинскими буквами.

## Функции и настройки (параметры командной строки)

| Параметр | Назначение |
| --- | --- |
| `--package ИМЯ` | имя анализируемого пакета |
| `--version ВЕРСИЯ` | версия пакета |
| `--repo-url URL` | URL репозитория (sparse-индекс Cargo) |
| `--test-repo ПУТЬ` | путь к файлу тестового репозитория |
| `--test-mode` | режим работы с тестовым репозиторием |
| `--output ФАЙЛ.png` | имя генерируемого файла изображения графа |
| `--filter ПОДСТРОКА` | не учитывать пакеты с этой подстрокой в имени |
| `--print-config` | вывести все параметры в формате ключ-значение |
| `--direct-deps` | вывести только прямые зависимости (демо этапа 2) |
| `--load-order` | вывести порядок загрузки зависимостей (этап 4) |

Все параметры проверяются, ошибки выводятся с пояснением.

## Команды сборки и запуска тестов

Сборка не требуется (интерпретируемый язык). Запуск тестов:

```bash
make test        # или: python -m unittest discover -s tests -v
```

Запуск приложения:

```bash
make run ARGS="--package A --version 1.0.0 --test-mode \
  --test-repo tests/fixtures/repo_basic.txt --output graph.png"
```

Скрипты запуска: `run.sh` (Linux/macOS), `run.bat` (Windows),
`Makefile`.

## Примеры использования по этапам

### Этап 1 — прототип с конфигурацией

```bash
python src/main.py --print-config --package serde --version 1.0.210 \
  --repo-url https://index.crates.io --output graph.png --filter rand
python src/main.py --package serde --version abc \
  --repo-url https://index.crates.io --output graph.png
```

### Этап 2 — сбор данных (прямые зависимости Cargo)

```bash
python src/main.py --package serde --version 1.0.210 \
  --repo-url https://index.crates.io --output graph.png --direct-deps
python src/main.py --package clap --version 4.5.23 \
  --repo-url https://index.crates.io --output graph.png --direct-deps
```

### Этап 3 — основные операции (граф, DFS без рекурсии)

```bash
python src/main.py --package A --version 1.0.0 --test-mode \
  --test-repo tests/fixtures/repo_basic.txt --output basic.png
python src/main.py --package A --version 1.0.0 --test-mode \
  --test-repo tests/fixtures/repo_cycle.txt --output cycle.png
python src/main.py --package A --version 1.0.0 --test-mode \
  --test-repo tests/fixtures/repo_basic.txt --filter B --output filtered.png
```

### Этап 4 — дополнительные операции (порядок загрузки)

```bash
python src/main.py --package A --version 1.0.0 --test-mode \
  --test-repo tests/fixtures/repo_basic.txt --output basic.png --load-order
python src/main.py --package serde --version 1.0.210 \
  --repo-url https://index.crates.io --output serde.png --load-order
```

### Этап 5 — визуализация (PlantUML и PNG)

```bash
python src/main.py --package A --version 1.0.0 --test-mode \
  --test-repo tests/fixtures/repo_basic.txt --output basic.png
python src/main.py --package serde --version 1.0.210 \
  --repo-url https://index.crates.io --output serde.png
python src/main.py --package bitflags --version 2.6.0 \
  --repo-url https://index.crates.io --output bitflags.png
```

Рядом с `*.png` создаётся текстовый файл `*.puml` на языке PlantUML.

## Формат тестового репозитория

```
# комментарий
A : B, C
B : D
D :
```

## Структура репозитория

```
src/     исходный код
tests/   тесты unittest и файлы тестовых репозиториев
docs/    пояснение логики работы (logic.md)
```
