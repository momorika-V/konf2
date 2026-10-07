"""Кодировщик PNG: минимальный writer только на стандартной библиотеке.

Изображение задаётся списком строк пикселей (bytearray по строке,
RGB по три байта на пиксель). Файл собирается из чанков IHDR, IDAT,
IEND согласно спецификации PNG.
"""

import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR_TYPE_RGB = 2
BITS_PER_CHANNEL = 8
FILTER_NONE = 0
COMPRESSION_LEVEL = 9


def make_chunk(chunk_type, data):
    """Собрать один чанк PNG: длина, тип, данные и контрольная сумма."""
    length = struct.pack(">I", len(data))
    body = chunk_type + data
    checksum = struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    return length + body + checksum


def make_ihdr(width, height):
    """Сформировать заголовок IHDR для RGB-изображения."""
    params = struct.pack(
        ">IIBBBBB", width, height, BITS_PER_CHANNEL,
        COLOR_TYPE_RGB, FILTER_NONE, FILTER_NONE, FILTER_NONE,
    )
    return make_chunk(b"IHDR", params)


def make_idat(pixels, width, height):
    """Сжать пиксельные данные: фильтр None для каждой строки."""
    raw = bytearray()
    for row in pixels:
        raw.append(FILTER_NONE)
        raw.extend(row)
    compressed = zlib.compress(bytes(raw), COMPRESSION_LEVEL)
    return make_chunk(b"IDAT", compressed)


def make_iend():
    """Сформировать завершающий чанк IEND."""
    return make_chunk(b"IEND", b"")


def save_png(path, pixels, width, height):
    """Записать RGB-изображение в PNG-файл по указанному пути."""
    with open(path, "wb") as handle:
        handle.write(PNG_SIGNATURE)
        handle.write(make_ihdr(width, height))
        handle.write(make_idat(pixels, width, height))
        handle.write(make_iend())
