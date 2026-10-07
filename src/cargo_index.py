"""Получение данных о зависимостях из sparse-индекса Cargo (этап 2).

Используется только стандартная библиотека: менеджеры пакетов и
сторонние библиотеки для получения зависимостей запрещены заданием.
"""

import json
import urllib.request

DEFAULT_INDEX_URL = "https://index.crates.io"
HTTP_TIMEOUT_SECONDS = 30
NORMAL_KINDS = (None, "normal")
NAME_LEN_SINGLE = 1
NAME_LEN_DOUBLE = 2
NAME_LEN_TRIPLE = 3


class CargoIndexError(Exception):
    """Ошибка получения или разбора данных индекса Cargo."""


def build_index_path(package):
    """Построить путь пакета в sparse-индексе по правилам Cargo."""
    name_len = len(package)
    if name_len == NAME_LEN_SINGLE:
        return f"1/{package}"
    if name_len == NAME_LEN_DOUBLE:
        return f"2/{package}"
    if name_len == NAME_LEN_TRIPLE:
        return f"3/{package[0]}/{package}"
    return f"{package[:2]}/{package[2:4]}/{package}"


def build_index_url(index_url, package):
    """Собрать полный URL записи пакета в sparse-индексе."""
    base = index_url.rstrip("/")
    return f"{base}/{build_index_path(package)}"


USER_AGENT = "dep-graph-visualizer"


def fetch_text(url):
    """Скачать текстовый ресурс по HTTP и вернуть его содержимое."""
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(
            request, timeout=HTTP_TIMEOUT_SECONDS
        ) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset)
    except OSError as error:
        raise CargoIndexError(f"Не удалось скачать {url}: {error}") from error


def parse_entries(text):
    """Разобрать текст индекса: по одной JSON-записи на строку."""
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


MAX_LISTED_VERSIONS = 20


def select_version(entries, version):
    """Найти запись индекса для заданной версии пакета."""
    for entry in entries:
        if entry.get("vers") == version:
            return entry
    available = sorted({entry.get("vers") for entry in entries})
    listed = available[:MAX_LISTED_VERSIONS]
    note = f" (всего {len(available)})"
    raise CargoIndexError(
        f"Версия {version} не найдена. Доступны: "
        f"{', '.join(listed)}{note}"
    )


def version_key(vers):
    """Ключ сортировки версий: числовые компоненты через точку."""
    parts = []
    for chunk in vers.split("."):
        digits = ""
        for char in chunk:
            if not char.isdigit():
                break
            digits += char
        parts.append(int(digits))
    return parts


def select_newest_version(entries):
    """Выбрать запись с новейшей версией (для транзитивных узлов)."""
    return max(entries, key=lambda entry: version_key(entry["vers"]))


def extract_direct_deps(entry):
    """Извлечь имена прямых (normal) зависимостей из записи."""
    names = []
    for dep in entry.get("deps", []):
        kind = dep.get("kind")
        if kind in NORMAL_KINDS and dep.get("optional") is not True:
            names.append(dep["name"])
    return sorted(set(names))


class CargoIndex:
    """Источник прямых зависимостей через sparse-индекс Cargo."""

    def __init__(self, index_url):
        self.index_url = index_url

    def get_direct_deps(self, package, version=None):
        """Вернуть прямые зависимости пакета.

        Для заданной версии выбирается точная запись индекса;
        если версия не задана (транзитивный узел), берётся новейшая.
        """
        url = build_index_url(self.index_url, package)
        entries = parse_entries(fetch_text(url))
        if version is None:
            entry = select_newest_version(entries)
        else:
            entry = select_version(entries, version)
        return extract_direct_deps(entry)
