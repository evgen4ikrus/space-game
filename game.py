import asyncio
import curses
import os
import random
import time
from itertools import cycle

from curses_tools import draw_frame, get_frame_size, read_controls


async def blink(canvas, row, column, symbol='*', offset_tics=0):
    while True:
        for _ in range(20):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)

        for _ in range(random.randint(0, offset_tics)):
            await asyncio.sleep(0)

        for _ in range(3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

        for _ in range(5):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)

        for _ in range(3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def get_animations_frames(folder='animations_frames'):
    file_names = os.listdir(folder)
    animations_frames = []
    for file_name in file_names:
        with open(os.path.join('animations_frames', file_name), "r") as file:
            animations_frames.append(file.read())
    return animations_frames


def get_new_rocket_coordinates(rocket_row, rocket_column, rows_direction, columns_direction, bottom_border,
                               upper_border, right_border, left_border, rocket_height,
                               rocket_width, canvas_border_indent):
    if rocket_row + rocket_height + rows_direction >= bottom_border and rows_direction > 0:
        rocket_row = bottom_border - rocket_height - canvas_border_indent
    elif rocket_row + rows_direction <= upper_border and rows_direction < 0:
        rocket_row = upper_border + canvas_border_indent
    elif rocket_column + rocket_width + columns_direction >= right_border and columns_direction > 0:
        rocket_column = right_border - rocket_width - canvas_border_indent
    elif rocket_column + columns_direction <= left_border and columns_direction < 0:
        rocket_column = left_border + canvas_border_indent
    else:
        rocket_row += rows_direction
        rocket_column += columns_direction
    return rocket_row, rocket_column


def draw(canvas):
    animations_frames = get_animations_frames()

    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)
    bottom_border, right_border = curses.window.getmaxyx(canvas)
    left_border, upper_border = 0, 0
    stars_symbols = ['+', '*', '.', ':']
    coroutines = []
    canvas_border_indent = 1
    stars_count = 50

    for _ in range(stars_count):
        row = random.choice(range(canvas_border_indent, bottom_border-canvas_border_indent))
        column = random.choice(range(canvas_border_indent, right_border-canvas_border_indent))
        symbol = random.choice(stars_symbols)
        coroutines.append(blink(canvas, row, column, symbol=symbol, offset_tics=10))
    fire_row, fire_column = bottom_border/2, right_border/2
    coroutines.append(fire(canvas, fire_row, fire_column, rows_speed=-2))

    rocket_row, rocket_column = bottom_border/2, right_border/2
    rocket_height, rocket_width = get_frame_size(animations_frames[0])
    rocket_speed = 3

    for frame in cycle(animations_frames):

        for coroutine in coroutines.copy():
            draw_frame(canvas, rocket_row, rocket_column, frame)
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(0.1)
        draw_frame(canvas, rocket_row, rocket_column, frame, negative=True)
        rows_direction, columns_direction, _ = read_controls(canvas, speed=rocket_speed)
        if rows_direction or columns_direction:
            rocket_row, rocket_column = get_new_rocket_coordinates(
                rocket_row, rocket_column, rows_direction, columns_direction, bottom_border,
                upper_border, right_border, left_border, rocket_height, rocket_width, canvas_border_indent)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
