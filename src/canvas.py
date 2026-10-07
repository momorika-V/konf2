"""Простейший растровый холст: прямоугольники, линии, текст.

Холст хранит RGB-пиксели построчно. Все операции рисования работают
в целочисленных координатах и не требуют сторонних библиотек.
"""

import bitmap_font

BYTES_PER_PIXEL = 3


class Canvas:
    """RGB-холст с операциями рисования и сохранением в PNG."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = [
            bytearray(background * width) for _ in range(height)
        ]

    def set_pixel(self, x, y, color):
        """Закрасить один пиксель, если он внутри холста."""
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = x * BYTES_PER_PIXEL
            self.pixels[y][offset:offset + BYTES_PER_PIXEL] = color

    def fill_rect(self, x, y, width, height, color):
        """Закрасить прямоугольник заданного размера."""
        for row in range(y, y + height):
            for column in range(x, x + width):
                self.set_pixel(column, row, color)

    def draw_rect(self, x, y, width, height, color):
        """Нарисовать контур прямоугольника."""
        self.fill_rect(x, y, width, 1, color)
        self.fill_rect(x, y + height - 1, width, 1, color)
        self.fill_rect(x, y, 1, height, color)
        self.fill_rect(x + width - 1, y, 1, height, color)

    def draw_line(self, x1, y1, x2, y2, color):
        """Нарисовать отрезок алгоритмом Брезенхема."""
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        step_x = 1 if x1 < x2 else -1
        step_y = 1 if y1 < y2 else -1
        error = dx + dy
        while True:
            self.set_pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                return
            doubled = 2 * error
            if doubled >= dy:
                error += dy
                x1 += step_x
            if doubled <= dx:
                error += dx
                y1 += step_y

    def draw_char(self, char, x, y, color, scale):
        """Нарисовать один символ шрифта с масштабированием."""
        glyph = bitmap_font.get_glyph(char)
        for row_index, row in enumerate(glyph):
            for column_index, cell in enumerate(row):
                if cell == "#":
                    self.fill_rect(
                        x + column_index * scale,
                        y + row_index * scale,
                        scale, scale, color,
                    )

    def draw_text(self, text, x, y, color, scale):
        """Нарисовать строку текста шрифтом 5x7."""
        cursor = x
        for char in text:
            self.draw_char(char, cursor, y, color, scale)
            cursor += bitmap_font.GLYPH_STEP * scale

    def save(self, path):
        """Сохранить холст в PNG-файл через кодировщик png_writer."""
        from png_writer import save_png
        save_png(path, self.pixels, self.width, self.height)
