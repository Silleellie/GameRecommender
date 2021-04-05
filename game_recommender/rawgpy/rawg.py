"""The main rawg class
"""
import requests
import json

from requests.auth import HTTPBasicAuth

from . import base
from . import game
from . import user
from . import collection
from .data_classes import *
from collections import defaultdict
from . import utils


class RAWG(metaclass=utils.Singleton):
    """main RAWG class

    the main class used for interactions with the RAWG.io database
    """

    def __init__(self, user_agent, api_key):
        """init for RAWG class

        :param user_agent: any string to be used as a user agent, should be unique to your project for bandwith monitoring purposes. should include some way of contacting you
        :type user_agent: str
        """
        self.user_agent = user_agent
        self.token = ""
        self.headers = {
            'User-Agent': self.user_agent,
            'content-type': 'application/json'
        }
        self._all_games = defaultdict(lambda: False)
        self._all_users = defaultdict(lambda: False)
        self._all_collections = defaultdict(lambda: False)
        self._api_key = api_key

        base.FromJSONobject._rawg = self

    def get_request(self, url) -> dict:
        """Sends a GET request

        :param url: the url it sends a request to,
        :type url: str
        :return: json-like list / dict structure of the returned json
        :rtype: dict
        """
        url = url.split('?')
        if len(url) != 1:
            url[0] = url[0] + '?key=' + self._api_key + "&"

        url = ''.join(url)
        response = requests.get(
            url, headers=self.headers)
        return response.json()

    def post_request(self, url, data) -> dict:
        """Sends a POST request 

        :param url: The POST url
        :type url: str
        :param data: The POST data
        :type data: dict
        """
        response = requests.post(
            url, headers=self.headers, json=data)
        return response.json()

    def patch_request(self, url, data) -> dict:
        """Sends a PATCH request

        :param url: The PATCH url
        :type url: str
        :param data: The PATCH data
        :type data: dict
        :return: The response json
        :rtype: dict
        """
        response = requests.patch(
            url, headers=self.headers, data=data)
        return response.json()

    def pagination_generator(self, url, results_name="results", next_name="next") -> dict:
        """Generator for pagination based urls, reads the value of `next_name` from the json to get the url for the next request

        uses :attr:`~rawgpy.RAWG.get_request`

        :param url: the url, needs to return some kind of next url value
        :type url: str
        :param results_name: the json key used to return the result, defaults to "results"
        :type results_name: str, optional
        :param next_name: the key used to get the next url, defaults to "next"
        :type next_name: str, optional
        :return: the paginated objects json
        :rtype: dict
        """
        json = self.get_request(url)
        while True:
            results = json.get(results_name, {})
            for res in results:
                yield res
            if not json.get(next_name):
                return
            json = self.get_request(json.get(next_name))

    def search_request(self, query, num_results=5, additional_param="") -> dict:
        """uses the :attr:`~rawgpy.RAWG.get_request` method to search for a game

        :param query: the name of the game that should be searched for
        :type query: str
        :param num_results: the amount of results the search should return
        :type num_results: int
        :param additional_param: any additional search parameter, like `&sorting=-_score` to sort the games by relevance, excluding popularity
        :return: json-like list / dict structure of the returned json
        :rtype: dict
        """
        url = "https://rawg.io/api/games?page_size={number}&search={query}".format(
            number=num_results, query=query)
        return self.get_request(url)

    def game_request(self, slug, additional_param="") -> dict:
        """uses the :attr:`~rawgpy.RAWG.get_request` method to get a specific games json

        :param slug: the slug of the game that shoudl be returned, needs to be correct rawg slug
        :type slug: str
        :param additional_param: any additional request parameter
        :return: json-like list / dict structure of the returned json
        :rtype: dict
        """
        url = "https://api.rawg.io/api/games/{slug}".format(slug=slug)
        return self.get_request(url)

    def search(self, query, num_results=5, additional_param="") -> game.Game:
        """searches for games

        :param query: the search query
        :type query: str
        :param num_results: the amount of results, defaults to 5
        :type num_results: int, optional
        :param additional_param: additional get parameters, defaults to ""
        :type additional_param: str, optional
        """
        search_res = self.search_request(query, num_results, additional_param)
        results = [game.Game(j)
                   for j in search_res.get("results", {})]
        return results

    def get_game(self, slug) -> game.Game:
        """get a specific game

        :param slug: the slug of the game
        :type slug: str
        :return: the game object
        :rtype: ~rawgpy.game.Game
        """
        return game.Game(self.game_request(slug))

    def user_request(self, slug) -> dict:
        """Returns a user json

        :param slug: the users slug
        :type slug: str
        :return: the users json
        :rtype: dict
        """
        return self.get_request("https://api.rawg.io/api/users/{slug}".format(slug=slug))

    def get_user(self, slug) -> user.User:
        """gets a user :class:`~rawgpy.user.User`

        :param slug: the userslug
        :type slug: str
        :return: user json
        :rtype: dict
        :return: generator of the collections json
        :rtype: ~rawgpy.user.User
        """
        return user.User(self.user_request(slug))

    def login(self, email, password):
        """Logs the user in, autheticating all subsequent requests with that user

        :param email: The users email
        :type email: str
        :param password: The users password
        :type password: str
        """
        response = self.post_request(
            "https://api.rawg.io/api/auth/login", {"email": email, "password": password})
        if response.get("non_field_errors"):
            raise ValueError(response.get("non_field_errors"))
        if response.get("email"):
            raise ValueError(response.get("email"))
        if response.get("password"):
            raise ValueError(response.get("password"))
        try:
            self.token = response.get("key")
            self.headers["token"] = "Token " + self.token
        except KeyError:
            raise ValueError(response)

    def user_games(self, slug, status=None):
        """generator that yields the users games json

        :param slug: the users slug
        :type slug: str
        :param status: the status of the game in the users library, can be `playing`, `owned`, `beaten`, `dropped`, `toplay`, `yet` defaults to "playing"
        :type status: str, optional
        :return: generator of the games json
        :rtype: ~rawgpy.RAWG.pagination_generator
        """
        if not status:
            return self.pagination_generator("https://api.rawg.io/api/users/{}/games".format(slug))
        else:
            return self.pagination_generator("https://api.rawg.io/api/users/{}/games?statuses={}".format(slug, status))

    def game_suggestions(self, slug):
        """generator that yields the suggested games for a game

        :param slug: the game slug
        :type slug: str
        :return: generator of the games json
        :rtype: ~rawgpy.RAWG.pagination_generator
        """
        return self.pagination_generator("https://api.rawg.io/api/games/{}/suggested".format(slug))

    def review_data(game_id: int, level, reactions=None, add_to_library=False, text="", post_twitter=False, post_facebook=False) -> dict:
        """creates the data for review operations

        :param game_id: the int id of the game
        :type game_id: int
        :param level: 1 = skip, 3 = meh, 4 = Recommended, 5 = Exceptional
        :type level: int
        :param reactions: List of the reactions to add, defaults to None
        :type reactions: List[int], optional
        :param add_to_library: whether the game whouls be added to the authenticated users library, defaults to False
        :type add_to_library: bool, optional
        :param text: the review text, uses html formats like <br>, defaults to ""
        :type text: str, optional
        :param post_twitter: whether to post on twitter, defaults to False
        :type post_twitter: bool, optional
        :param post_facebook: whether to post on facebook, defaults to False
        :type post_facebook: bool, optional
        :return: The data that has been made
        :rtype: dict
        """
        data = {"game": game_id, "rating": 5, "post_facebook": post_facebook,
                "post_twitter": post_twitter, "add_to_library": add_to_library}
        if len(text) > 0:
            data["text"] = text
        if isinstance(reactions, list):
            data["reactions"] = reactions
        return data

    def review_game(self, game_id: int, level, reactions=None, add_to_library=False, text="", post_twitter=False, post_facebook=False):
        """Adds a review to a game

        :param game_id: the int id of the game
        :type game_id: int
        :param level: 1 = skip, 3 = meh, 4 = Recommended, 5 = Exceptional
        :type level: int
        :param reactions: List of the reactions to add, defaults to None
        :type reactions: List[int], optional
        :param add_to_library: whether the game whouls be added to the authenticated users library, defaults to False
        :type add_to_library: bool, optional
        :param text: the review text, uses html formats like <br>, defaults to ""
        :type text: str, optional
        :param post_twitter: whether to post on twitter, defaults to False
        :type post_twitter: bool, optional
        :param post_facebook: whether to post on facebook, defaults to False
        :type post_facebook: bool, optional
        """
        self.post_request("https://api.rawg.io/api/reviews",
                          self.review_data(level, reactions=reactions, add_to_library=add_to_library, text=text, post_twitter=post_twitter, post_facebook=post_facebook))

    def game_collections(self, game_slug):
        """Retrieve the collections a game is a part of

        :param game_slug: the slug of the game
        :type game_slug: str.
        :return: generator of the collections json
        :rtype: ~rawgpy.RAWG.pagination_generator
        """
        return self.pagination_generator(
            "https://api.rawg.io/api/games/{}/collections".format(game_slug))

    def collection_games(self, slug):
        """generator that yields the collections games json

        :param slug: the slug of the collection
        :type slug: str
        :return: generator of the games json
        :rtype: ~rawgpy.RAWG.pagination_generator
        """
        return self.pagination_generator(
            "https://api.rawg.io/api/collections/{}/feed".format(slug))

    def collection_request(self, slug) -> dict:
        """Returns the collection json

        :param slug: the collection slug
        :type slug: str
        :return: The collection json
        :rtype: dict
        """
        return self.get_request("https://api.rawg.io/api/collections/{}".format(slug))

    def get_collection(self, slug) -> collection.Collection:
        """Returns the collection object

        :param slug: the collection slug
        :type slug: str
        :return: The collection object
        :rtype: ~rawgpy.collection.Collection
        """
        return collection.Collection(self.collection_request(slug))

    def current_user_request(self) -> dict:
        """Returns the currently authenticated user json

        :return: Json of the authenticated user
        :rtype: dict
        """
        json = self.get_request("https://api.rawg.io/api/users/current")
        if json.get("detail", "").startswith("Authentication credentials"):
            raise AttributeError(json["detail"])
        return json

    def current_user(self) -> user.User:
        """Returns the currently authenticated user

        :return: The currently authenticated user
        :rtype: ~rawgpy.user.User
        """
        return user.User(self.current_user_request())

    def patch_game(self, slug, data):
        """Patch (edit) a game

        :param slug: The games slug
        :type slug: str
        :param data: The edited data
        :type data: dict
        :return: The response json
        :rtype: dict
        """
        return self.patch_request("https://api.rawg.io/api/games/{}".format(slug), data)

    def create_collection(self, name, description) -> collection.Collection:
        """creates a new collection

        :param name: Name of the collection
        :type name: str
        :param description: Description of the collection
        :type description: str
        :return: Collection object of created collection
        :rtype: ~rawgpy.collection.Collection
        """
        if len(name) > 50:
            raise ValueError("name has a character limit of 50")
        if len(description) > 512:
            raise ValueError("description has a character limit of 512")
        data = {
            "name": name,
            "description": description
        }
        return collection.Collection(self.post_request("https://api.rawg.io/api/collections", data))
