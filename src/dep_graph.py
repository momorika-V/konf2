"""Построение графа зависимостей алгоритмом DFS без рекурсии (этап 3).

Граф хранится как словарь: имя пакета -> список прямых зависимостей.
Циклы обнаруживаются и не приводят к зацикливанию обхода.
"""

STATE_NEW = 0
STATE_IN_PROGRESS = 1
STATE_DONE = 2


def is_filtered(name, filter_substring):
    """Определить, должен ли пакет быть исключён из анализа."""
    return bool(filter_substring) and filter_substring in name


def version_for(root, package, version):
    """Версия запроса: для корня - заданная, для остальных - новейшая."""
    if package == root:
        return version
    return None


def discover_neighbours(
    stack, source, root, package, version, filter_substring, colors
):
    """Положить соседей вершины на стек с учётом фильтра и циклов."""
    for dep in source.get_direct_deps(
        package, version_for(root, package, version)
    ):
        if is_filtered(dep, filter_substring):
            continue
        if colors.get(dep, STATE_NEW) == STATE_IN_PROGRESS:
            continue
        stack.append(dep)


def walk(source, root, version, filter_substring):
    """Итеративный DFS: вернуть множество посещённых пакетов."""
    colors = {root: STATE_IN_PROGRESS}
    stack = []
    discover_neighbours(
        stack, source, root, root, version, filter_substring, colors
    )
    while stack:
        package = stack.pop()
        if colors.get(package, STATE_NEW) != STATE_NEW:
            continue
        colors[package] = STATE_IN_PROGRESS
        discover_neighbours(
            stack, source, root, package, version,
            filter_substring, colors,
        )
        colors[package] = STATE_DONE
    return set(colors)


def build_edges(source, root, visited, version, filter_substring):
    """Собрать рёбра графа для всех посещённых пакетов."""
    edges = {}
    for package in sorted(visited):
        deps = source.get_direct_deps(
            package, version_for(root, package, version)
        )
        kept = [
            dep for dep in deps
            if not is_filtered(dep, filter_substring)
        ]
        edges[package] = sorted(kept)
    return edges


def find_cycles(edges):
    """Найти циклы в графе и вернуть список описаний предупреждений."""
    colors = {}
    warnings = []
    for start in sorted(edges):
        visit_for_cycles(start, edges, colors, warnings)
    return warnings


def visit_for_cycles(node, edges, colors, warnings):
    """Итеративный обход одного дерева поиска для поиска циклов."""
    stack = [(node, iter(edges.get(node, [])))]
    colors[node] = STATE_IN_PROGRESS
    while stack:
        current, neighbours = stack[-1]
        found_next = False
        for neighbour in neighbours:
            state = colors.get(neighbour, STATE_NEW)
            if state == STATE_IN_PROGRESS:
                warnings.append(f"Обнаружен цикл: {current} -> {neighbour}")
            elif state == STATE_NEW:
                colors[neighbour] = STATE_IN_PROGRESS
                stack.append((neighbour, iter(edges.get(neighbour, []))))
                found_next = True
                break
        if not found_next:
            colors[current] = STATE_DONE
            stack.pop()


def build_dependency_graph(source, root, version, filter_substring):
    """Построить граф: вернуть (рёбра, предупреждения о циклах)."""
    visited = walk(source, root, version, filter_substring)
    edges = build_edges(
        source, root, visited, version, filter_substring
    )
    warnings = find_cycles(edges)
    return edges, warnings
