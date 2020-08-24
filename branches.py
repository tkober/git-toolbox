import argparse
import os
import curses
from utils.git import Repository
from gupy.view import Label, HBox, BackgroundView
from gupy.geometry import Padding
from gupy.screen import ConstrainedBasedScreen
from pathlib import Path

class Keys:
    UP = curses.KEY_UP
    DOWN = curses.KEY_DOWN
    LEFT = curses.KEY_LEFT
    RIGHT = curses.KEY_RIGHT
    ESCAPE = 27
    BACKSPACE = 127
    SPACE = ord(' ')
    ENTER = ord('\n')

    F = ord('f')
    Q = ord('q')
    C = ord('c')

class Colorpairs:
    KEY = 1
    DESCRIPTION = 2
    SELECTED = 3
    HEADER_TEXT = 4
    FILTER_CRITERIA = 5
    FILTER_CRITERIA_EDITING = 6
    PATTERN = 7

class Legends:

    MAIN = [
        ('[ENTER]', ' Checkout  '),
        ('[UP]', ' Scroll up '),
        ('[DOWN]', ' Scroll down '),
        ('[M]', ' Merge '),
        ('[R]', ' Toggle remote branches '),
        ('[F]', ' Filter '),
        ('[C]', ' Clear Filter '),
        ('[Q]', ' Quit ')
    ]

    FILTER = [
        ('[ENTER]', ' Quit and save Filter '),
        ('[ESC]', ' Quit and clear Filter ')
    ]

