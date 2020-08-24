import curses
import os
from pathlib import Path

from gupy.geometry import Padding
from gupy.screen import ConstrainedBasedScreen
from gupy.view import ListView, Label, HBox, BackgroundView
from utils.git import Stage

KEY_SPACE=ord(' ')
KEY_ENTER=ord('\n')
KEY_C=ord('c')
KEY_Q=ord('q')
KEY_R=ord('r')
KEY_A=ord('a')
KEY_I=ord('i')
KEY_S=ord('s')
KEY_P=ord('p')

COLOR_PAIR_DEFAULT=0
COLOR_PAIR_TITLE=1
COLOR_PAIR_KEY=2
COLOR_PAIR_DESCRIPTION=3
COLOR_PAIR_BRANCH=4
COLOR_PAIR_SELECTED=5
COLOR_PAIR_ADDED=6
COLOR_PAIR_DELETED=7
COLOR_PAIR_MODIFIED=8
COLOR_PAIR_MOVED=9
COLOR_PAIR_UNTRACKED=10
COLOR_PAIR_STAGED=11
COLOR_PAIR_CONFIRMATION=12
COLOR_PAIR_CONFIRMATION_SELECTION=13

LEGEND=[
    ('[SPACE]', ' Toggle file '),
    ('[A]', ' Toggle all '),
    ('[I]', ' Ignore file '),
    ('[S]', ' Stash all '),
    ('[P]', ' Pop stash '),
    ('[C]', ' Checkout '),
    ('[R]', ' Refresh '),
    ('[Q]', ' Quit ')
]


class TableViewDelegate:

    def __init__(self, change_type_colors, files=[]):
        self.change_type_colors = change_type_colors
        self.files = files

    def number_of_rows(self):
        return len(self.files)

    def get_data(self, i):
        return self.files[i]

    def build_row(self, i, file, is_selected, width):
        hbox = HBox()

        staged_char = '+'
        if file.is_staged() is not True:
            staged_char = ' '
        staged_label = Label(staged_char)
        hbox.add_view(staged_label, Padding(2, 0, 0, 0))

        change_type = file.get_change_type()
        change_type_label = Label(change_type)
        change_type_label.attributes.append(curses.A_BOLD)
        change_type_label.attributes.append(self.change_type_colors[change_type])
        hbox.add_view(change_type_label, Padding(3, 0, 2, 0))

        path_to_show = file.get_relative_path()
        available_width = width - hbox.required_size().width
        if available_width < len(path_to_show):
            path_to_show = '...' + path_to_show[len(path_to_show)-available_width+4:]

        path_label = Label(path_to_show)
        hbox.add_view(path_label, Padding(0, 0, 0, 0))

        if file.is_staged():
            staged_label.attributes.append(curses.color_pair(COLOR_PAIR_STAGED))
            path_label.attributes.append(curses.color_pair(COLOR_PAIR_STAGED))

        result = hbox
        if is_selected:
            result = BackgroundView(curses.color_pair(COLOR_PAIR_SELECTED))
            result.add_view(hbox)
            for label in hbox.get_elements():
                label.attributes.append(curses.color_pair(COLOR_PAIR_SELECTED))

        return result


