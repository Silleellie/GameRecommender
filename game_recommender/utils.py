def rating_discretization(rating: float):
    """
    Rating discretization for ratings in range [0, 100]
    :param rating: rating to discretize
    :return: rating in range [1,5]
    """
    if 0 <= rating < 20:
        return [1]
    elif 20 <= rating < 40:
        return [2]
    elif 40 <= rating < 60:
        return [3]
    elif 60 <= rating < 80:
        return [4]
    elif 80 <= rating <= 100:
        return [5]


def calc_ranges(number, n_range):
    """
    Function that calc even n_ranges based on the number bassed
    :param number: number of which the range calculation will be based
    :param n_range: how many ranges we must calculate
    :return: ranges
    """
    step = number / n_range
    ranges = {}
    for i in range(n_range):
        ranges[i+1] = [round(step*i), round(step*(i+1))]

    return ranges


def weight_calc(playtime: int, playtime_max: int):
    """
    old
    """
    old_max = playtime_max
    old_min = 0
    new_max = 2
    new_min = 1

    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    multiplier = (((playtime - old_min) * new_range) / old_range) + new_min
    return multiplier


def playtime_probability(playtime: int, playtime_max: int, prob: float):
    """
    old
    """

    weight = weight_calc(playtime, playtime_max)

    return increase_probability(prob, weight)


def increase_probability(prob: float, multiplier: float):
    """
    old
    """
    odds = prob / (1 - prob)

    odds_weighted = odds*multiplier

    prob_weighted = odds_weighted / (odds_weighted + 1)

    return prob_weighted


# def preprocess(summary: str):
#     text = summary.lower()
#
#     text_p = "".join([char for char in text if char not in string.punctuation])
#
#     words = nltk.word_tokenize(text_p)
#
#     stop_words = stopwords.words('english')
#     filtered_words = [word for word in words if word not in stop_words]
#
#     porter = nltk.PorterStemmer()
#     stemmed = [porter.stem(word) for word in filtered_words]
#
#     return stemmed
