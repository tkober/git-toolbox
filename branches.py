import argparse
import os
import curses
import sys
import subprocess
from utils.git import Repository
from gupy.view import Label, HBox, BackgroundView, ListView, ListViewDelegate, ListViewDataSource, View
from gupy.geometry import Padding
from gupy.screen import ConstrainedBasedScreen
from pathlib import Path
from git import GitCommandError

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
    R = ord('r')
    S = ord('s')
    M = ord('m')
    U = ord('u')
    A = ord('a')
    L = ord('l')

class Colorpairs:
    KEY = 1
    DESCRIPTION = 2
    SELECTED = 3
    HEADER_TEXT = 4
    FILTER_CRITERIA = 5
    FILTER_CRITERIA_EDITING = 6
    PATTERN = 7
    ACTIVE = 8
    REMOTE = 9
    DIFF = 10
    CONFIRMATION = 11
    CONFIRMATION_SELECTION = 12
    VIEW = 13

class Legends:

    MAIN = [
        ('[ENTER]', ' Checkout  '),
        ('[UP]', ' Scroll up '),
        ('[DOWN]', ' Scroll down '),
        ('[M]', ' Merge '),
        ('[L]', ' Toggle local/remote '),
        ('[S]', ' Toggle order '),
        ('[F]', ' Filter '),
        ('[C]', ' Clear Filter '),
        ('[R]', ' Refresh '),
        ('[A]', ' Fetch all '),
        ('[U]', ' Toggle upstreams '),
        ('[Q]', ' Quit ')
    ]

    FILTER = [
        ('[ENTER]', ' Quit and save Filter '),
        ('[ESC]', ' Quit and clear Filter ')
    ]

