import curses
import os
from pathlib import Path

from ui.geometry import Padding
from ui.screen import ConstrainedBasedScreen
from ui.view import ListView, Label, HBox, BackgroundView
from utils.git import Stage

KEY_SPACE=32
KEY_C=99
KEY_Q=113

COLOR_PAIR_TITLE=1
COLOR_PAIR_KEY=2
COLOR_PAIR_DESCRIPTION=3
COLOR_PAIR_BRANCH=4

LEGEND=[
    #('[UP/DWN]', ' Scroll '),
    ('[SPACE]', ' Toggle file '),
    ('[A]', ' Toggle all '),
    ('[I]', ' Ignore file '),
    ('[S]', ' Stash all '),
    ('[P]', ' Pop stash '),
    ('[C]', ' Checkout '),
    ('[R]', ' Refresh '),
    ('[Q]', ' Quit ')
]

#########################################################################
class TestDataSource:

    def __init__(self, items):
        self.items = items

    def number_of_rows(self):
        return len(self.items)

    def get_data(self, i):
        return self.items[i]

    def build_row(self, i, data, is_selected, width):
        content = data.get_change_type() + '  ' + data.get_relative_path()
        if is_selected:
            content = '* '+content
        else:
            content = '  '+content

        return Label(content)
#########################################################################

def main(stdscr):

    working_directory = os. getcwd()
    repository_directory = working_directory # TODO: command line argument should be possible

    stage = Stage(repository_directory)

    curses.curs_set(0)
    curses.init_pair(COLOR_PAIR_TITLE, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_PAIR_KEY, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(COLOR_PAIR_DESCRIPTION, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_PAIR_BRANCH, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

    screen = ConstrainedBasedScreen(stdscr)
    title_background = BackgroundView(curses.color_pair(COLOR_PAIR_TITLE))
    screen.add_view(title_background, lambda w, h, v: (0, 0, w, 1))

    title = repository_directory
    path = Path(repository_directory)
    try:
        relative = path.relative_to(Path.home())
        title = '~/' + str(relative)
    except ValueError:
        pass

    repo_label = Label(title)
    repo_label.attributes.append(curses.color_pair(COLOR_PAIR_TITLE))
    repo_label.attributes.append(curses.A_BOLD)

    branch_label = Label()
    branch_label.attributes.append(curses.color_pair(COLOR_PAIR_BRANCH))
    branch_label.attributes.append(curses.A_BOLD)

    title_hbox = HBox()
    title_hbox.add_view(repo_label, Padding(0, 0, 0, 0))
    title_hbox.add_view(branch_label, Padding(1, 0, 0, 0))
    screen.add_view(title_hbox, lambda w, h, v: ((w-v.required_size().width)//2, 0, title_hbox.required_size().width+1, 1))

    more_label = Label('')
    legend_hbox = HBox()
    def set_more_label(clipped):
        if clipped:
            more_label.text = '...'
        else:
            more_label.text = ''

    legend_hbox.clipping_callback = set_more_label
    for key, description in LEGEND:
        key_label = Label(key)
        key_label.attributes.append(curses.color_pair(COLOR_PAIR_KEY))
        legend_hbox.add_view(key_label, Padding(0, 0, 0, 0))

        description_label = Label(description)
        description_label.attributes.append(curses.color_pair(COLOR_PAIR_DESCRIPTION))
        legend_hbox.add_view(description_label, Padding(0, 0, 2, 0))

    screen.add_view(legend_hbox, lambda w, h, v: (0, h-1, w-more_label.required_size().width, 1))
    screen.add_view(more_label, lambda  w, h, v: (w-v.required_size().width-1, h-1, v.required_size().width, 1))


    #########################################################################
    dataSource = TestDataSource(stage.status())
    listView = ListView(dataSource, dataSource)
    screen.add_view(listView, lambda w, h, v: (1, 1, w, h-2))
    #########################################################################

    while 1:
        branch_label.text = '['+stage.active_branch_name()+']'

        screen.render()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            listView.select_previous()

        elif key == curses.KEY_DOWN:
            listView.select_next()

        elif key == KEY_SPACE:
            pass

        elif key == KEY_C:
            pass

        elif key == KEY_Q:
            exit(0)

curses.wrapper(main)