import asyncio
import curses
import os
import random
import time
from itertools import cycle

from curses_tools import draw_frame


async def blink(canvas, row, column, symbol='*'):
    while True:
        for _ in range(20):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)

        for _ in range(random.randint(0, 20)):
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


def draw(canvas):
    with open(os.path.join('animations_frames', 'rocket_frame_1.txt'), "r") as file:
        rocket_frame_1 = file.read()
    with open(os.path.join('animations_frames', 'rocket_frame_2.txt'), "r") as file:
        rocket_frame_2 = file.read()

    canvas.border()
    curses.curs_set(False)
    max_row, max_column = curses.window.getmaxyx(canvas)
    symbols = ['+', '*', '.', ':']
    coroutines = []

    for _ in range(100):
        row = random.choice(range(2, max_row-1))
        column = random.choice(range(2, max_column-1))
        symbol = random.choice(symbols)
        coroutines.append(blink(canvas, row, column, symbol=symbol))
        column += 3
    coroutines.append(fire(canvas, max_row/2, max_column/2, rows_speed=-2))

    for frame in cycle('12'):
        try:
            for coroutine in coroutines.copy():
                if frame == '1':
                    draw_frame(canvas, max_row/2, max_column/2, rocket_frame_2, negative=True)
                    draw_frame(canvas, max_row/2, max_column/2, rocket_frame_1)
                else:
                    draw_frame(canvas, max_row/2, max_column/2, rocket_frame_1, negative=True)
                    draw_frame(canvas, max_row/2, max_column/2, rocket_frame_2)
                coroutine.send(None)
                canvas.refresh()
            time.sleep(0.1)
        except StopIteration:
            coroutines.remove(coroutine)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
