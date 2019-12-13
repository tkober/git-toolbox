from ui.geometry import Rect

class Screen:

    def __init__(self, stdscr):
        self.stdscr = stdscr

    def begin_redndering(self):
        self.stdscr.clear()

    def end_redndering(self):
        self.stdscr.refresh()

    def render(self):
        self.begin_redndering()
        self.end_redndering()

    def getViews(self):
        pass


class StackedScreen(Screen):

    def __init__(self, stdscr, views=[]):
        super().__init__(stdscr)
        self.__views = views

    def add_view(self, view):
        self.__views.append(view)

    def render(self):
        self.begin_redndering()

        screen_height, screen_width = self.stdscr.getmaxyx()
        rect = Rect(0, 0, screen_width, screen_height)
        for view in self.__views:
            view.render(self.stdscr, rect)

        self.end_redndering()

    def getViews(self):
        return [view for view in self.__views]


class ConstrainedBasedScreen(Screen):

    def __init__(self, stdscr):
        super().__init__(stdscr)
        self.__views = []

    def add_view(self, view, placement_calc):
        self.__views.append((view, placement_calc))

    def remove_view(self, view):
        for item in self.__views:
            v, _ = item
            if v == view:
                self.__views.remove(item)
                break

    def render(self):
        self.begin_redndering()

        screen_height, screen_width = self.stdscr.getmaxyx()
        for view, placement_calc in self.__views:
            x, y, width, height = placement_calc(screen_width, screen_height, view)
            x = min(max(x, 0), screen_width)
            y = min(max(y, 0), screen_height)
            rect = Rect(x, y, width, height)
            view.render(self.stdscr, rect)

        self.end_redndering()

    def get_views(self):
        return [view for view, _ in self.__views]
