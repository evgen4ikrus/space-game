from physics import update_speed


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas, row_speed, column_speed):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            row_speed, column_speed = update_speed(row_speed, column_speed, -1, 0)
            rows_direction += row_speed

        elif pressed_key_code == DOWN_KEY_CODE:
            row_speed, column_speed = update_speed(row_speed, column_speed, 1, 0)
            rows_direction += row_speed

        elif pressed_key_code == RIGHT_KEY_CODE:
            row_speed, column_speed = update_speed(row_speed, column_speed, 0, 1)
            columns_direction += column_speed

        elif pressed_key_code == LEFT_KEY_CODE:
            row_speed, column_speed = update_speed(row_speed, column_speed, 0, -1)
            columns_direction += column_speed

        else:
            row_speed, column_speed = update_speed(row_speed, column_speed, 0, 0)
            row_speed, column_speed = row_speed + row_speed, column_speed + column_speed

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns
