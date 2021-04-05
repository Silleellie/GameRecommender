import json
import pickle

from .Naive import NaiveBayes, EnsembleNaiveBayes
from .Connectors import STEAMConnector, IGDBConnector, STEAMSPYConnector
from tqdm.auto import tqdm


class GameRecommender:
    """
    Class for the Game Recommender
    It supports Naive Bayes recommendation from IGDB and STEAMSPY. It also supports ensamble
    prediction using info retrieved by both data source.
    """
    def __init__(self):
        self.__steam_games = None
        self.__classifier_igdb: NaiveBayes = None
        self.__classifier_spy: NaiveBayes = None

    def load_profile_remote(self, user: str):
        """
        Function that loads a single STEAM profile from STEAM directly.
        The profile extracted is the user passed as parameter

        :param user: username of a STEAM user
        :return: None
        """
        # Create connection to STEAM and extract user profile
        self.__steam_games = STEAMConnector().get_games(user)

    def load_profile_local(self, filepath: str):
        """
        Function that loads from a local file .dat a single STEAM profiles

        :param filepath: location of the dat dumped containing the profile
                    extracted from STEAM
        :return: None
        """
        # Load Steam profile from local filepath
        with open(filepath, "r") as fp:
            self.__steam_games = json.load(fp)

    def save_profile(self, file_name: str):
        """
        Save profiles loaded from STEAM into a file .dat

        :param file_name: name used to rename the file which will be dumped. The function
                    adds '.dat' in automatic to the parameter passed
        :return: None
        """
        with open("{}.dat".format(file_name), "w") as fp:
            json.dump(self.__steam_games, fp)

    def create_model(self, augmentation: int = None):
        """
        Function that instantiates the Naive Bayes models from the info retrieved both from
        STEAMSPY and IGDB. It supports data augmentation for when the games played by a particular user
        are too low. Data Augmentation is supported only for IGDB.

        :param augmentation: number augmented game retrieved for every game of the profile. So if
                    games played are 20 and augmentation==3, IGDB dataset will contain 60 games.
        :return: None
        """

        progbar = tqdm(total=100)

        progbar.set_description("Retrieving games property from IGDB")
        # Create connection to IGDB and create dataset using user profile
        if augmentation is not None:
            dataset_igdb = IGDBConnector().get_dataset_augmented(self.__steam_games, augmentation)
        else:
            dataset_igdb = IGDBConnector().get_dataset(self.__steam_games)
        progbar.update(10)

        progbar.set_description("Retrieving games property from SPY")
        # Create connection to STEAMSpy and create dataset using user profile
        dataset_spy = STEAMSPYConnector().get_dataset(self.__steam_games)
        progbar.update(30)

        progbar.set_description("Fitting first classifier with IGDB data")
        # Fit first classifier with dataset from igdb
        classifier_igdb = NaiveBayes()
        classifier_igdb.fit(dataset_igdb)
        progbar.update(30)

        progbar.set_description("Fitting second classifier with STEAMSpy data")
        # Fit second classifier with dataset from steamspy
        classifier_spy = NaiveBayes()
        classifier_spy.fit(dataset_spy)
        progbar.update(30)
        progbar.close()

        self.__classifier_igdb = classifier_igdb
        self.__classifier_spy = classifier_spy

    def save_model(self, name: str):
        """
        Save the model locally in a file named withe the parameter 'name'
        It will add '.ob' to the file automatically

        :param name: name of the file
        :return: None
        """
        obj = [self.__steam_games, self.__classifier_igdb, self.__classifier_spy]
        with open("{}.rec".format(name), 'wb') as d:
            pickle.dump(obj, d)

    def load_model(self, filepath: str):
        """
        Load the model from a file indicated by 'filepath' parameter

        :param filepath: path of the file to load
        :return: None
        """
        with open(filepath, 'rb') as d:
            obj = pickle.load(d)

        self.__steam_games = obj[0]
        self.__classifier_igdb = obj[1]
        self.__classifier_spy = obj[2]


    def make_prediction_igdb(self, appid: str):
        """
        Calculates how much the game passed will be liked by the user
        using features retrieved from IGDB. The function expects the STEAM game identifier,
        the appid.

        :param appid: game identifer
        :return: prediction of how much the user will like the game
        """
        # Extract game to predict from igdb
        test_igdb = IGDBConnector().get_games([appid])
        test_igdb = test_igdb[0]

        return self.__classifier_igdb.predict(test_igdb), test_igdb['name']

    def make_prediction_steamspy(self, appid: str):
        """
        Calculates how much the game passed will be liked by the user
        using features retrieved from STEAMSPY. The function expects the STEAM game identifier,
        the appid.

        :param appid: game identifer
        :return: prediction of how much the user will like the game
        """
        # Extract game to predict from steamspy
        test_spy = STEAMSPYConnector().get_games([appid])
        test_spy = test_spy[0]

        return self.__classifier_spy.predict(test_spy), test_spy['name']

    def make_ensamble_prediction(self, appid: str):
        """
        Calculates how much the game passed will be liked by the user
        using features retrieved from both STEAMSPY and IGDB. It uses both fitted classifier
        to make an ensamble prediction.
        The function expects the STEAM game identifier, the appid.

        :param appid: game identifer
        :return: prediction of how much the user will like the game
        """
        # Extract game to predict from igdb and steamspy
        test_igdb = IGDBConnector().get_games([appid])
        test_igdb = test_igdb[0]
        test_spy = STEAMSPYConnector().get_games([appid])
        test_spy = test_spy[0]

        # Instantiate ensamble classifier
        ensamble_classifier = EnsembleNaiveBayes({self.__classifier_igdb: test_igdb,
                                                  self.__classifier_spy: test_spy})

        return ensamble_classifier.predict(), test_igdb['name']

    def get_greatest_features(self):
        """
        Function that returns the most liked genres and tags
        based on the user profile

        :return: top-5 genres and top-5 tags
        """
        return self.__classifier_spy.get_greatest_features()
