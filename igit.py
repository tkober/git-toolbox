import curses

from ui.screen import StackedScreen, ConstrainedBasedScreen
from ui.view import ListView, Label

KEY_SPACE=32
KEY_C=99
KEY_Q=113

def main(stdscr):
    # turn off cursor blinking
    curses.curs_set(0)

    # color scheme for selected row
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # specify the current selected row
    current_row = 0

    listView = ListView()
    label_1 = Label('Halloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo Welt!');
    label_2 = Label('Halloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo Welt!');
    screen = ConstrainedBasedScreen(stdscr)
    screen.add_view(label_1, lambda w, h: (0, h//2, w//2-1, 1))
    screen.add_view(label_2, lambda w, h: (w//2+1, h//2, w//2-1, 1))

    while 1:
        screen.render()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            pass

        elif key == curses.KEY_DOWN:
            pass

        elif key == KEY_SPACE:
            pass

        elif key == KEY_C:
            pass

        elif key == KEY_Q:
            exit(0)

curses.wrapper(main)