from ui.geometry import Size, Rect


class View:

    def __init__(self):
        pass

    def render(self, stdscr, rect):
        pass

    def required_size(self):
        pass


class ListView(View):

    def __init__(self, data_source, row_factory):
        super().__init__()
        self.__data_source = data_source
        self.__from_index = 0
        self.__to_index = 0
        self.__selected_row_index = 0
        self.__row_factory = row_factory

    def select_next(self):
        self.select_row(self.__selected_row_index + 1)

    def select_previous(self):
        self.select_row(self.__selected_row_index - 1)

    def select_row(self, index):
        self.__selected_row_index = index

    def render(self, stdscr, rect):
        super().render(stdscr, rect)
        n_rows = self.__data_source.number_of_rows()

        self.__clip_selected_row_index(n_rows)
        self.__align_frame(n_rows, rect.height)

        for i in range(self.__from_index, self.__to_index+1):
            if i >= n_rows:
                break

            is_selected = i == self.__selected_row_index
            data = self.__data_source.get_data(i)
            row_view = self.__row_factory.build_row(i, data, is_selected, rect.width)
            row_view.render(stdscr, Rect(rect.x, rect.y+i, rect.width, 1))

    def required_size(self):
        return Size(-1, -1)

    def __clip_selected_row_index(self, n_rows):
        self.__selected_row_index = max(min(n_rows-1, self.__selected_row_index), 0)

    def __align_frame(self, n_rows, n_available_lines):
        # Make sure from is not negative
        self.__from_index = max(self.__from_index, 0)

        # Make sure from <= selected
        self.__from_index = min(self.__from_index, self.__selected_row_index)

        # Make sure the frame is as big as the available space
        self.__to_index = self.__from_index + n_available_lines -1

        # Check if selected > to
        if self.__selected_row_index > self.__to_index:
            self.__to_index = self.__selected_row_index
            self.__from_index = min(0, (self.__to_index - n_available_lines) + 1)


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