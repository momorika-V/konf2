"""Порядок загрузки зависимостей: обход в глубину без рекурсии (этап 4).

Зависимость должна быть загружена раньше пакета, который её
использует, поэтому используется пост-порядок обхода графа.
"""

STATE_NEW = 0
STATE_OPEN = 1
STATE_CLOSED = 2


def iter_neighbours(edges, package):
    """Вернуть соседей пакета в отсортированном (стабильном) порядке."""
    return sorted(edges.get(package, []))


def process_next(stack, edges, colors, order):
    """Обработать вершину со стека: развернуть или закрыть её."""
    package, neighbours = stack[-1]
    for neighbour in neighbours:
        state = colors.get(neighbour, STATE_NEW)
        if state == STATE_NEW:
            colors[neighbour] = STATE_OPEN
            stack.append(
                (neighbour, iter(iter_neighbours(edges, neighbour)))
            )
            return
        if state == STATE_OPEN:
            order.append((package, neighbour))
    colors[package] = STATE_CLOSED
    order.append(package)
    stack.pop()


def get_load_order(edges, root):
    """Вернуть список зависимостей в порядке их загрузки.

    Пост-порядок обхода: зависимость появляется в списке раньше
    использующего её пакета. Циклы не приводят к зависанию, корень
    в порядок загрузки не включается.
    """
    colors = {root: STATE_OPEN}
    stack = [(root, iter(iter_neighbours(edges, root)))]
    order = []
    while stack:
        process_next(stack, edges, colors, order)
    return [
        item for item in order
        if isinstance(item, str) and item != root
    ]
