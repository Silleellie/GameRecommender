"""The class representing a User
"""
from . import game
from . import rawg
from . import collection
from . import base


class User(base.FromJSONobject):
    def __new__(cls, *args, **kwargs):
        r = rawg.RAWG()  # singelton behaviour
        slug = args[0]["slug"]  # args[0] = json
        if not r._all_users[slug]:
            r._all_users[slug] = super(User, cls).__new__(cls)  # creates new instance
        return r._all_users[slug]

    def __init__(self, json):
        super().__init__(json)
        self.name = self.username
        self._games = None
        self._playing = None
        self._owned = None
        self._beaten = None
        self._dropped = None
        self._toplay = None
        self._yet = None

    @property
    def games(self):
        """Returns a list of unpopulated :class:`~rawgpy.game.Game` objects that this user has added. 
        """
        if self._games:
            return self._games # return already existing
        gen = self.rawg.user_games(self.slug) # get the generator
        self._games = [game.Game(json) for json in gen] # convert it to list of Game
        return self._games

    @property
    def playing(self):
        """The games this user has makers as playing, list of :class:`~rawgpy.game.Game`
        """
        if self._playing:
            return self._playing
        gen = self.rawg.user_games(self.slug, status="playing")
        self._playing = [game.Game(json) for json in gen]
        return self._playing

    @property
    def owned(self):
        """The games this user has makerd as owned, list of :class:`~rawgpy.game.Game`
        """
        if self._owned:
            return self._owned
        gen = self.rawg.user_games(self.slug, status="owned")
        self._owned = [game.Game(json) for json in gen]
        return self._owned

    @property
    def beaten(self):
        """The games this user has makers as beaten, list of :class:`~rawgpy.game.Game`
        """
        if self._beaten:
            return self._beaten
        gen = self.rawg.user_games(self.slug, status="beaten")
        self._beaten = [game.Game(json) for json in gen]
        return self._beaten

    @property
    def dropped(self):
        """The games this user has makers as dropped, list of :class:`~rawgpy.game.Game`
        """
        if self._dropped:
            return self._dropped
        gen = self.rawg.user_games(self.slug, status="dropped")
        self._dropped = [game.Game(json) for json in gen]
        return self._dropped

    @property
    def toplay(self):
        """The games this user has makers as toplay, list of :class:`~rawgpy.game.Game`
        """
        if self._toplay:
            return self._toplay
        gen = self.rawg.user_games(self.slug, status="toplay")
        self._toplay = [game.Game(json) for json in gen]
        return self._toplay

    @property
    def yet(self):
        """The games this user has makers as yet, list of :class:`~rawgpy.game.Game`
        """
        if self._yet:
            return self._yet
        gen = self.rawg.user_games(self.slug, status="yet")
        self._yet = [game.Game(json) for json in gen]
        return self._yet

    def populate(self):
        """Populates the user by re-requesting the data
        """
        json = self.rawg.user_request(self.slug)
        self.__init__(json)
        return True
