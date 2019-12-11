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


class HBox(View):

    def __init__(self):
        super().__init__()
        self.__elements = []

    def render(self, stdscr, rect):
        super().render(stdscr, rect)

        x_offset = 0
        for view, padding in self.__elements:
            x_offset += padding.left
            required_size = view.required_size()

            if x_offset+required_size.width >= rect.width:
                break

            y = rect.y + padding.top
            x = rect.x + x_offset
            view.render(stdscr, Rect(x, y, required_size.width, required_size.height))

            x_offset += required_size.width + padding.right


    def add_view(self, view, paddding):
        self.__elements.append((view, paddding))

    def required_size(self):
        width = 0
        max_height = 0

        for view, padding in self.__elements:
            required_view_size = view.required_size()
            if required_view_size.width < 0 or required_view_size.height < 0:
                raise Exception('Element views of a HBox need to be able to determine the required size prior to rendering')

            width += padding.left + required_view_size.width + padding.right
            height = padding.top + required_view_size.height + padding.bottom
            max_height = max(max_height, height)

        return Size(width, max_height)