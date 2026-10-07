"""Текстовое представление графа на языке диаграмм PlantUML (этап 5)."""

START_MARKER = "@startuml"
END_MARKER = "@enduml"
INDENT = "  "


def format_edge(source, target):
    """Отформатировать одно ребро графа в синтаксисе PlantUML."""
    return f"[{source}] --> [{target}]"


def build_plantuml(edges):
    """Построить полный текст диаграммы PlantUML по рёбрам графа."""
    lines = [START_MARKER]
    for source in sorted(edges):
        for target in edges[source]:
            lines.append(INDENT + format_edge(source, target))
    lines.append(END_MARKER)
    return "\n".join(lines) + "\n"


def save_plantuml(edges, path):
    """Сохранить текст PlantUML в файл с заданным именем."""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(build_plantuml(edges))