class UI(ListViewDelegate, ListViewDataSource):

    def __init__(self, repo, keepOpen):
        self.errorMessage = None
        self.__repo = repo
        self.__filter = ''
        self.__onlyLocal = True
        self.__sortAscending = False
        self.__keepOpen = keepOpen
        self.isFiltering = False
        self.refreshList()

    def refreshList(self):
        self.__branches = self.__repo.getBranches(self.__onlyLocal)
        self.__filteredBranches = self.__branches
        remotes = self.__repo.remotes()
        self.__maxRemoteNameLength = max([len(remote.name) for remote in remotes]) if len(remotes) else 0
        self.sort()
        self.applyFilter()

    def fetchAll(self):
        self.__repo.fetch()
        self.refreshList()

    def setupColors(self):
        curses.curs_set(0)

        curses.init_pair(Colorpairs.KEY, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(Colorpairs.DESCRIPTION, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Colorpairs.SELECTED, curses.COLOR_BLACK, curses.COLOR_CYAN)

        curses.init_pair(Colorpairs.FILTER_CRITERIA, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(Colorpairs.FILTER_CRITERIA_EDITING, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(Colorpairs.HEADER_TEXT, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Colorpairs.PATTERN, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

        curses.init_pair(Colorpairs.ACTIVE, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(Colorpairs.REMOTE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(Colorpairs.DIFF, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        curses.init_pair(Colorpairs.CONFIRMATION, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(Colorpairs.CONFIRMATION_SELECTION, curses.COLOR_BLACK, curses.COLOR_WHITE)

        curses.init_pair(Colorpairs.VIEW, curses.COLOR_BLUE, curses.COLOR_WHITE)

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

        title_hbox = HBox()

        directoryLabel = Label(title)
        directoryLabel.attributes.append(curses.color_pair(Colorpairs.HEADER_TEXT))
        directoryLabel.attributes.append(curses.A_BOLD)
        title_hbox.add_view(directoryLabel, Padding(0, 0, 0, 0))

        activeBranchLabel = Label('[' + self.__repo.active_branch_name() + ']')
        activeBranchLabel.attributes.append(curses.color_pair(Colorpairs.PATTERN))
        activeBranchLabel.attributes.append(curses.A_BOLD)
        title_hbox.add_view(activeBranchLabel, Padding(1, 0, 0, 0))

        viewLabel = Label('({})'.format('local' if self.__onlyLocal else 'remotes'))
        viewLabel.attributes.append(curses.color_pair(Colorpairs.VIEW))
        viewLabel.attributes.append(curses.A_BOLD)
        title_hbox.add_view(viewLabel, Padding(1, 0, 0, 0))

        screen.add_view(title_hbox, lambda w, h, v: (
        (w - v.required_size().width) // 2, 0, title_hbox.required_size().width + 1, 1))

        return (title_hbox, directoryLabel, activeBranchLabel, viewLabel)

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

        screen.remove_views(self.titleElements)
        if len(self.getFilter()) == 0 and not self.isFiltering:
            self.titleElements = self.addTitle(screen)
        else:
            self.titleElements = []

    def addListView(self, screen):
        listView = ListView(self, self)
        screen.add_view(listView, lambda w, h, v: (0, 1, w, h-2))

        return listView

    def updateConfirmationLabels(self):
        _, _, noLabel, yesLabel = self.confirmationViews;

        noLabel.attributes.clear()
        yesLabel.attributes.clear()

        if self.confirmationYesSelected:
            noLabel.attributes.append(curses.color_pair(Colorpairs.CONFIRMATION))
            yesLabel.attributes.append(curses.color_pair(Colorpairs.CONFIRMATION_SELECTION))
        else:
            noLabel.attributes.append(curses.color_pair(Colorpairs.CONFIRMATION_SELECTION))
            yesLabel.attributes.append(curses.color_pair(Colorpairs.CONFIRMATION))

    def showConfirmation(self, screen, text):

        background = BackgroundView(curses.color_pair(Colorpairs.CONFIRMATION))
        screen.add_view(background, lambda w, h, v: (0, h - 1, w - 1, 1))

        textLabel = Label(text)
        textLabel.attributes.append(curses.color_pair(Colorpairs.CONFIRMATION))
        textLabel.attributes.append(curses.A_BOLD)
        screen.add_view(textLabel, lambda w, h, v:  (2, h-1, w-16, 1))

        noLabel = Label('NO')
        screen.add_view(noLabel, lambda w, h, v:   (w-14, h-1, 4, 1))

        yesLabel = Label('YES')
        screen.add_view(yesLabel, lambda w, h, v: (w-10, h-1, 5, 1))

        self.confirmationViews = (background, textLabel, noLabel, yesLabel)
        self.updateConfirmationLabels()


    def hideConfirmation(self, screen):
        self.confirmationActive = False
        screen.remove_views(self.confirmationViews)

    def applyComfirmedAction(self, screen, action, text):
        self.confirmationActive = True
        self.confirmationYesSelected = False
        self.confirmationAction = action

        self.showConfirmation(screen, text)

    def performMerge(self, branch):
        branchName = '{}/{}'.format(branch.remote, branch.head) if branch.remote else branch.head
        activeBranchName = self.__repo.active_branch_name()

        if branch.head == activeBranchName:

            if branch.remote:
                self.errorMessage = 'error: Command rejected. Merging remote branch \'{}\' into its local counterpart is prohibited.\n' \
                                    '\n'.format(branchName)
            else:
                self.errorMessage = 'error: Command rejected. Merging your local branch \'{}\' into itself is prohibited.'.format(branchName)

            self.stopLoop()
            return

        command = 'cd {} && git merge {}'.format(self.__repo.getDirectory(), branchName)
        subprocess.Popen(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        self.stopLoop()

    def merge(self, screen, branch):
        self.applyComfirmedAction(screen, lambda: self.performMerge(branch), 'Do you want to merge the selected branch into your active?')

    def loop(self, stdscr):

        self.setupColors()
        self.__loopRunning = True

        screen = ConstrainedBasedScreen(stdscr)
        self.titleElements = []
        legendElements = self.addLegend(screen, Legends.MAIN)
        headerElements = self.addHeaderBox(screen)
        listView = self.addListView(screen)

        self.confirmationActive = False
        self.confirmationYesSelected = False
        self.confirmationAction = None

        while self.__loopRunning:
            self.updateHeaderBox(screen, headerElements)

            screen.render()

            key = stdscr.getch()
            if key == curses.KEY_RESIZE:
                continue

            if self.confirmationActive:
                if key == Keys.LEFT:
                    self.confirmationYesSelected = False
                    self.updateConfirmationLabels()

                elif key == Keys.RIGHT:
                    self.confirmationYesSelected = True
                    self.updateConfirmationLabels()

                elif key == Keys.ENTER:
                    self.hideConfirmation(screen)
                    if self.confirmationYesSelected and self.confirmationAction is not None:
                        self.confirmationAction()

            elif self.isFiltering:
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

                elif key in [Keys.LEFT, Keys.RIGHT, Keys.UP, Keys.DOWN]:
                    pass

                else:
                    character = chr(key)
                    self.setFilter(self.getFilter() + character)

            else:
                if key == Keys.ENTER:
                    branch = self.__filteredBranches[listView.get_selected_row_index()]
                    self.checkoutSelectedBranch(branch)

                if key == Keys.F:
                    self.isFiltering = True
                    screen.remove_views(list(legendElements))
                    legendElements = self.addLegend(screen, Legends.FILTER)

                if key == Keys.UP:
                    listView.select_previous()

                if key == Keys.DOWN:
                    listView.select_next()

                if key == Keys.C:
                    self.clearFilter()

                if key == Keys.L:
                    self.toggleLocalOnly()

                if key == Keys.S:
                    self.toggleSortOrder()

                if key == Keys.R:
                    self.refreshList()

                if key == Keys.A:
                    self.fetchAll()

                if key == Keys.M:
                    self.merge(screen, self.__filteredBranches[listView.get_selected_row_index()])

                if key == Keys.Q:
                    self.stopLoop()

    def checkoutSelectedBranch(self, branch):
        if branch.reference == self.__repo.active_branch():
            self.errorMessage = 'error: Branch \'{}\' is already your active branch.\n'.format(branch.reference)

        else:
            try:
                branch.reference.checkout()
            except GitCommandError as e:
                self.errorMessage = e.stderr

        if self.__keepOpen:
            self.refreshList()
        else:
            self.stopLoop()

    def stopLoop(self):
        self.__loopRunning = False

    def getFilter(self):
        return self.__filter

    def setFilter(self, filter):
        self.__filter = filter
        self.applyFilter()

    def clearFilter(self):
        self.setFilter('')

    def applyFilter(self):
        self.__filteredBranches = list(filter(lambda item: self.__filter.lower() in item.head.lower(), self.__branches))
        self.sort()

    def toggleLocalOnly(self):
        self.__onlyLocal = not self.__onlyLocal
        self.refreshList()

    def sort(self):
        self.__filteredBranches = sorted(self.__filteredBranches, key=lambda branch: branch.head, reverse=self.__sortAscending)

    def toggleSortOrder(self):
        self.__sortAscending = not self.__sortAscending
        self.sort()

    def build_row(self, i, data, is_selected, width) -> View:
        rowHBox = HBox()

        if data.remote:
            remoteName = '[{}]'.format(data.remote) if data.remote else ''
            length = self.__maxRemoteNameLength+2
            remoteLabel = Label(remoteName.ljust(length))
            rowHBox.add_view(remoteLabel, Padding(2, 0, 0, 0))

            remoteLabel.attributes.append(curses.color_pair(Colorpairs.REMOTE))
            remoteLabel.attributes.append(curses.A_BOLD)

        isCheckedOut = data.head == self.__repo.active_branch_name() and not data.remote
        checkedOutPrefix = '*' if isCheckedOut else ' '
        headLabel = Label(checkedOutPrefix+data.head)
        rowHBox.add_view(headLabel, Padding(2, 0, 0, 0))

        if isCheckedOut:
            headLabel.attributes.append(curses.color_pair(Colorpairs.ACTIVE))

        if not data.remote:
            diffLabel = Label(data.diff)
            diffLabel.attributes.append(curses.color_pair(Colorpairs.DIFF))
            diffLabel.attributes.append(curses.A_BOLD)
            rowHBox.add_view(diffLabel, Padding(2, 0, 0, 0))

        result = rowHBox
        if is_selected:
            result = BackgroundView(curses.color_pair(Colorpairs.SELECTED))
            result.add_view(rowHBox)
            for label in rowHBox.get_elements():
                label.attributes.append(curses.color_pair(Colorpairs.SELECTED))

        return result

    def number_of_rows(self) -> int:
        return len(self.__filteredBranches)

    def get_data(self, i) -> object:
        return self.__filteredBranches[i]


def parseArguments():
    argparser = argparse.ArgumentParser(
        prog='branches',
        description='Gives you an interactive overview of all branches'
    )
    argparser.add_argument(
        'PATH', nargs="?",
        help='The path to the git repository that shall be used. If no path is provided the current working directory will be used.'
    )
    argparser.add_argument(
        '-k',
        '--keep-open',
        help="The app stays open after checking out a branch",
        action="store_true"
    )
    return argparser.parse_args()


if __name__ == '__main__':
    args = parseArguments()

    if args.PATH:
        repositoryDirectory = os.path.abspath(args.PATH)
    else:
        repositoryDirectory = os.getcwd()
    repo = Repository(repositoryDirectory)

    ui = UI(repo, args.keep_open)
    curses.wrapper(ui.loop)

    if ui.errorMessage:
        print(ui.errorMessage, file=sys.stderr)