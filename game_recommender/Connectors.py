from abc import ABC, abstractmethod

import json
from typing import List

from igdb.wrapper import IGDBWrapper
import time
import pandas as pd
import requests
import steamspypi
from tqdm.auto import tqdm
from . import steamapi
from .steamapi.user import SteamUser
from .steamapi.errors import UserNotFoundError
from . import utils

class GameDBConnector(ABC):
    """
    Abstract class that conceptualizes a Connector to a DB containing
    games information
    """

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def is_game_liked(self, game: dict, threshold_percentage: float, threshold_playtime: float):
        """
        Function that calculates if a game is liked or not.
        If the trophies percentage is greater than threshold or if the playtime
        is greater than threshold then the game is liked

        :param game: dict with properties of the game
        :param threshold_percentage: float
        :param threshold_playtime: float
        :return: True if game is liked, False otherwise
        """

        if game['ach_percentage'] is not None and game['ach_percentage'] >= threshold_percentage or \
                game['playtime'] >= threshold_playtime:
            return True
        else:
            return False

    def threshold_calculator(self, games: list):
        """
        Function that calculates the threshold of playtime and the threshold of trophies percentage
        based on the games passed.
        The threshold for both is the average of the playtime and the average of trophies achieved.

        :param games: list containing steam game info
        :return: playtime threshold and trophy threshold
        """
        threshold_percentage = 0
        threshold_playtime = 0
        den_percentage = len(games)
        den_playtime = len(games)
        for g in games:
            if g['ach_percentage'] is not None:

                threshold_percentage += g['ach_percentage']
            else:
                # if game doesn't have trophies, we mustn't count it so
                # we decrease the denominator
                den_percentage -= 1
            threshold_playtime += g['playtime']

        return (threshold_percentage/den_percentage), (threshold_playtime/den_playtime)

    @abstractmethod
    def get_dataset(self, games: list):
        """
        Retrieve games info from the source and create a pandas DataFrame
        :param games: steam games list
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_games(self, appids: List[str]):
        """
        Retrieves games info from the source
        :param appids: list of steam game identifier of which we want to retrieve properties
        :return:
        """
        raise NotImplementedError


class IGDBConnector(GameDBConnector):
    """
    Connector to the IGDB Database
    """
    def __init__(self):
        self.__client_id = "cntz2oqhj91a7cchvsk97rjnjev2oy"
        self.__client_secret = "9b0p0oscbsjc45qcmsr5fp10z49adh"
        self.__igdb_access_token = self.__get_access_token()
        self.__wrapper = IGDBWrapper(self.__client_id, self.__igdb_access_token)

    def __get_access_token(self):
        """
        Function that enables access to IGDB

        :return: connection token to IGDB
        """
        token_url = f"https://id.twitch.tv/oauth2/token?client_id={self.__client_id}" \
                    f"&client_secret={self.__client_secret}&grant_type=client_credentials"
        response = requests.post(token_url).json()
        return response["access_token"]

    def get_games_augmented(self, appids: List[str], augmentation: int):
        """
        Function that retrieves games information from IGDB.
        The features it tries to extract are:
        'genres', 'game_modes', 'player_perspectives', 'themes', 'total_rating', 'involved_companies'.
        The particularity is that for every game retrieved, it retrieves also n similar games chosen by IGDB.
        n is dictated by the parameter 'augmentation'.
        The augmented game(s) is/are retrieved with the same features as the non augmented ones.

        :param appids: list of STEAM game identifiers
        :param augmentation: how many augmented game for every game we want
        :return: games with property retireved
        """
        where_string = "where "
        i = 0
        for appid in appids:
            i += 1
            if i == len(appids):
                where_string += 'category = 1 & uid = "{}";'.format(appid)
            else:
                where_string += 'category = 1 & uid = "{}" | '.format(appid)

        byte_array = self.__wrapper.api_request(
            'external_games',
            'fields uid, game.name, game.genres, game.game_modes,'
            'game.player_perspectives, game.themes, game.total_rating, game.involved_companies.company,'
            'game.similar_games.name, game.similar_games.genres,'
            'game.similar_games.game_modes, game.similar_games.player_perspectives, game.similar_games.themes,'
            'game.similar_games.total_rating, game.similar_games.involved_companies.company;' +
            where_string +
            'limit {};'.format(len(appids))
        )

        game_list = json.loads(byte_array)

        game_list_reformatted = []
        for g in game_list:
            try:
                game_list_reformatted.append(self.__clean(g['game'], g['uid']))
                i = 0
                for similar in g['game']['similar_games']:
                    if i < augmentation:
                        game_list_reformatted.append(self.__clean(similar, g['uid']))
                        i += 1
                    else:
                        break
                del g['game']['similar_games']
            except KeyError:
                continue

        return game_list_reformatted

    def __clean(self, game: dict, uid: str):
        """
        Private function that deletes unnecessary data from the result taken from
        IGDB, such as IGDB id.
        It also refactors the game dictand 'flattens' it.

        :param game: dict containing info of a game retrieved from IGDB
        :param uid: appid of the game
        """

        del game['id']

        game['appid'] = uid

        try:
            companies = []
            for c in game['involved_companies']:
                companies.append(c['company'])

            del game['involved_companies']
            game['companies'] = companies
        except KeyError:
            pass

        try:
            game['rating'] = utils.rating_discretization(game['total_rating'])
            del game['total_rating']
        except KeyError:
            pass

            # for k in game.keys():
            #     if isinstance(game[k], list):
            #         game[k] = [str(i) for i in game[k]]
        return game

    def get_dataset_augmented(self, games: list, augmentation: int):
        """
        Function that retrieve properties of the games listed from IGDB.
        It considers only game played more than 30 minutes.
        The particularity is that for every game in the 'games' parameter, it adds n similar game
        to the dataset and labels them in the same way as the 'parent' game was labeled.
        n is specified by the 'augmentation' parameter.

        :return: dataframe, where every row is a game with the properties extracted and labeled
        """
        frame_steam = pd.DataFrame(games)

        threshold_percentage, threshold_playtime = self.threshold_calculator(games)
        appids_list = [g['appid'] for g in games if g['playtime'] > 30]

        list_igdb = self.get_games_augmented(appids_list, augmentation)
        frame_igdb = pd.DataFrame(list_igdb)

        played_games = frame_igdb[::augmentation+1]

        for index, row in played_games.iterrows():
            steam_game = frame_steam.loc[frame_steam['appid'] == row['appid']]
            steam_game = steam_game.to_dict(orient="records")[0]
            frame_igdb.loc[(frame_igdb['appid'] == row['appid']) & (frame_igdb['name'] == row['name']), 'playtime'] = steam_game['playtime']

        frame_igdb = frame_igdb.sort_values(by=['playtime'], ascending=False)

        list_igdb = frame_igdb.to_dict('records')
        appid_already_labeled = {}
        for igdb_game in list_igdb:
            if igdb_game['appid'] not in appid_already_labeled:
                steam_game = frame_steam.loc[frame_steam['appid'] == igdb_game['appid']]
                steam_game = steam_game.to_dict(orient="records")[0]

                if self.is_game_liked(steam_game, threshold_percentage, threshold_playtime):
                    igdb_game['likes'] = 1
                else:
                    igdb_game['likes'] = 0

                appid_already_labeled[igdb_game['appid']] = igdb_game['likes']
            else:
                igdb_game['likes'] = appid_already_labeled[igdb_game['appid']]

        frame_igdb = pd.DataFrame(list_igdb)

        frame_igdb = frame_igdb.drop_duplicates(subset=['name'])

        return frame_igdb

    def get_dataset(self, games: list):
        """
        Function that retrieves properties of the games listed from IGDB.
        It considers only game played more than 30 minutes.
        :return: dataframe, where every row is a game with the properties extracted and labeled
        """
        frame_steam = pd.DataFrame(games)

        threshold_percentage, threshold_playtime = self.threshold_calculator(games)
        appids_list = [g['appid'] for g in games if g['playtime'] > 30]

        list_igdb = self.get_games(appids_list)

        for igdb_game in list_igdb:
            steam_game = frame_steam.loc[frame_steam['appid'] == igdb_game['appid']]
            steam_game = steam_game.to_dict(orient="records")[0]
            if self.is_game_liked(steam_game, threshold_percentage, threshold_playtime):
                igdb_game['likes'] = 1
            else:
                igdb_game['likes'] = 0

            igdb_game['playtime'] = steam_game['playtime']

        frame_igdb = pd.DataFrame(list_igdb)

        return frame_igdb

    def get_games(self, appids: List[str]):
        """
        Function that retrieves games information from IGDB.
        The features it tries to extract are:
        'genres', 'game_modes', 'player_perspectives', 'themes', 'total_rating', 'involved_companies'.

        :param appids: list of STEAM game identifiers
        :return: games with property retireved
        """

        where_string = "where "
        i = 0
        for appid in appids:
            i += 1
            if i == len(appids):
                where_string += 'category = 1 & uid = "{}";'.format(appid)
            else:
                where_string += 'category = 1 & uid = "{}" | '.format(appid)

        byte_array = self.__wrapper.api_request(
            'external_games',
            'fields uid, game.name, game.genres, game.game_modes,'
            'game.player_perspectives, game.themes, game.total_rating, game.involved_companies.company;' +
            where_string +
            'limit 500;'
        )

        game_list = json.loads(byte_array)

        game_list_reformatted = []
        for g in game_list:
            try:
                game_list_reformatted.append(self.__clean(g['game'], g['uid']))
            except KeyError:
                continue

        return game_list_reformatted


class STEAMSPYConnector(GameDBConnector):
    """
    Connector to the STEAMSPY Database
    """

    def __init__(self):
        pass

    def get_games(self, appids: List[str]):
        """
        Function that retrieves games information from SPYSteam.
        The features it tries to extract are:
        'genres', 'publishers', 'positive', 'negative', 'average_forever', 'tags'.

        :param appids: list of STEAM game identifiers
        :return: games with property retrieved
        """
        games = [self.get_row(app) for app in appids]

        positive_list = [g['positive'] for g in games]
        negative_list = [g['negative'] for g in games]
        playtime_list = [g['average_forever'] for g in games]

        mean_positive = sum(positive_list)/len(positive_list)
        mean_negative = sum(negative_list)/len(negative_list)
        mean_playtime = sum(playtime_list)/len(playtime_list)

        for g in games:
            g['positive'] = self.discretize(mean_positive, g['positive'])
            g['negative'] = self.discretize(mean_negative, g['negative'])
            g['average_forever'] = self.discretize(mean_playtime, g['average_forever'])

        return games

    def get_row(self, appid: str):
        """
        Function that retrieves a game information from SPYSteam.
        The features it tries to extract are:
        'developers', 'genre', 'positive', 'negative', 'average_forever', 'tags'.

        :param appid: STEAM game identifiers
        :return: game with property retrieved
        """
        data_request = dict()
        data_request['request'] = 'appdetails'
        data_request['appid'] = appid

        game = steamspypi.download(data_request)

        game_reformatted = {}
        try:
            game_reformatted['publishers'] = [publisher.strip().lower() for publisher in game['developer'].split(',')]
        except AttributeError:
            pass

        try:
            game_reformatted['genres'] = [genre.strip().lower() for genre in game['genre'].split(',')]
        except AttributeError:
            pass

        game_reformatted['positive'] = game['positive']
        game_reformatted['negative'] = game['negative']
        game_reformatted['average_forever'] = game['average_forever']
        game_reformatted['appid'] = str(game['appid'])
        game_reformatted['name'] = game['name']

        try:
            game_reformatted['tags'] = [tag.strip().lower() for tag in game['tags'].keys()]
        except AttributeError:
            pass

        return game_reformatted

    def get_dataset(self, games: list):
        """
        Function that retrieve properties of the games listed from SPYSteam
        :return: dataframe, where every row is a game with the properties extracted and labeled
        """
        frame_steam = pd.DataFrame(games)

        threshold_percentage, threshold_playtime = self.threshold_calculator(games)
        appids_list = [g['appid'] for g in games if g['playtime'] > 30]

        list_spy = self.get_games(appids_list)

        for spy_game in list_spy:
            steam_game = frame_steam.loc[frame_steam['appid'] == spy_game['appid']]
            steam_game = steam_game.to_dict(orient="records")[0]
            if self.is_game_liked(steam_game, threshold_percentage, threshold_playtime):
                spy_game['likes'] = 1
            else:
                spy_game['likes'] = 0

            spy_game['playtime'] = steam_game['playtime']

        frame_spy = pd.DataFrame(list_spy)

        return frame_spy

    def discretize(self, max: float, continuous: int):
        """
        Function that discretizes a continuous input in 5 ranges

        :param max: the max number of the possible value that the continuous input can be
        :param continuos: the number to discretize
        :return: a number between 1 and 5 representing the range of which the continuous parameter belongs
        """
        ranges = utils.calc_ranges(max, 5)

        for i in ranges.keys():
            range = ranges[i]
            if range[0] <= continuous <= range[1]:
                return [i]

        return [5]  # for numbers greater than last rage return 5, the max


class STEAMConnector:
    """
    Class that implements the connector to STEAM
    """

    def __init__(self):
        self.__api_key = '538BE38F2DBF76F50BF84E02473CC578'
        steamapi.core.APIConnection(api_key=self.__api_key, validate_key=True)


    def get_friends_games(self, user: str):
        """
        Get the profiles of the friends from STEAM of the user passed as parameter.
        Friends profiles contain the game purchased by them and every game is a dict
        containing 'appid', 'name', 'playtime', 'ach_percentage'.

        It returns a dict where every key is a friend, every value are lists of games purchased
        by that friend.
        EXAMPLE:
                {'friend1': [game1, game2, ...], 'friend2': [game1, game2, ...]}


        :param user: id of the user of which we need to extract friends profiles
        :return: dict containing as key a friend, as value games purchased by that friend
        """
        try:
            profile = steamapi.user.SteamUser(userurl=user)
        except UserNotFoundError:
            profile = steamapi.user.SteamUser(userid=int(user))

        friends = profile.friends

        friends_games = {}

        for f in friends:
            try:
                friends_games[f.name] = self.get_games(str(f.steamid))
            except (steamapi.errors.APIPrivate, steamapi.errors.AccessException):
                continue

            time.sleep(2)

        return friends_games

    def __extract_games(self, profile: SteamUser):
        """
        Function that extract games played by the user

        :return: games played by user
        """
        return profile.games

    def get_games(self, user: str):
        """
        Get the profile from STEAM of the user passed as parameter.
        The profile contains the game purchased by the user and every game is a dict
        containing 'appid', 'name', 'playtime', 'ach_percentage'.


        :param user: id of the user of which we need to extract the profile
        :return: list of games purchased by the user
        """

        try:
            profile = steamapi.user.SteamUser(userurl=user)
        except UserNotFoundError:
            profile = steamapi.user.SteamUser(userid=int(user))

        games_objects = self.__extract_games(profile)

        games_list = []

        for g in tqdm(games_objects, desc="Extracting game played by {} from steam".format(profile.name)):
            game = {'appid': str(g.appid),
                    'name': g.name,
                    'playtime': g.playtime_forever}
            try:
                game['ach_percentage'] = g.achievements_percentage
            except (steamapi.errors.APIBadCall, KeyError):

                # IF the game has no trphy there's an exception.
                game['ach_percentage'] = None

            games_list.append(game)

        return games_list

# class RAWGConnector(GameDBConnector):
#     def __init__(self):
#         self.__rawg = rawgpy.RAWG("Game Recommender", "04cd19a2efb04d7aa3f873e8d2b90345")
#
#     def get_row(self, appid: str, name: str):
#         """
#         Extract NAME, GENRES, GAME_MODES, PLAYER_PERSPECTIVE, THEMES,
#         RATING of the given game from IGDB
#         :param appid: str appid of the game
#         :return: dict containing, containing the first game found and its properties
#         """
#         name = re.sub('[^a-zA-Z0-9-_*. ,:;]', '', name)
#
#         games_list = self.__rawg.search(name)
#
#         if len(games_list) != 0:
#             for g in games_list:
#                 g.populate()
#                 for site in g.stores:
#                     if site.small_id == 1:
#                         url = site.url.split('/')
#                         if appid in url:
#                             return self.__extract_properties(g, appid)
#         else:
#             return None
#
#     def __extract_properties(self, game, appid: str):
#         # {name: ...., companies:[], genres:[], keywords: []}
#         game_dict = {}
#         features_list_slug = ['genres', 'tags', 'publishers']
#         features_list_direct = ['name', 'added', 'ratings_count', 'rating']
#         game_dict['appid'] = appid
#
#         for feature in features_list_slug:
#             for element in getattr(game, feature):
#                 if feature == 'tags' and 'steam' in element.slug:
#                     continue
#                 try:
#                     game_dict[feature].append(element.slug)
#                 except KeyError:
#                     game_dict[feature] = [element.slug]
#
#         for feature in features_list_direct:
#             if feature == 'rating':
#                 game_dict[feature] = [int(getattr(game, feature))]
#             elif feature == 'added':
#                 game_dict[feature] = utils.n_added_discretization(getattr(game, feature))
#             elif feature == 'ratings_count':
#                 game_dict[feature] = utils.n_rating_discretization(getattr(game, feature))
#             elif feature == 'name':
#                 game_dict[feature] = getattr(game, feature)
#
#         return game_dict
#
#     def get_dataset(self, games: list):
#         """
#         Function that retrieve properties of the games listed from IGDB
#         :return: dataframe, where every row is a game with the properties extracted
#         """
#         frame_steam = pd.DataFrame(games)
#         n_games = len(games)
#
#         threshold_percentage, threshold_playtime = self.threshold_calculator(games)
#         list_rawg = [self.get_row(g['appid'], g['name']) for g in games if g['playtime'] > 30]
#
#         list_rawg = [i for i in list_rawg if i]
#
#         for rawg_game in list_rawg:
#             steam_game = frame_steam.loc[frame_steam['appid'] == rawg_game['appid']]
#             steam_game = steam_game.to_dict(orient="records")[0]
#             if self.is_game_liked(steam_game, threshold_percentage, threshold_playtime):
#                 rawg_game['likes'] = 1
#             else:
#                 rawg_game['likes'] = 0
#
#             rawg_game['playtime'] = steam_game['playtime']
#
#         frame_rawg = pd.DataFrame(list_rawg)
#
#         return frame_rawg
#
#     def n_rating_discretization(self, n: int):
#         if n < 800:
#             return [1]
#         elif 800 <= n < 1600:
#             return [2]
#         elif 1600 <= n < 3200:
#             return [3]
#         elif 3200 <= n < 4000:
#             return [4]
#         else:
#             return [5]
#
#     def n_added_discretization(self, n: int):
#         if n < 1000:
#             return [1]
#         elif 1000 <= n < 2000:
#             return [2]
#         elif 2000 <= n < 3000:
#             return [3]
#         elif 3000 <= n < 4000:
#             return [4]
#         else:
#             return [5]
