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


def get_new_rocket_coordinates(canvas, rocket_frame, rocket_row, rocket_column, rows_direction,
                               columns_direction, canvas_border_indent):
    height, width = curses.window.getmaxyx(canvas)
    rocket_row += rows_direction
    rocket_column += columns_direction
    rocket_height, rocket_width = get_frame_size(rocket_frame)
    if rocket_row <= 0:
        rocket_row = canvas_border_indent
    if rocket_row >= height - rocket_height:
        rocket_row = height - rocket_height - canvas_border_indent
    if rocket_column <= 0:
        rocket_column = canvas_border_indent
    if rocket_column >= width - rocket_width - canvas_border_indent:
        rocket_column = width - rocket_width - canvas_border_indent
    return rocket_row, rocket_column


async def animate_spaceship(canvas, rocket_frames, rocket_row, rocket_column,
                            canvas_border_indent):
    for rocket_frame in cycle(rocket_frames):
        rows_direction, columns_direction, _ = read_controls(canvas)
        rocket_row, rocket_column = get_new_rocket_coordinates(
            canvas, rocket_frame, rocket_row, rocket_column, rows_direction,
            columns_direction, canvas_border_indent)
        draw_frame(canvas, rocket_row, rocket_column, rocket_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_row, rocket_column, rocket_frame, negative=True)


def draw(canvas):
    rocket_frames = get_animations_frames()

    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)
    bottom_border, right_border = curses.window.getmaxyx(canvas)

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
    coroutines.append(animate_spaceship(canvas, rocket_frames, bottom_border/2, right_border/2, canvas_border_indent))

    while True:

        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(0.1)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