class UI():

    def __init__(self, repo):
        self.__repo = repo
        self.__filter = ''

    def setupColors(self):
        curses.curs_set(0)

        curses.init_pair(Colorpairs.KEY, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(Colorpairs.DESCRIPTION, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Colorpairs.SELECTED, curses.COLOR_BLACK, curses.COLOR_CYAN)

        curses.init_pair(Colorpairs.FILTER_CRITERIA, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(Colorpairs.FILTER_CRITERIA_EDITING, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(Colorpairs.HEADER_TEXT, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Colorpairs.PATTERN, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

    def addLegend(self, screen, legendItems):
        moreLabel = Label('')

        def setMoreLabel(clipped):
            moreLabel.text = '...' if clipped else ''

        legendHBox = HBox()
        legendHBox.clipping_callback = setMoreLabel

        for key, description in legendItems:
            keyLabel = Label(key)
            keyLabel.attributes.append(curses.color_pair(Colorpairs.KEY))
            legendHBox.add_view(keyLabel, Padding(2, 0, 0, 0))

            descriptionLabel = Label(description)
            descriptionLabel.attributes.append(curses.color_pair(Colorpairs.DESCRIPTION))
            legendHBox.add_view(descriptionLabel, Padding(0, 0, 0, 0))

        screen.add_view(legendHBox, lambda w, h, v: (0, h - 1, w - moreLabel.required_size().width, 1))
        screen.add_view(moreLabel, lambda w, h, v: (w - v.required_size().width - 1, h - 1, v.required_size().width, 1))

        return (legendHBox, moreLabel)

    def addHeaderBox(self, screen):

        filterBackground = BackgroundView(curses.color_pair(Colorpairs.HEADER_TEXT))
        screen.add_view(filterBackground, lambda w, h, v: (0, 0, w, 1))

        filterCriteriaLabel = Label()
        filterCriteriaLabel.attributes.append(curses.color_pair(Colorpairs.FILTER_CRITERIA))
        filterCriteriaLabel.attributes.append(curses.A_BOLD)

        filterLabel = Label()
        filterLabel.attributes.append(curses.color_pair(Colorpairs.HEADER_TEXT))

        filterHBox = HBox();
        filterHBox.add_view(filterCriteriaLabel, Padding(0, 0, 0, 0))
        filterHBox.add_view(filterLabel, Padding(0, 0, 0, 0))

        screen.add_view(filterHBox, lambda w, h, v: (0, 0, w, 1))

        return (filterBackground, filterHBox, filterCriteriaLabel, filterLabel)

    def addTitle(self, screen):

        path = Path(self.__repo.getDirectory())
        try:
            relative = path.relative_to(Path.home())
            title = '~/' + str(relative)
        except ValueError:
            pass

        directoryLabel = Label(title)
        directoryLabel.attributes.append(curses.color_pair(Colorpairs.HEADER_TEXT))
        directoryLabel.attributes.append(curses.A_BOLD)

        activeBranchLabel = Label('[' + self.__repo.active_branch_name() + ']')
        activeBranchLabel.attributes.append(curses.color_pair(Colorpairs.PATTERN))
        activeBranchLabel.attributes.append(curses.A_BOLD)

        title_hbox = HBox()
        title_hbox.add_view(directoryLabel, Padding(0, 0, 0, 0))
        title_hbox.add_view(activeBranchLabel, Padding(1, 0, 0, 0))
        screen.add_view(title_hbox, lambda w, h, v: (
        (w - v.required_size().width) // 2, 0, title_hbox.required_size().width + 1, 1))

        return (title_hbox, directoryLabel, activeBranchLabel)

    def updateHeaderBox(self, screen, filterElements):
        _, _, filterCriteriaLabel, filterLabel = filterElements

        filterLabel.text = self.__filter

        filterCriteria = 'FILTER='
        if len(self.getFilter()) > 0:
            filterCriteriaLabel.text = filterCriteria
        else:
            filterCriteriaLabel.text = filterCriteria if self.isFiltering else ''

        filterCriteriaLabel.attributes.clear()
        filterCriteriaLabel.attributes.append(curses.A_BOLD)
        color = curses.color_pair(Colorpairs.FILTER_CRITERIA_EDITING) if self.isFiltering else curses.color_pair(
            Colorpairs.FILTER_CRITERIA)
        filterCriteriaLabel.attributes.append(color)

        if len(self.getFilter()) == 0 and not self.isFiltering:
            self.titleElements = self.addTitle(screen)
        else:
            screen.remove_views(self.titleElements)
            self.titleElements = []

    def loop(self, stdscr):

        self.setupColors()

        screen = ConstrainedBasedScreen(stdscr)
        self.titleElements = []
        legendElements = self.addLegend(screen, Legends.MAIN)
        headerElements = self.addHeaderBox(screen)
        #listView = self.addListView(screen)

        self.isFiltering = False

        while 1:
            self.updateHeaderBox(screen, headerElements)

            screen.render()

            key = stdscr.getch()
            if key == curses.KEY_RESIZE:
                continue

            if self.isFiltering:
                if key == Keys.ESCAPE:
                    self.isFiltering = False
                    screen.remove_views(list(legendElements))
                    legendElements = self.addLegend(screen, Legends.MAIN)
                    self.setFilter('')

                elif key == Keys.ENTER:
                    self.isFiltering = False
                    screen.remove_views(list(legendElements))
                    legendElements = self.addLegend(screen, Legends.MAIN)
                    if len(self.getFilter()) == 0:
                        self.clearFilter()

                elif key == Keys.BACKSPACE:
                    self.setFilter(self.getFilter()[:-1])

                elif key in [Keys.LEFT, Keys.RIGHT]:
                    pass

                else:
                    character = chr(key)
                    self.setFilter(self.getFilter() + character)

            else:
                if key == Keys.F:
                    self.isFiltering = True
                    screen.remove_views(list(legendElements))
                    legendElements = self.addLegend(screen, Legends.FILTER)

                if key == Keys.Q:
                    exit(0)


    def getFilter(self):
        return self.__filter

    def setFilter(self, filter):
        self.__filter = filter
        self.applyFilter()

    def clearFilter(self):
        self.setFilter('')

    def applyFilter(self):
        pass


def parseArguments():
    argparser = argparse.ArgumentParser(
        prog='branches',
        description='Gives you an interactive overview of all branches'
    )
    argparser.add_argument(
        'PATH', nargs="?",
        help='The path to the git repository that shall be used. If no path is provided the current working directory will be used.'
    )
    return argparser.parse_args()


if __name__ == '__main__':
    args = parseArguments()

    if args.PATH:
        repositoryDirectory = os.path.abspath(args.PATH)
    else:
        repositoryDirectory = os.getcwd()
    repo = Repository(repositoryDirectory)

    ui = UI(repo)
    curses.wrapper(ui.loop)