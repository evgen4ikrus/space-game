import curses
import asyncio
import time


async def blink(canvas, row, column, symbol='*'):
    while True:
        for _ in range(20):
            canvas.addstr(row, column, symbol, curses.A_DIM)
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


def draw(canvas):
    row, column = (10, 20)
    canvas.border()
    curses.curs_set(False)
    coroutines = []
    for _ in range(5):
        coroutines.append(blink(canvas, row, column))
        column += 3
    while True:
        for coroutine in coroutines.copy():
            coroutine.send(None)
            canvas.refresh()
        time.sleep(0.1)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
