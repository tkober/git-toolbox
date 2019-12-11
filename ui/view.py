from ui.geometry import Size


class View:

    def __init__(self):
        pass

    def render(self, stdscr, rect):
        pass

    def required_size(self):
        pass


class ListView(View):

    def __init__(self):
        super().__init__()

    def render(self, stdscr, rect):
        super().render(stdscr, rect)
        stdscr.addstr(0, 0, str(rect.width)+' '+str(rect.height))

    def required_size(self):
        return Size(-1, -1)


class Label(View):

    def __init__(self, text):
        super().__init__()
        self.text = text

    def render(self, stdscr, rect):
        super().render(stdscr, rect)

        if rect.width >= len(self.text):
            stdscr.addstr(rect.y, rect.x, self.text)
        else:
            stdscr.addstr(rect.y, rect.x, self.text[:rect.width-2]+'..')

    def required_size(self):
        return Size(len(self.text), 1)
