"""Компоновка и отрисовка графа зависимостей в PNG (этап 5).

Узлы раскладываются по уровням (расстояние от корня), рёбра
рисуются стрелками слева направо. Текст подписей - шрифт 5x7.
"""

from bitmap_font import FONT_HEIGHT
from canvas import Canvas

BACKGROUND = (255, 255, 255)
BOX_COLOR = (70, 110, 190)
TEXT_COLOR = (0, 0, 0)
ARROW_COLOR = (60, 60, 60)

MARGIN = 30
CELL_WIDTH = 190
CELL_HEIGHT = 80
NODE_MIN_WIDTH = 130
NODE_PADDING = 20
NODE_HEIGHT = 46
TEXT_SCALE = 2
ARROW_HEAD = 8


def compute_levels(edges, root):
    """Вычислить уровень каждого узла (обход в ширину от корня)."""
    levels = {root: 0}
    frontier = [root]
    while frontier:
        next_frontier = []
        for node in frontier:
            for dep in edges.get(node, []):
                if dep not in levels:
                    levels[dep] = levels[node] + 1
                    next_frontier.append(dep)
        frontier = next_frontier
    return levels


def compute_positions(edges, root):
    """Разложить узлы по колонкам уровней; вернуть позиции и размеры."""
    levels = compute_levels(edges, root)
    columns = {}
    for node in sorted(levels):
        columns.setdefault(levels[node], []).append(node)
    positions = {}
    for level, nodes in columns.items():
        for index, node in enumerate(nodes):
            x = MARGIN + level * CELL_WIDTH
            y = MARGIN + index * CELL_HEIGHT
            positions[node] = (x, y)
    rows = max(len(nodes) for nodes in columns.values())
    return positions, len(columns), rows


def measure_node_width(names):
    """Подобрать ширину узла под самое длинное имя пакета."""
    char_step = 6 * TEXT_SCALE
    widest = max(len(name) * char_step for name in names)
    return max(NODE_MIN_WIDTH, widest + NODE_PADDING * 2)


def draw_label(canvas, name, box_x, box_y, node_width):
    """Нарисовать подпись узла по центру прямоугольника."""
    char_step = 6 * TEXT_SCALE
    text_w = len(name) * char_step - TEXT_SCALE
    text_h = FONT_HEIGHT * TEXT_SCALE
    x = box_x + (node_width - text_w) // 2
    y = box_y + (NODE_HEIGHT - text_h) // 2
    canvas.draw_text(name, x, y, TEXT_COLOR, TEXT_SCALE)


def draw_nodes(canvas, positions, node_width):
    """Нарисовать все узлы графа с подписями."""
    for name, (x, y) in positions.items():
        canvas.draw_rect(x, y, node_width, NODE_HEIGHT, BOX_COLOR)
        draw_label(canvas, name, x, y, node_width)


def draw_arrow(canvas, start, end, node_width):
    """Нарисовать стрелку от правой грани узла-источника к цели."""
    x1 = start[0] + node_width
    y1 = start[1] + NODE_HEIGHT // 2
    x2 = end[0]
    y2 = end[1] + NODE_HEIGHT // 2
    canvas.draw_line(x1, y1, x2, y2, ARROW_COLOR)
    canvas.draw_line(x2, y2, x2 - ARROW_HEAD, y2 - ARROW_HEAD, ARROW_COLOR)
    canvas.draw_line(x2, y2, x2 - ARROW_HEAD, y2 + ARROW_HEAD, ARROW_COLOR)


def draw_arrows(canvas, positions, edges, node_width):
    """Нарисовать все рёбра графа."""
    for source in sorted(edges):
        for target in edges[source]:
            draw_arrow(
                canvas, positions[source], positions[target], node_width
            )


def render_diagram_png(edges, root, path):
    """Построить изображение графа и сохранить его в PNG-файл."""
    positions, columns, rows = compute_positions(edges, root)
    node_width = measure_node_width(positions)
    width = MARGIN * 2 + (columns - 1) * CELL_WIDTH + node_width
    height = MARGIN * 2 + (rows - 1) * CELL_HEIGHT + NODE_HEIGHT
    canvas = Canvas(width, height, BACKGROUND)
    draw_arrows(canvas, positions, edges, node_width)
    draw_nodes(canvas, positions, node_width)
    canvas.save(path)
