"""Represents a Platform that a game is availiable on
"""
class Platform():
    """Represents a Platform
    """
    def __init__(self, id_, name, slug, image, year_end, year_start, games_count, released_at, minimum_requirements, maximum_requirements):
        self.id = id_#: the id of the Platform
        self.name = name#: the name of the Platform
        self.slug = slug#: the slug of the Platform
        self.image = image#: the image url for the Platform
        self.year_end = year_end#: TODO
        self.year_start = year_start#: TODO
        self.games_count = games_count#: the number of games on this Platform
        self.released_at = released_at#: the time this Platform was released at
        self.minimum_requirements = minimum_requirements #: the minimum requirements for the game
        self.maximum_requirements = maximum_requirements#: the optimnal requirements for the game 
