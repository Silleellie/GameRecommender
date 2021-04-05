from game_recommender import KMeansCluster

if __name__ == "__main__":

    cl = KMeansCluster()

    cl.load_friends_local("example_database/friends_profile/armadillo_friends.dat")

    cl.clusterize()

    print(cl.predict('silleellie').to_string(index=False))
    print("---------------------------------------------------------------------")
