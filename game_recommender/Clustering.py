import pickle
import time
from collections import Counter

from scipy.spatial import distance
from sklearn.cluster import KMeans
import json
import pandas as pd
import statistics
from tqdm.auto import tqdm

from sklearn.preprocessing import StandardScaler

from . import steamapi
from .Connectors import STEAMConnector, IGDBConnector

class KMeansCluster:
    """
    Class that implements KMeans Cluster for recommending top-5 games from the most similar
    profiles extracted from STEAM.
    """
    def __init__(self):
        self.__friends_steam_games = None
        self.__full_dataset: pd.DataFrame = None
        self.__kmeans_model = KMeans()
        self.__scaler = StandardScaler()

    def _get_info_igdb(self, games: list):
        """
        Retrieves info of the games passed as parameter from IGDB.
        It expects a list of games extracted by STEAM.

        :param games:
        :return:
        """
        frame_steam = pd.DataFrame(games)

        appids_list = [g['appid'] for g in games if g['playtime'] > 30]

        if len(appids_list) == 0:
            raise ValueError("No game played")

        list_igdb = IGDBConnector().get_games(appids_list)

        for igdb_game in list_igdb:
            steam_game = frame_steam.loc[frame_steam['appid'] == igdb_game['appid']]
            steam_game = steam_game.to_dict(orient="records")[0]
            igdb_game['playtime'] = steam_game['playtime']
            igdb_game['ach_percentage'] = steam_game['ach_percentage']

        return list_igdb

    def load_friends_local(self, filepath: str):
        """
        Function that loads from a local file .dat multiple STEAM profiles

        :param filepath: location of the dat dumped containing friends profiles
                    extracted from STEAM
        :return: None
        """
        with open(filepath, "r") as fp:
            self.__friends_steam_games = json.load(fp)

        self._get_dataset(self.__friends_steam_games)

    def load_friends_remote(self, user: str):
        """
        Function that loads multiple STEAM profiles from STEAM directly.
        Profiles extracted are the friends of the user passed as parameter

        :param user: username of a STEAM user
        :return: None
        """
        try:
            self.__friends_steam_games = STEAMConnector().get_friends_games(user)
        except steamapi.errors.APIUnauthorized:
            raise steamapi.errors.APIUnauthorized("La lista di amici di queto profilo è privata!"
                                                  "Inserisci un altro profilo")

        self._get_dataset(self.__friends_steam_games)

    def save_friends(self, file_name: str):
        """
        Save profiles loaded from STEAM into a file .dat

        :param file_name: name used to rename the file which will be dumped. The function
                    adds '.dat' in automatic to the parameter passed
        :return: None
        """
        with open("{}.dat".format(file_name), "w") as fp:
            json.dump(self.__friends_steam_games, fp)

    def save_model(self, name: str):
        """
        Save the model locally in a file named withe the parameter 'name'
        It will add '.cl' to the file automatically

        :param name: name of the file
        :return: None
        """
        obj = [self.__friends_steam_games, self.__full_dataset, self.__kmeans_model, self.__scaler]
        with open("{}.cl".format(name), 'wb') as d:
            pickle.dump(obj, d)

    def load_model(self, filepath: str):
        """
        Load the model from a file indicated by 'filepath' parameter

        :param filepath: path of the file to load
        :return: None
        """
        with open(filepath, 'rb') as d:
            obj = pickle.load(d)

        self.__friends_steam_games = obj[0]
        self.__full_dataset = obj[1]
        self.__kmeans_model = obj[2]
        self.__scaler = obj[3]

    def _get_dataset(self, friends_games: dict):
        """
        Function that retrieves game informations from IGDB of the friends game list.
        It creates a full dataset and stores it in the 'self.__full_dataset' attribute of the
        class

        :param friends_games: dict containing friends name and the games played
        :return: None
        """
        friend_games_w_info = []
        t = tqdm(friends_games.keys())
        for friend in t:
            t.set_description("Retrieving game info from friend {}".format(str(friend)))
            time.sleep(.2)
            try:
                games_info = self._get_info_igdb(friends_games[friend])
                for g in games_info:
                    g['friend_name'] = friend

                friend_games_w_info.extend(games_info)
            except ValueError:
                pass

        games_reformatted = []
        for g in friend_games_w_info:
            for feature in g.keys():
                if isinstance(g[feature], list):
                    m = statistics.mean(g[feature])
                    g[feature] = m

            games_reformatted.append(g)

        games_reformatted = pd.DataFrame(games_reformatted)

        games_reformatted = games_reformatted.dropna()

        games_reformatted = games_reformatted.drop_duplicates(subset=['appid'])

        self.__full_dataset = games_reformatted

    def clusterize(self):
        """
        Function that clusterizes friends profiles loaded previously. It scales the features value
        thanks to StandardScaler() from sklearn and then clusterize the friends profiles based on
        their games played.

        :return: None
        """
        reformatted_dataset = self.__full_dataset[self.__full_dataset.columns.difference(['appid', 'friend_name', 'name'])]

        scaled_array = self.__scaler.fit_transform(reformatted_dataset)
        scaled_dataframe = pd.DataFrame(scaled_array, columns=reformatted_dataset.columns)

        self.__kmeans_model.fit(scaled_dataframe)

        self.__full_dataset['cluster'] = self.__kmeans_model.labels_

        friends = set(self.__full_dataset['friend_name'])

        for name in friends:
            subset = self.__full_dataset.loc[self.__full_dataset['friend_name'] == name]
            occurence_count = Counter(subset['cluster'])
            highest = occurence_count.most_common(1)[0][0]

            self.__full_dataset.loc[self.__full_dataset['friend_name'] == name, ['cluster']] = highest

    def predict(self, user: str):
        """
        Given a new profile, the function clusterizes it, and then returns
        the top-5 games liked from the users inside the same cluster.
        It extracts the profile remotely from STEAM in order to clusterize it.

        :param user: profile to clusterize
        :return: top-5 games played by users in the same cluster as a pandas DataFrame
        """
        games = STEAMConnector().get_games(user)
        games = self._get_info_igdb(games)

        games_reformatted = []
        for g in games:

            for feature in g.keys():
                if isinstance(g[feature], list):
                    m = statistics.mean(g[feature])
                    g[feature] = m

            games_reformatted.append(g)

        games_reformatted = pd.DataFrame(games_reformatted)

        games_reformatted = games_reformatted.dropna()

        dataframe_wo_name_appid = games_reformatted[games_reformatted.columns.difference(['appid', 'name'])]

        scaled_array = self.__scaler.transform(dataframe_wo_name_appid)

        scaled_dataframe = pd.DataFrame(scaled_array, columns=dataframe_wo_name_appid.columns)

        clusters = self.__kmeans_model.predict(scaled_dataframe)

        occurence_count = Counter(clusters)
        highest = occurence_count.most_common(1)[0][0]

        # {'user': user, 'cluster': highest}

        friends_same_cluster = self.__full_dataset.loc[self.__full_dataset['cluster'] == highest]

        if friends_same_cluster.empty:
            highest = self._get_nearest_centroid(highest)
            friends_same_cluster = self.__full_dataset.loc[self.__full_dataset['cluster'] == highest]

        appids = list(games_reformatted['appid'])
        friends_same_cluster = friends_same_cluster[~friends_same_cluster['appid'].isin(appids)]

        friends_same_cluster = friends_same_cluster.sort_values(by=['playtime', 'ach_percentage'], ascending=False)

        friends_same_cluster = friends_same_cluster.drop_duplicates(subset=['appid'])

        friends_same_cluster = friends_same_cluster.rename(columns={'name': 'Gioco', 'friend_name': 'Nome_amico'})

        return friends_same_cluster[['Gioco', 'Nome_amico']].head()

    def _get_nearest_centroid(self, cluster: int):
        """
        Private function that calculates the nearest cluster of the cluster passed as
        parameter. Also, the cluster found must contain at least one profile.


        :param cluster: identifier of the cluster of which we must calculate the nearest
                    centroid
        :return: the nearest cluster of the cluster passed as parameter which contains
                at least one profile
        """
        centroid = self.__kmeans_model.cluster_centers_[cluster]

        dist = [distance.euclidean(centroid, cen) for cen in self.__kmeans_model.cluster_centers_]

        empty_cluster = True
        minim = max(dist)
        index_minim = 0
        i = 0
        while empty_cluster:
            for d in dist:
                if d == 0:
                    i += 1
                    continue
                if d < minim or self._is_last_one(dist):
                    minim = d
                    index_minim = i
                i += 1

            frame = self.__full_dataset.loc[self.__full_dataset['cluster'] == index_minim]
            if frame.empty:
                dist[index_minim] = 0
                i = 0
                minim = max(dist)
            else:
                empty_cluster = False

        return index_minim

    def _is_last_one(self, dist: list):
        """
        Private function that checks if there is only one cluster candidate.

        :param dist: list containing euclidean distances
        :return: True if the list contains only one element != 0, false otherwise
        """
        lista_no_0 = [i for i in dist if i != 0]
        if len(lista_no_0) > 1:
            return False
        else:
            return True