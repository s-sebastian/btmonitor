class YearConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f'{value:04}'


class MonthConverter:
    regex = '[0-9]{2}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f'{value:02}'
