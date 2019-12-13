import curses

from ui.geometry import Size, Rect


class View:

    def __init__(self):
        pass

    def render(self, stdscr, rect):
        pass

    def required_size(self):
        pass


class BackgroundView(View):

    def __init__(self, color_pair):
        super().__init__()
        self.color_pair = color_pair
        self.__subviews = []

    def add_view(self, view):
        self.__subviews.append(view)

    def render(self, stdscr, rect):
        super().render(stdscr, rect)

        stdscr.attron(self.color_pair)

        for x_offset in range(0, rect.width):
            for y_offset in range(0, rect.height):
                x = rect.x + x_offset
                y = rect.y + y_offset
                stdscr.addch(y, x, ord(' '))

        stdscr.attroff(self.color_pair)

        for view in self.__subviews:
            view.render(stdscr, rect)


class ListView(View):

    def __init__(self, delegate):
        super().__init__()
        self.delegate = delegate
        self.__from_index = 0
        self.__selected_row_index = 0

    def select_next(self):
        self.select_row(self.__selected_row_index + 1)

    def select_previous(self):
        self.select_row(self.__selected_row_index - 1)

    def select_row(self, index):
        self.__selected_row_index = index

    def render(self, stdscr, rect):
        super().render(stdscr, rect)
        n_rows = self.delegate.number_of_rows()

        self.__clip_selected_row_index(n_rows)
        self.__align_frame(n_rows, rect.height)

        for i in range(0, rect.height):
            item_index = self.__from_index + i

            if item_index >= n_rows:
                break

            is_selected = item_index == self.__selected_row_index
            data = self.delegate.get_data(item_index)
            row_view = self.delegate.build_row(item_index, data, is_selected, rect.width)
            row_view.render(stdscr, Rect(rect.x, rect.y+i, rect.width, 1))

    def required_size(self):
        return Size(-1, -1)

    def __clip_selected_row_index(self, n_rows):
        self.__selected_row_index = max(min(n_rows-1, self.__selected_row_index), 0)

    def __align_frame(self, n_rows, n_available_lines):
        self.__from_index = max(self.__from_index, 0)
        self.__from_index = min(self.__from_index, self.__selected_row_index)

        if self.__selected_row_index >= (self.__from_index + n_available_lines-1):
            self.__from_index = max(0, self.__selected_row_index - n_available_lines +1)

        if self.__from_index + n_available_lines > n_rows:
            self.__from_index = max(0, n_rows - n_available_lines)

    def get_selected_row_index(self):
        return self.__selected_row_index


class Label(View):

    def __init__(self, text=''):
        super().__init__()
        self.text = text
        self.attributes = []

    def render(self, stdscr, rect):
        super().render(stdscr, rect)

        for attribute in self.attributes:
            stdscr.attron(attribute)

        if rect.width >= len(self.text):
            stdscr.addstr(rect.y, rect.x, self.text)
        else:
            stdscr.addstr(rect.y, rect.x, self.text[:rect.width-2]+'..')

        for attribute in self.attributes:
            stdscr.attroff(attribute)

    def required_size(self):
        return Size(len(self.text), 1)


class HBox(View):

    def __init__(self):
        super().__init__()
        self.__elements = []
        self.clipping_callback = None

    def render(self, stdscr, rect):
        super().render(stdscr, rect)

        x_offset = 0
        clipped = False
        for view, padding in self.__elements:
            x_offset += padding.left
            required_size = view.required_size()

            if x_offset+required_size.width >= rect.width:
                clipped = True
                break

            y = rect.y + padding.top
            x = rect.x + x_offset
            view.render(stdscr, Rect(x, y, required_size.width, required_size.height))

            x_offset += required_size.width + padding.right

        if self.clipping_callback is not None:
            self.clipping_callback(clipped)



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

    def get_elements(self):
        return [view for view, _ in self.__elements]