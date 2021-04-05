from game_recommender import GameRecommender

if __name__ == "__main__":

    rec = GameRecommender()

    rec.load_profile_local('example_database/single_profile/oceanchief.dat')

    rec.create_model()

    appid = '421020'

    pred, game_name = rec.make_prediction_igdb(appid)
    print("------------------------------------------------------------------")
    print("La probabilità secondo dataset igdb che {} ti piaccia è del {}".format(game_name, pred))

    pred, game_name = rec.make_prediction_steamspy(appid)
    print("------------------------------------------------------------------")
    print("La probabilità secondo dataset steamspy che {} ti piaccia è del {}".format(game_name, pred))

    pred, game_name = rec.make_ensamble_prediction(appid)
    print("------------------------------------------------------------------")
    print("La probabilità ensamble che {} ti piaccia è del {}".format(game_name, pred))

    tags, genres = rec.get_greatest_features()
    print("------------------------------------------------------------------")
    print("A te piacciono molto i giochi con questi tags:")
    print("{}, {}, {}, {}, {}".format(tags[0], tags[1], tags[2], tags[3], tags[4]))

    print("------------------------------------------------------------------")
    print("A te piacciono molto i giochi con questi genere:")
    print("{}, {}, {}, {}, {}".format(genres[0], genres[1], genres[2], genres[3], genres[4]))
    print("------------------------------------------------------------------")
