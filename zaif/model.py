
from google.appengine.ext import ndb


class Price(ndb.Model):
    """Models an BTC/JPY price."""
    price = ndb.IntegerProperty()
    datetime = ndb.DateTimeProperty(auto_now_add=True)

    # @classmethod
    # def query_book(cls, ancestor_key):
    #     return cls.query(ancestor=ancestor_key).order(-cls.date)

    @classmethod
    def get_price_before(cls, more_than_before):
        q = Price.query(
            Price.datetime <= more_than_before)
        q = q.order(-Price.datetime)
        results = q.fetch(1)

        if len(results) > 0:
            return results[0]
        else:
            return None


class BTCBidOrder(ndb.Model):
    """Models an BTC/JPY bid order."""
    price = ndb.IntegerProperty()
    amount = ndb.FloatProperty()
    datetime = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_latest(cls):
        q = BTCBidOrder.query()
        q = q.order(-BTCBidOrder.datetime)
        results = q.fetch(1)

        if len(results) > 0:
            return results[0]
        else:
            return None


class BTCAskOrder(ndb.Model):
    """Models an BTC/JPY Ask order."""
    price = ndb.IntegerProperty()
    amount = ndb.FloatProperty()
    datetime = ndb.DateTimeProperty(auto_now_add=True)
