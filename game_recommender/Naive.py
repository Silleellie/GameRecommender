import pandas as pd

from . import utils


class NaiveBayes:
    """
    Class that implements a Naive Bayes Model
    """

    def __init__(self):
        self.__CPT = {}
        self.__num_smoothed = 1
        self.__den_smoothed = -1
        self.__n_liked = -1
        self.__n_disliked = -1

    # CALCOLO priori
    def __calc_y(self, dataset: pd.DataFrame):
        """
        Function that calculates the prior probability that the user
        will like a new game.
        To calculate said prior probability, the function will use the column 'likes' of
        the dataset and will calculate games_liked/games_played.
        The result will be inserted into CPT attribute of the Class
        EXAMPLE:
            IF a user likes 40 games out of 50, then it will probably like a new game
            Instead, IF a user likes 10 games out of 50, then it won't probably like a new game

        :param dataset: Dataframe containing games played by the user.
                        Columns of the Dataframe are the features
                        EXAMPLE: ...| genre | game_modes | player_perspective | likes ...
                                 ...|  rpg  |     1      |         2          |   1 ...
        """
        games_liked = (dataset.likes == 1).sum()
        games_played = len(dataset.likes)

        self.__CPT.update({'likes': games_liked / games_played})

    # CALCOLO posteriori
    def __calc_xi_after_y(self, dataset: pd.DataFrame, val_feature: str, feature: str):
        """
        Function that calculates the posterior probability of the specified
        value of a given feature.
        It will be calculated the positive probability as well as the
        negative probability.
        Laplace Smoothing is used to avoid 0 probabilities
        EXAMPLE:
                calc_xi_after_y(dataset, 'rpg', 'genre') will calculate:
                P(genre='rpg'| likes) -----> how many games are rpg that the user liked
                P(genre='rpg'| -likes) ----> how many games are rpg the the user didn't like

        :param dataset: Dataframe containing games that the user played
        :param val_feature: str representing value of the feature needed for the
                            posterior probability
        :param feature: str representing feature of which the posterior probability
                        will be calculated
        """
        # LAPLACE
        num_likes = self.__num_smoothed
        den_likes = self.__den_smoothed
        num_dislikes = self.__num_smoothed
        den_dislikes = self.__den_smoothed
        max_playtime_feature = 0
        max_playtime_total = dataset['playtime'].max()

        for index, row in dataset.iterrows():
            if row['likes'] == 1:
                den_likes += 1
                try:
                    if val_feature in [str(el) for el in row[feature]]:
                        num_likes += 1
                        # if row['playtime'] > max_playtime_feature:
                        #     max_playtime_feature = row['playtime']
                except TypeError:
                    # if the feature isn't present for a game
                    # we don't consider it
                    den_likes -= 1
                    continue
            else:
                den_dislikes += 1
                try:
                    if val_feature in [str(el) for el in row[feature]]:
                        num_dislikes += 1
                except TypeError:
                    # if the feature isn't present for a game
                    # we don't consider it
                    den_dislikes -= 1
                    continue

        prob = num_likes/den_likes

        # prob_likes_weighted = utils.playtime_probability(
        #     playtime=max_playtime_feature,
        #     playtime_max=max_playtime_total,
        #     prob=prob
        # )

        self.__CPT.update(
            {feature + '=' + str(val_feature) + '| likes': prob,
             feature + '=' + str(val_feature) + '| -likes': (num_dislikes / den_dislikes)}
        )

    def save_dom(self, dataset: pd.DataFrame, feature: str):
        """
        Function that extracts the domain of a feature.
        The domain corresponds of all the value of that feature in the dataset,
        If in the online phase a feature with a new value is given, then its probability must
        be minimum.


        :param dataset: games dataset
        :param feature: feature of which we want to extract its domain
        :return: domain of the feature
        """
        if feature == 'rating' or feature == 'average_forever' or feature == 'positive'\
                or feature == 'negative':
            dom = {1, 2, 3, 4, 5}
        else:
            # we extract all values that a column have
            all_values = dataset[feature].tolist()
            # we flatten the list
            flat_dom = []
            for sublist in all_values:
                try:
                    for item in sublist:
                        flat_dom.append(item)
                except TypeError:
                    continue

            # we take only unique values from the flattened_list
            dom = set(flat_dom)

        return dom

    def __calc_den_smoothed(self, dataset: pd.DataFrame):
        """
        Private function that calculates Laplace smoothing.
        It uses the features of the dataset - irrelevant features of the dataset
        such as appid, name of the game, the label etc.

        :param dataset:
        :return:
        """
        features_list = list(dataset.columns.values)
        features_irrelevant = ['appid', 'likes', 'name', 'playtime']
        intersection = [value for value in features_list if value not in features_irrelevant]

        self.__den_smoothed = len(intersection)

    def fit(self, dataset: pd.DataFrame):
        """
        Fit the Naive Bayes model with the dataset passed as parameter.
        It is fitted by calculating the prior probability and the posterior probabilities.
        All of them are then stored in the attribute CPT.


        :param dataset: DataFrame containing infos on which the Naive Bayes must be fit
        :return: None
        """
        self.__n_liked = len(dataset.loc[dataset['likes'] == 1])
        self.__n_disliked = len(dataset.loc[dataset['likes'] == 0])
        self.__calc_den_smoothed(dataset)
        self.__calc_y(dataset)
        for feature in dataset.columns:
            if feature != 'appid' and feature != 'likes' and feature != 'name' and feature != 'playtime':
                dom = self.save_dom(dataset, feature)

                for element in dom:
                    self.__calc_xi_after_y(dataset, str(element), feature)

    def __merge_probabilities(self, feature: str, values: list):
        """
        Private function that merges probabilites of multiple feture values.
        EXAMPLE:
                genres = [rpg, action]

                Calculates the average of P(likes=1| genres=rpg) and P(likes=1| genres=action),
                as well as the negative probabilites P(likes=0| genres=rpg) and P(likes=0| genres=action)

        :param feature: feature name
        :param values: lsit containing multiple values for the feature
        :return: positive probability and negative probability
        """
        total_likes = 0
        total_dislikes = 0
        for v in values:
            field = feature + '=' + str(v)
            try:
                total_likes += self.__CPT[field + "| likes"]
                total_dislikes += self.__CPT[field + "| -likes"]
            except KeyError:
                total_likes += self.__num_smoothed/(self.__den_smoothed + self.__n_liked)
                total_dislikes += self.__num_smoothed/(self.__den_smoothed + self.__n_disliked)

        return total_likes/len(values), total_dislikes/len(values)

    def predict(self, x_pred: dict):
        """
        Function that calculates probability that the user will like given game (x_pred)

        :param x_pred: dict containing features of the game
        :return: like probability
        """
        p_likes = self.__CPT['likes']
        p_dislikes = 1 - self.__CPT['likes']
        for feature in x_pred.keys():
            if feature != 'appid' and feature != 'name' and x_pred.get(feature) is not None:
                result = self.__merge_probabilities(feature, x_pred[feature])
                p_likes *= result[0]
                p_dislikes *= result[1]

        c = 1 / (p_likes + p_dislikes)
        return p_likes * c

    def get_greatest_features(self):
        """
        Function that returns genres and tags value with the highest posterior probabilities

        :return: most liked tags, most liked genres
        """
        dicto = dict(sorted(self.__CPT.items(), key=lambda item: item[1], reverse=True))
        tags_liked = []
        genres_liked = []

        tags = [(key, value) for key, value in dicto.items() if key.startswith("tags")]
        for t in tags:
            tag_string = t[0]
            tag_string = [x.strip() for x in tag_string.split('|')]
            if tag_string[1] == 'likes':
                tags_liked.append(tag_string[0])

            if len(tags_liked) == 5:
                break

        genres = [(key, value) for key, value in dicto.items() if key.startswith("genres")]
        for g in genres:
            genre_string = g[0]
            genre_string = [x.strip() for x in genre_string.split('|')]
            if genre_string[1] == 'likes':
                genres_liked.append(genre_string[0])

            if len(genres_liked) == 5:
                break

        tags_liked = [x.split("=")[1] for x in tags_liked]
        genres_liked = [x.split("=")[1] for x in genres_liked]

        return tags_liked, genres_liked

class EnsembleNaiveBayes:
    """
    Class for Ensamble prediction

    Attributes:
        clf_and_test (dict): dict containing model fitted and game to predict
                EXAMPLE:
                    EnsambleNaiveBayes({clf_igdb: [game, multiplier], clf_spysteam: [game, multiplier]})
    """

    def __init__(self, clf_and_test: dict):
        self.__clf_and_test: dict = clf_and_test

    def predict(self):
        """
        Calculates ensemble prediction using all classifier passed in the constructor
        on the game passed in the constructor
        The ensemble prediction is made by averaging the predictions made by clfs
        passed in the constructor

        :return: ensemble prediction
        """
        total = 0
        for clf in self.__clf_and_test.keys():
            total += clf.predict(self.__clf_and_test[clf])

        return total/len(self.__clf_and_test)