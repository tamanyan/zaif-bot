
from google.appengine.ext import ndb


class Price(ndb.Model):
    """Models an BTC/JPY price."""
    price = ndb.IntegerProperty()
    datetime = ndb.DateTimeProperty(auto_now_add=True)

    # @classmethod
    # def query_book(cls, ancestor_key):
    #     return cls.query(ancestor=ancestor_key).order(-cls.date)