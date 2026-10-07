"""Разбор и проверка параметров командной строки (этап 1).

Все настраиваемые параметры: имя пакета, URL репозитория, путь к
тестовому репозиторию, режим тестирования, версия пакета, имя файла
изображения графа, подстрока фильтрации.
"""

import argparse

DEFAULT_FILTER = ""
PNG_EXTENSION = ".png"
REQUIRED_OPTION = None


class ConfigError(Exception):
    """Ошибка некорректных параметров командной строки."""


class Config:
    """Хранилище параметров командной строки приложения."""

    def __init__(self, namespace):
        self.package = namespace.package
        self.version = namespace.version
        self.repo_url = namespace.repo_url
        self.test_repo_path = namespace.test_repo
        self.test_mode = namespace.test_mode
        self.output_file = namespace.output
        self.filter_substring = namespace.filter_substring
        self.print_config = namespace.print_config
        self.direct_only = namespace.direct_deps
        self.load_order = namespace.load_order

    def as_pairs(self):
        """Вернуть параметры списком пар ключ-значение для вывода."""
        return [
            ("package", self.package),
            ("version", self.version),
            ("repo_url", self.repo_url),
            ("test_repo_path", self.test_repo_path),
            ("test_mode", self.test_mode),
            ("output_file", self.output_file),
            ("filter_substring", self.filter_substring),
        ]


def build_parser():
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей пакетов Cargo"
    )
    parser.add_argument("--package", help="имя анализируемого пакета")
    parser.add_argument("--version", help="версия пакета")
    parser.add_argument(
        "--repo-url", help="URL-адрес репозитория пакетов"
    )
    parser.add_argument(
        "--test-repo", help="путь к файлу тестового репозитория"
    )
    parser.add_argument(
        "--test-mode", action="store_true",
        help="режим работы с тестовым репозиторием",
    )
    parser.add_argument(
        "--output", help="имя генерируемого файла изображения (.png)"
    )
    parser.add_argument(
        "--filter", dest="filter_substring", default=DEFAULT_FILTER,
        help="подстрока для фильтрации пакетов",
    )
    parser.add_argument(
        "--print-config", action="store_true",
        help="вывести параметры ключ-значение и завершить работу",
    )
    parser.add_argument(
        "--direct-deps", action="store_true",
        help="вывести только прямые зависимости (демо этапа 2)",
    )
    parser.add_argument(
        "--load-order", action="store_true",
        help="вывести порядок загрузки зависимостей (этап 4)",
    )
    return parser


def validate_pair(config):
    """Проверить совместимость источника данных: URL или тестовый."""
    has_url = config.repo_url is not None
    has_test = config.test_mode or config.test_repo_path is not None
    if has_url and has_test:
        raise ConfigError(
            "Заданы одновременно repo-url и тестовый репозиторий"
        )
    if not has_url and not has_test:
        raise ConfigError(
            "Не задан источник данных: repo-url или test-repo"
        )


def validate_required(config):
    """Проверить наличие обязательных параметров и формата вывода."""
    if not config.package:
        raise ConfigError("Не задано имя пакета (--package)")
    if not config.version:
        raise ConfigError("Не задана версия пакета (--version)")
    if not config.output_file:
        raise ConfigError("Не задано имя файла вывода (--output)")
    if not config.output_file.endswith(PNG_EXTENSION):
        raise ConfigError("Файл вывода должен иметь расширение .png")


def validate_values(config):
    """Проверить допустимость значений отдельных параметров."""
    if config.test_mode and not config.test_repo_path:
        raise ConfigError(
            "Режим тестирования требует путь (--test-repo)"
        )
    if config.test_repo_path and not config.test_mode:
        raise ConfigError(
            "Путь test-repo требует режима (--test-mode)"
        )
    if config.filter_substring != DEFAULT_FILTER:
        if not config.filter_substring.strip():
            raise ConfigError("Фильтр состоит из пробелов")


def parse_config(argv):
    """Разобрать и проверить параметры; вернуть объект Config."""
    namespace = build_parser().parse_args(argv)
    config = Config(namespace)
    validate_required(config)
    validate_pair(config)
    validate_values(config)
    return config


def print_config(config):
    """Вывести все параметры в формате ключ-значение (этап 1)."""
    for key, value in config.as_pairs():
        print(f"{key} = {value}")
