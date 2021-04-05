"""Represents a Rating of a game
"""


class Rating():
    """Represents a rating
    """
    def __init__(self, id_, title, count, percent):
        self.id = id_  #: the ID of the rating
        self.title = title  #: the title of the rating
        self.count = count  #: the amount of these ratings
        self.percent = percent  #: the percent this rating occupies

    def __str__(self):
        return "{title} {percent}%".format(title=self.title, percent=self.percent)

    def __repr__(self):
        return "{title} {percent}%".format(title=self.title, percent=self.percent)
