import time
import curses


def draw(canvas):
    row, column = (5, 20)
    canvas.addstr(row, column, 'Hello, World!', curses.A_BOLD)
    canvas.border()
    canvas.refresh()
    time.sleep(1)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
