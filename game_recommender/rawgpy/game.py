"""The class representing a game
"""
from .data_classes import *
from .data_classes import store
from .data_classes import id_name_slug
from .data_classes import platform_
from .data_classes import rating
from .data_classes import store
from . import collection
from . import rawg
from . import user
from . import base
import typing


class Game(base.FromJSONobject):
    """The class representing a Game
    """
    def __new__(cls, *args, **kwargs):
        r = rawg.RAWG()  # get the rawg, this works cause it's a singelton
        slug = args[0]["slug"]  # get the slug of the instance from pure json
        if not r._all_games[slug]:  # check if rawg DOESN'T know a instance with this slug
            r._all_games[slug] = super(Game, cls).__new__(
                cls)  # add the new instance to rawg
        return r._all_games[slug]  # return the instance with this id from rawg

    def __init__(self, json):
        super().__init__(json)  # initialize parent object (FromJSONobject)
        self._collections = None
        self._reactions = None
        self._genrecharts = None
        self._yearcharts = None
        self._charts = None
        self._platforms = None
        self._stores = None
        self._developers = None
        self._categories = None
        self._genres = None
        self._tags = None
        self._publishers = None
        self._esrb = None

    @property
    def reactions(self):
        """The reactions to the game, a list of dictionaries with reaction id as key and amount as value"""
        if not self._reactions:
            self._reactions = [
                {r: num}
                for r, num in self.json.get("reactions", {}).items()
            ]
        return self._reactions

    @property
    def _genrechart(self):
        """the top genre chart for the game, of class :class:`~rawgpy.data_classes.charts.GenreChart`
        
        This shows in what Genre the game is largest
        """
        if not self._genrecharts:
            self._genrecharts = charts.GenreChart(
                self.json.get("charts", {}).get("genre", {}).get("name", ""),
                self.json.get("charts", {}).get(
                    "genre", {}).get("position", ""),
                self.json.get("charts", {}).get("genre", {}).get("change", ""))
        return self._genrecharts

    @property
    def _yearchart(self):
        """The chart place for the game in its release year, of class :class:`~rawgpy.data_classes.charts.YearChart`
        """
        if not self._yearcharts:
            self._yearcharts = charts.YearChart(
                self.json.get("charts", {}).get("year", {}).get("year", ""),
                self.json.get("charts", {}).get(
                    "year", {}).get("position", ""),
                self.json.get("charts", {}).get("year", {}).get("change", ""))
        return self._yearcharts

    @property
    def charts(self):
        """The charts for this game, simply a tuple of :attr:`_genrechart` and :attr:`_yearchart`

        The GenreChart shows what genre this game is most popular in
        The YearChart shows the popularity of the game in its release year
        """
        if not self._charts:
            self._charts = (
                self._genrechart,
                self._yearchart
            )
        return self._charts

    @property
    def platforms(self):
        """The platforms the game is availiable on, list of instances of :class:`~rawgpy.data_classes.platform_.Platform`
        """
        if not self._platforms:
            self._platforms = [
                platform_.Platform(
                    p.get("platform", {}).get("id", ""),
                    p.get("platform", {}).get("name", ""),
                    p.get("platform", {}).get("slug", ""),
                    p.get("platform", {}).get("image", ""),
                    p.get("platform", {}).get("year_end", ""),
                    p.get("platform", {}).get("year_start", ""),
                    p.get("platform", {}).get("games_count", ""),
                    p.get("released_at", ""),
                    p.get("requirements", {}).get("minimum", ""),
                    p.get("requirements", {}).get("maximum", "")
                )
                for p in self.json.get("platforms", [])
            ]
        return self._platforms

    @property
    def stores(self):
        """The stores the game is avaliable on, list of instances of :class:`~rawgpy.data_classes.store.Store`
        """
        if not self._stores:
            self._stores = [
                store.Store(
                    s.get("id", ""),
                    s.get("url", ""),
                    s.get("store", {}).get("id", ""),
                    s.get("store", {}).get("name", ""),
                    s.get("store", {}).get("slug", ""),
                    s.get("store", {}).get("domain", "")
                )
                for s in self.json.get("stores", [])
            ]
        return self._stores

    @property
    def developers(self):
        """The developers that worked on this game, list of instances of :class:`~rawgpy.data_classes.id_name_slug.Developer`
        """
        if not self._developers:
            self._developers = [
                id_name_slug.Developer(
                    d.get("id", ""),
                    d.get("name", ""),
                    d.get("slug", ""),
                    d.get("games_count", "")
                )
                for d in self.json.get("developers", [])
            ]
        return self._developers

    @property
    def categories(self):
        """The categories that apply to this game, list of instances of :class:`~rawgpy.data_classes.id_name_slug.Category`
        """
        if not self._categories:
            self._categories = [
                id_name_slug.Category(
                    d.get("id", ""),
                    d.get("name", ""),
                    d.get("slug", ""),
                    d.get("games_count", "")
                )
                for d in self.json.get("categories", [])
            ]
        return

    @property
    def genres(self):
        """The genres this game falls under, of class :class:`~rawgpy.data_classes.id_name_slug.Genre`
        """
        if not self._genres:
            self._genres = [
                id_name_slug.Genre(
                    d.get("id", ""),
                    d.get("name", ""),
                    d.get("slug", ""),
                    d.get("games_count", "")
                )
                for d in self.json.get("genres", [])
            ]
        return self._genres

    @property
    def tags(self):
        """The tags this game is tagged with, of class :class:`~rawgpy.data_classes.id_name_slug.Tag`
        """
        if not self._tags:
            self._tags = [
                id_name_slug.Tag(
                    d.get("id", ""),
                    d.get("name", ""),
                    d.get("slug", ""),
                    d.get("games_count", "")
                )
                for d in self.json.get("tags", [])
            ]
        return self._tags

    @property
    def publishers(self):
        """The publishers this game was published by, of class :class:`~rawgpy.data_classes.id_name_slug.Publisher`
        """
        if not self._publishers:
            self._publishers = [
                id_name_slug.Publisher(
                    d.get("id", ""),
                    d.get("name", ""),
                    d.get("slug", ""),
                    d.get("games_count", "")
                )
                for d in self.json.get("publishers", [])
            ]
        return self._publishers

    @property
    def esrb(self):
        """The ESRB rating this game got, of class :class:`~rawgpy.data_classes.rating.ESRB`
        """
        if not self._esrb:
            self._esrb = rating.ESRB(
                self.json.get("esrb_rating", {}).get("id", ""),
                self.json.get("esrb_rating", {}).get("name", ""),
                self.json.get("esrb_rating", {}).get("slug", "")
            )
        return self._esrb

    def populate(self):
        """Populates the game by re-requesting the data
        """
        json = self.rawg.game_request(self.slug)
        self.__init__(json)
        return True

    def review(self, text: str, level: str, reaction=None):
        """Adds a review to the game, only works if user is authenticated

        :param text: the review text, empty for none
        :type text: str
        :param level: the name of the rating, as shown on the website
        :type level: str
        :param reaction: a list of reactions, defaults to None
        :type reaction: List[int], optional
        """
        level_strs = {
            "skip": 1, "meh": 3, "recommended": 4, "exceptional": 5
        }
        self.rawg.review_game(
            self.id, level_strs[level_str.lower()], reactions=None, add_to_library=False, text=text)

    @property
    def collections(self):
        """Returns a list of unpopulated :class:`~rawgpy.collections.Collection` objects that this game is part of. 
        """
        if self._collections:
            return self._collections
        gen = self.rawg.game_collections(self.slug)
        all_collections = list(gen)
        self._collections = [collection.Collection(
            json) for json in all_collections]
        return self._collections

    @property
    def suggestions(self):
        """Generator that returns :class:`~rawgpy.game.Game` instances of suggestions made by the rawg Neural Network modell
        """
        for suggestion in self.rawg.game_suggestions(self.slug):
            yield Game(suggestion)

    def edit(self):
        """Sends all edited base variables to rawg
        """
        data = {
            "name": self.name,
            "description": self.description,
            "alternative_names": self.alternative_names,
            "platforms": [p.id for p in self.platforms],
            "genres": [g.id for g in self.genres],
            "publishers": [p.id for p in self.publishers],
            "developers": [d.id for d in self.developers],
            "website": self.website,
            "reddit_url": self.reddit_url,
            "tba": self.tba,
            "released": self.released,
            "metacritic_url": self.metacritic_url
        }
        return self.rawg.patch_game(self.slug, data)

    def collect(self, collection: collection.Collection):
        """Adds this game to the provided collection

        :param collection: the collection object this game should be added to
        :type collection: :class:`~rawgpy.collection.Collection`
        """
        collection.add(self)
