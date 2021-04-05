"""
Classes that represent a games chart listing values on rawg
"""


class Chart():
    """parent Chart class
    """

    def __init__(self, position, change):
        """initializes a simple Chart

        :param position: the position of this chart listing
        :type position: int
        :param change: the current change of this chart listing
        :type change: str
        """

        self.position = position
        self.change = change


class GenreChart(Chart):
    """This represents the genre based chart list entry.

if a Game were to have a GenreChart with:
    * :attr:position = 2 
    * :attr:genre = "Shooter"

it would be the second best/most popular shooter game on RAWG
    """

    def __init__(self, genre, position, change):
        """initializes a GenreChart instance

        :param genre: the genre of this chart listing
        :type genre: str
        :param position: the position of this chart listing
        :type position: int
        :param change: the current change of this chart listing
        :type change: str
        """

        super().__init__(position, change)
        self.genre = genre


class YearChart(Chart):
    """a YearChart

if a Game were to have a YearChart with:
    * :attr:position = 2 
    * :attr:year = 2012

it would be the second best/most popular game on rawg in 2012
    """

    def __init__(self, year, position, change):
        """initializes a YearChart instance

        :param year: the year of this chart listing
        :type year: int
        :param position: the position of this chart listing
        :type position: int
        :param change: the current change of this chart listing
        :type change: str
        """

        super().__init__(position, change)
        self.year = year
