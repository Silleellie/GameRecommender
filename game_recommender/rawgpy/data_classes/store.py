"""Represents a Store that a game is availiable on
"""


class Store():
    def __init__(self, id_, url, small_id, name, slug, domain):
        self.id = id_  #:
        self.url = url
        self.small_id = small_id
        self.name = name
        self.slug = slug
        self.domain = domain
