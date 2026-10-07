"""Точка входа CLI-приложения визуализации графа зависимостей.

Вариант 22: инструмент строит граф зависимостей пакетов формата
Cargo (Rust), поддерживает тестовый репозиторий и сохраняет
визуализацию в форматах PlantUML и PNG.
"""

import os
import sys

from config import ConfigError, parse_config, print_config
from cargo_index import CargoIndex, CargoIndexError
from dep_graph import build_dependency_graph
from load_order import get_load_order
from test_repo import TestRepo, TestRepoError
from plantuml import save_plantuml
from diagram import render_diagram_png

EXIT_OK = 0
EXIT_ERROR = 1


def build_source(config):
    """Создать источник данных о зависимостях по конфигурации."""
    if config.test_mode:
        return TestRepo(config.test_repo_path)
    return CargoIndex(config.repo_url)


def run_direct_mode(source, config):
    """Вывести только прямые зависимости заданного пакета (этап 2)."""
    deps = source.get_direct_deps(config.package, config.version)
    print(f"Прямые зависимости {config.package}:")
    for dep in deps:
        print(f"  {dep}")


def run_full_mode(source, config):
    """Построить граф, вывести порядок загрузки и визуализацию."""
    edges, warnings = build_dependency_graph(
        source, config.package, config.version, config.filter_substring
    )
    for warning in warnings:
        print(f"Предупреждение: {warning}")
    if config.load_order:
        order = get_load_order(edges, config.package)
        print("Порядок загрузки зависимостей:")
        for name in order:
            print(f"  {name}")
    puml_path, png_path = save_outputs(edges, config)
    print(f"PlantUML сохранён: {puml_path}")
    print(f"PNG сохранён: {png_path}")
    print(f"Пакетов в графе: {len(edges)}")


def save_outputs(edges, config):
    """Сохранить текст PlantUML и изображение PNG графа."""
    output_dir = os.path.dirname(config.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    puml_path = config.output_file.replace(".png", ".puml")
    save_plantuml(edges, puml_path)
    render_diagram_png(edges, config.package, config.output_file)
    return puml_path, config.output_file


def main(argv):
    """Запустить приложение: разбор параметров и выполнение этапов."""
    try:
        config = parse_config(argv)
        if config.print_config:
            print_config(config)
            return EXIT_OK
        source = build_source(config)
        if config.direct_only:
            run_direct_mode(source, config)
        else:
            run_full_mode(source, config)
        return EXIT_OK
    except (ConfigError, CargoIndexError, TestRepoError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
