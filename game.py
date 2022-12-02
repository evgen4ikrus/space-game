import asyncio
import curses
import os
import random
import time
from itertools import cycle

from curses_tools import draw_frame, get_frame_size, read_controls, update_speed

coroutines = []


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*', offset_tics=0):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(tics=20)
        await sleep(tics=random.randint(0, offset_tics))
        canvas.addstr(row, column, symbol)
        await sleep(tics=3)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(tics=5)
        canvas.addstr(row, column, symbol)
        await sleep(tics=3)


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


def get_animations_frames(path):
    file_names = os.listdir(path)
    animations_frames = []
    for file_name in file_names:
        with open(os.path.join(path, file_name), "r") as file:
            animations_frames.append(file.read())
    return animations_frames


def get_new_rocket_coordinates(canvas, rocket_frame, rocket_row, rocket_column,
                               rows_direction, columns_direction,
                               canvas_border_indent, row_speed, column_speed):
    frame_rows, frame_columns = curses.window.getmaxyx(canvas)
    row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
    rocket_row += row_speed
    rocket_column += column_speed
    rocket_height, rocket_width = get_frame_size(rocket_frame)
    if rocket_row <= 1:
        rocket_row = canvas_border_indent
    if rocket_row >= frame_rows - rocket_height - canvas_border_indent:
        rocket_row = frame_rows - rocket_height - canvas_border_indent
    if rocket_column <= 1:
        rocket_column = canvas_border_indent
    if rocket_column >= frame_columns - rocket_width - canvas_border_indent:
        rocket_column = frame_columns - rocket_width - canvas_border_indent
    return rocket_row, rocket_column, row_speed, column_speed


async def animate_spaceship(canvas, rocket_frames, rocket_row, rocket_column,
                            canvas_border_indent):
    row_speed = column_speed = 0
    for rocket_frame in cycle(rocket_frames):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        rocket_row, rocket_column, row_speed, column_speed = get_new_rocket_coordinates(
            canvas, rocket_frame,
            rocket_row, rocket_column,
            rows_direction, columns_direction,
            canvas_border_indent,
            row_speed, column_speed
        )
        draw_frame(canvas, rocket_row, rocket_column, rocket_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_row, rocket_column, rocket_frame, negative=True)
        if space_pressed:
            _, rocket_width = get_frame_size(rocket_frame)
            fire_column = rocket_column + rocket_width / 2
            coroutines.append(fire(canvas, rocket_row, fire_column, rows_speed=-2))


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    rows_number, columns_number = canvas.getmaxyx()
    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0
    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas, space_garbage_frames, canvas_border_indent):
    _, frame_columns = curses.window.getmaxyx(canvas)
    while True:
        offset_tics = random.randint(0, 15)
        await sleep(tics=offset_tics)
        garbage_frame = random.choice(space_garbage_frames)
        _, garbage_width = get_frame_size(garbage_frame)
        garbage_column = random.randint(canvas_border_indent, frame_columns - garbage_width - canvas_border_indent)
        coroutines.append(fly_garbage(canvas, garbage_column, garbage_frame, speed=0.5))


def draw(canvas):
    global coroutines
    rocket_frames_path = os.path.join('animations_frames', 'rocket')
    space_garbage_path = os.path.join('animations_frames', 'space_debris')
    rocket_frames = get_animations_frames(rocket_frames_path)
    space_garbage_frames = get_animations_frames(space_garbage_path)

    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)
    bottom_border, right_border = curses.window.getmaxyx(canvas)

    stars_symbols = ['+', '*', '.', ':']
    canvas_border_indent = 1
    stars_count = 100

    for _ in range(stars_count):
        row = random.choice(range(canvas_border_indent, bottom_border-canvas_border_indent))
        column = random.choice(range(canvas_border_indent, right_border-canvas_border_indent))
        symbol = random.choice(stars_symbols)
        coroutines.append(blink(canvas, row, column, symbol=symbol, offset_tics=10))

    _, rocket_width = get_frame_size(rocket_frames[0])
    rocket_row = right_border / 2 - int(rocket_width / 2)
    rocket_column = bottom_border / 2
    coroutines.append(animate_spaceship(canvas, rocket_frames, rocket_column, rocket_row, canvas_border_indent))
    coroutines.append(fill_orbit_with_garbage(canvas, space_garbage_frames, canvas_border_indent))

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
