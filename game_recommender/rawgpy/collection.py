"""The class representing a collection
"""

from . import game
from . import rawg
from . import user
from . import base


class Collection(base.FromJSONobject):
    """Class representing a collection of Games
    """
    def __new__(cls, *args, **kwargs):
        r = rawg.RAWG() # uses singleton behaviour
        slug = args[0]["slug"] # args[0] = json
        if not r._all_collections[slug]:
            r._all_collections[slug] = super(Collection, cls).__new__(cls) # create new instance
        return r._all_collections[slug]

    def __init__(self, json):
        super().__init__(json)
        self._creator = None
        self._games = None

    @property
    def creator(self):
        """Returns the unpopulated :class:`~rawgpy.user.User` that made this collection
        """
        if not self._creator:
            self._creator = user.User(self.json["creator"])
        return self._creator

    @property
    def games(self):
        """Returns a list of unpopulated :class:`~rawgpy.game.Game` objects that were added to this collection.
        """
        if self._games:
            return self._games
        gen = self.rawg.collection_games(self.slug)
        all_games = list(gen)
        self._games = [game.Game(json) for json in all_games]
        return self._games

    @property
    def is_mine(self):
        """Returns true if the collection is created by the currently authenticated user, requires authentication
        """
        return self.creator.id == self.rawg.current_user.id

    def populate(self):
        """Populates the collection by re-requesting the data
        """
        json = self.rawg.user_request(self.slug)
        self.__init__(json)
        return True

    def add(self, game):
        """Adds a game to the collection, requires you to be owner of it

        :param game: the game to be adde
        :type game: :class:`~rawgpy.game.Game`, or a list of.
        """
        if not isinstance(game, list):
            game = [game]
        self.rawg.post_request(
            "https://api.rawg.io/api/collections/{}/games".format(self.slug), {
                "games": [g.id for g in game]
            })
