"""Classes that mostly only have the attributes `id`, `name` and `slug` """
class IdNameSlug():
    """
    base id, name, slug class that is jsut used as a parent to many others
    """
    def __init__(self, id_, name, slug):
        """initializes the base id, name, slug object

        :param id_: the id of the object
        :type id_: int
        :param name: the name of the object
        :type name: str
        :param slug: the slug (url compatible) of the object
        :type slug: str
        """
        self.id = id_
        self.name = name
        self.slug = slug

    def __str__(self):
        """
        the string representation of the object is just its name

        :return: str
        """
        return self.name

    def __repr__(self):
        """
        the machine readable representation is the slug

        :return: str
        """
        return self.slug


class SimplePlatform(IdNameSlug):
    def __init__(self, id_, name, slug):
        """initializes a simple platform object, not to be confused with :class:`~rawgpy.platform_.Platform`

        :param id_: the id of the object
        :type id_: int
        :param name: the name of the object
        :type name: str
        :param slug: the slug (url compatible) of the object
        :type slug: str
        """
        super().__init__(id_, name, slug)


class SimpleStore(IdNameSlug):
    def __init__(self, id_, name, slug):
        """initializes a simple store object, not to be confused with :class:`~rawgpy.store.Store`

        :param id_: the id of the object
        :type id_: int
        :param name: the name of the object
        :type name: str
        :param slug: the slug (url compatible) of the object
        :type slug: str
        """
        super().__init__(id_, name, slug)


class Developer(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        """initializes a simple developer object

        :param id_: the id of the object
        :type id_: int
        :param name: the name of the object
        :type name: str
        :param slug: the slug (url compatible) of the object
        :type slug: str
        :param games_count: the amount of games this developer has made
        :type games_count: int
        """
        super().__init__(id_, name, slug)
        self.games_count = games_count


class Category(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        """initializes a simple category object

        :param id_: the id of the object
        :type id_: int
        :param name: the name of the object
        :type name: str
        :param slug: the slug (url compatible) of the object
        :type slug: str
        :param games_count: the amount of games in this category
        :type games_count: int
        """
        super().__init__(id_, name, slug)
        self.games_count = games_count


class Genre(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        """initializes a simple genre object

        :param id_: the id of the object
        :type id_: int
        :param name: the name of the object
        :type name: str
        :param slug: the slug (url compatible) of the object
        :type slug: str
        :param games_count: the amount of games in this genre
        :type games_count: int
        """
        super().__init__(id_, name, slug)
        self.games_count = games_count


class Tag(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        """initializes a simple tag object

        :param id_: the id of the object
        :type id_: int
        :param name: the name of the object
        :type name: str
        :param slug: the slug (url compatible) of the object
        :type slug: str
        :param games_count: the amount of games with this tag
        :type games_count: int
        """
        super().__init__(id_, name, slug)
        self.games_count = games_count


class Publisher(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        """initializes a simple publisher object

        :param id_: the id of the object
        :type id_: int
        :param name: the name of the object
        :type name: str
        :param slug: the slug (url compatible) of the object
        :type slug: str
        :param games_count: the amount of games this publisher has made
        :type games_count: int
        """
        super().__init__(id_, name, slug)
        self.games_count = games_count


class ESRB(IdNameSlug):
    def __init__(self, id_, name, slug):
        """initializes a simple esrb object

        :param id_: the id of the object
        :type id_: int
        :param name: the name of the object
        :type name: str
        :param slug: the slug (url compatible) of the object
        :type slug: str
        """
        super().__init__(id_, name, slug)
