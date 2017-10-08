
from google.appengine.ext import ndb


class Price(ndb.Model):
    """Models an BTC/JPY price."""
    price = ndb.IntegerProperty()
    datetime = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_max_price(cls):
        q = Price.query()
        q = q.order(-Price.price)
        results = q.fetch(1)

        if len(results) > 0:
            return results[0]
        else:
            return None

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

    @classmethod
    def cleanup(cls, more_than_before):
        q = Price.query(
            Price.datetime <= more_than_before)
        results = q.fetch()

        if len(results) > 0:
            for i in results:
                i.key.delete()
            return True
        else:
            return False



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
