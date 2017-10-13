from google.appengine.ext import ndb
from helpers import *
import webapp2


class BidBTCHandler(webapp2.RequestHandler):
    def post(self):
        PERCENTAGE_THRESHOLD = 1.0 # 1% down

        half_hour_ago_price = get_minutes_ago_price(60)
        max_price = get_max_price()
        now_price = get_btc_last_price()

        if max_price is not None:
            if float(now_price) / float(max_price) > 0.98:
                logging.info("The price is too high to trade")
                logging.info("now {}".format(now_price))
                logging.info("max {}".format(max_price))
                logging.info("percentage {:.3f}%".format(float(now_price) / float(max_price)))
                return 

        if half_hour_ago_price is None:
            logging.info("There is not price")
            return

        percentage = ((float(now_price) / float(half_hour_ago_price)) - 1) * 100

        logging.info("now {}".format(now_price))
        logging.info("30 mins {}".format(half_hour_ago_price))

        if percentage > 0:
            logging.info("The price of BTC/JPY {:.3f}% up".format(percentage))
        else:
            logging.info("The price of BTC/JPY {:.3f}% down".format(percentage))

        funds_jpy, funds_btc = get_jpy_and_btc_funds()

        logging.info("The Balance JPY {}  BTC {}".format(funds_jpy, funds_btc))

        # bid BTC
        # if price down PERCENTAGE_THRESHOLD
        if percentage <= -PERCENTAGE_THRESHOLD and funds_jpy > 100:
            amount = round_down4(funds_jpy/now_price)

            trade_btc(action='bid',
                      amount=amount,
                      price=int(now_price))

            bid_order = BTCBidOrder(price=int(now_price), amount=amount)
            bid_order.put()

            logging.info("Bid BTC/JPY price: {}, amount: {}, JPY: {}".format(int(now_price), amount, funds_jpy))


class AskBTCHandler(webapp2.RequestHandler):
    def post(self):
        ASK_PRICE_RATIO = 1.005 # 0.5% up

        latest_price, latest_amount = get_latest_bid_order_price_and_amount()

        # ask BTC
        if latest_price is None:
            logging.info("There is not order")
            return

        funds_jpy, funds_btc = get_jpy_and_btc_funds()
        logging.info("The Balance JPY {}  BTC {}".format(funds_jpy, funds_btc))

        if funds_btc == 0:
            logging.info("funds_btc is empty")
            return

        now_price = int(get_btc_last_price())
        ask_price = (int(latest_price * ASK_PRICE_RATIO) / 5) * 5
        if now_price > ask_price:
            ask_price = now_price

        amount = funds_btc

        logging.info("The latest bid order price: {}, amount: {}".format(latest_price, latest_amount))

        trade_btc(action='ask',
                  amount=amount,
                  price=int(ask_price))

        logging.info("Ask trade {}".format(int(ask_price), amount))

        # delete the latest bid order in order to avoid duplicate order 
        delete_latest_order()

app = webapp2.WSGIApplication([
    ('/bid_btc_worker', BidBTCHandler),
    ('/ask_btc_worker', AskBTCHandler)
], debug=True)
