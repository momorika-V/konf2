"""Тестовый репозиторий зависимостей из текстового файла (этап 3).

Формат файла (пакеты называются большими латинскими буквами):

    # комментарий
    A : B, C
    B :
"""

SEPARATOR = ":"
COMMENT_PREFIX = "#"


class TestRepoError(Exception):
    """Ошибка чтения или разбора файла тестового репозитория."""


def parse_line(line):
    """Разобрать одну строку: вернуть пару (пакет, список зависимостей)."""
    if SEPARATOR not in line:
        raise TestRepoError(f"Нет разделителя '{SEPARATOR}': {line}")
    left, right = line.split(SEPARATOR, 1)
    package = left.strip()
    deps = [part.strip() for part in right.split(",")]
    deps = [dep for dep in deps if dep]
    if not package:
        raise TestRepoError(f"Пустое имя пакета: {line}")
    return package, deps


def load_repo_map(path):
    """Прочитать файл тестового репозитория в словарь зависимостей."""
    repo_map = {}
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError as error:
        raise TestRepoError(f"Не удалось прочитать файл: {error}") from error
    for number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith(COMMENT_PREFIX):
            continue
        try:
            package, deps = parse_line(line)
        except TestRepoError as error:
            raise TestRepoError(f"Строка {number}: {error}") from error
        repo_map[package] = deps
    return repo_map


class TestRepo:
    """Источник зависимостей для режима тестирования (этап 3)."""

    def __init__(self, path):
        self.repo_map = load_repo_map(path)

    def get_direct_deps(self, package, version=None):
        """Вернуть прямые зависимости пакета из файла репозитория."""
        if package not in self.repo_map:
            raise TestRepoError(f"Пакет {package} отсутствует в репозитории")
        return list(self.repo_map[package])