def main(stdscr):
    repository_directory = os. getcwd()
    stage = Stage(repository_directory)

    curses.curs_set(0)
    curses.init_pair(COLOR_PAIR_TITLE, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_PAIR_KEY, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(COLOR_PAIR_DESCRIPTION, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_PAIR_BRANCH, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
    curses.init_pair(COLOR_PAIR_SELECTED, curses.COLOR_BLACK, curses.COLOR_CYAN)

    curses.init_pair(COLOR_PAIR_ADDED, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_DELETED, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_MODIFIED, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_MOVED, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_UNTRACKED, curses.COLOR_CYAN, curses.COLOR_BLACK)

    curses.init_pair(COLOR_PAIR_STAGED, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_CONFIRMATION, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(COLOR_PAIR_CONFIRMATION_SELECTION, curses.COLOR_BLACK, curses.COLOR_WHITE)

    change_type_colors = {
        'A': curses.color_pair(COLOR_PAIR_ADDED),
        'D': curses.color_pair(COLOR_PAIR_DELETED),
        'R': curses.color_pair(COLOR_PAIR_MOVED),
        'M': curses.color_pair(COLOR_PAIR_MODIFIED),
        'T': curses.color_pair(COLOR_PAIR_MODIFIED),
        'C': curses.color_pair(COLOR_PAIR_DEFAULT),
        '?': curses.color_pair(COLOR_PAIR_UNTRACKED)
    }

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
        legend_hbox.add_view(key_label, Padding(2, 0, 0, 0))

        description_label = Label(description)
        description_label.attributes.append(curses.color_pair(COLOR_PAIR_DESCRIPTION))
        legend_hbox.add_view(description_label, Padding(0, 0, 0, 0))

    screen.add_view(legend_hbox, lambda w, h, v: (0, h-1, w-more_label.required_size().width, 1))
    screen.add_view(more_label, lambda  w, h, v: (w-v.required_size().width-1, h-1, v.required_size().width, 1))

    delegate = TableViewDelegate(change_type_colors)
    def refresh_stage():
        delegate.files = stage.status()

    refresh_stage()

    list_view = ListView(delegate, delegate)
    screen.add_view(list_view, lambda w, h, v: (0, 1, w, h-2))

    confirmation_active = False
    confirmation_action = None

    def perform_checkout(file):
        stage.checkout(file)
        refresh_stage()

    confirmation_background = BackgroundView(curses.color_pair(COLOR_PAIR_CONFIRMATION))
    confirmation_text_label = Label()
    confirmation_text_label.attributes.append(curses.color_pair(COLOR_PAIR_CONFIRMATION))
    confirmation_no_label = Label(' NO ')
    confirmation_yes_label = Label(' YES ')
    yes_selected = False

    def update_confirmation_answer_labels():
        confirmation_no_label.attributes.clear()
        confirmation_yes_label.attributes.clear()

        if yes_selected:
            confirmation_no_label.attributes.append(curses.color_pair(COLOR_PAIR_CONFIRMATION))
            confirmation_yes_label.attributes.append(curses.color_pair(COLOR_PAIR_CONFIRMATION_SELECTION))
        else:
            confirmation_no_label.attributes.append(curses.color_pair(COLOR_PAIR_CONFIRMATION_SELECTION))
            confirmation_yes_label.attributes.append(curses.color_pair(COLOR_PAIR_CONFIRMATION))

    def show_confirmation(text):
        confirmation_text_label.text = text
        screen.add_view(confirmation_background, lambda w, h, v: (0, h-1, w-1, 1))
        screen.add_view(confirmation_yes_label, lambda w, h, v:  (w-10, h-1, 5, 1))
        screen.add_view(confirmation_no_label, lambda w, h, v:   (w-14, h-1, 4, 1))
        screen.add_view(confirmation_text_label, lambda w, h, v: (2, h-1, w-16, 1))
        update_confirmation_answer_labels()

    def hide_confirmation():
        screen.remove_view(confirmation_background)
        screen.remove_view(confirmation_yes_label)
        screen.remove_view(confirmation_no_label)
        screen.remove_view(confirmation_text_label)


    while 1:
        branch_label.text = '['+stage.active_branch_name()+']'

        screen.render()
        key = stdscr.getch()

        if key == KEY_Q:
            exit(0)

        if confirmation_active:
            if key == curses.KEY_LEFT:
                yes_selected = False
                update_confirmation_answer_labels()

            elif key == curses.KEY_RIGHT:
                yes_selected = True
                update_confirmation_answer_labels()

            elif key == KEY_ENTER:
                confirmation_active = False
                hide_confirmation()
                if yes_selected and confirmation_action is not None:
                    confirmation_action()

        else:
            if key == curses.KEY_UP:
                list_view.select_previous()

            elif key == curses.KEY_DOWN:
                list_view.select_next()

            elif key == KEY_SPACE:
                file = delegate.get_data(list_view.get_selected_row_index())
                if file.is_staged():
                    stage.reset(file)
                else:
                    stage.add(file)
                refresh_stage()
                list_view.select_next()

            elif key == KEY_A:
                all_staged = True
                for file in stage.status():
                    if file.is_staged() is not True:
                        all_staged = False
                        break

                if all_staged:
                    stage.reset_all()
                else:
                    stage.add_all()
                refresh_stage()

            elif key == KEY_I:
                file = delegate.get_data(list_view.get_selected_row_index())
                if file.is_tracked() is not True:
                    stage.ignore(file)
                    refresh_stage()

            elif key == KEY_S:
                if len(stage.status()) > 0:
                    stage.stash_all()
                    refresh_stage()

            elif key == KEY_P:
                stage.pop_stash()
                refresh_stage()

            elif key == KEY_C:
                file = delegate.get_data(list_view.get_selected_row_index())
                if file.is_tracked():
                    confirmation_active = True
                    yes_selected = False
                    confirmation_action = lambda : perform_checkout(file)
                    show_confirmation('Checkout selected file?')

            elif key == KEY_R:
                refresh_stage()

curses.wrapper(main)
