import argparse
import os
import curses
from utils.git import Repository
from gupy.view import Label, HBox
from gupy.geometry import Padding
from gupy.screen import ConstrainedBasedScreen

class Colorpairs:
    KEY = 1
    DESCRIPTION = 2
    SELECTED = 3

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
        ('[UP|DOWN]', ' Change Filter Criteria '),
        ('[ESC]', ' Quit and clear Filter ')
    ]

class UI():

    def __init__(self, repo):
        self.__repo = repo

    def setupColors(self):
        curses.curs_set(0)

        curses.init_pair(Colorpairs.KEY, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(Colorpairs.DESCRIPTION, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Colorpairs.SELECTED, curses.COLOR_BLACK, curses.COLOR_CYAN)

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

    def loop(self, stdscr):

        self.setupColors()

        screen = ConstrainedBasedScreen(stdscr)
        self.titleElements = []
        legendElements = self.addLegend(screen, Legends.MAIN)
        #headerElements = self.addHeaderBox(screen)
        #listView = self.addListView(screen)

        self.isFiltering = False

        while 1:
            #self.updateHeaderBox(screen, headerElements)

            screen.render()

            key = stdscr.getch()


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