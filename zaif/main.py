
import logging
import math

# from google.cloud import datastore
from settings import KEY, SECRET
from google.appengine.ext import ndb
from flask import Flask
from flask import jsonify
from datetime import datetime, timedelta
from zaifapi import ZaifPublicApi, ZaifPrivateApi
from model import Price, BTCBidOrder, BTCAskOrder
from google.appengine.api import urlfetch
from decimal import Decimal, ROUND_DOWN


urlfetch.set_default_fetch_deadline(120)

app = Flask(__name__)

def round_down4(value):
    value = Decimal(value).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
    return float(value)


@app.route('/cleanup')
def cleanup():
    today = datetime.today()
    a_day_ago = today - timedelta(days=1)
    Price.cleanup(a_day_ago)

    return jsonify({'cleanup': Price.cleanup(a_day_ago)})

@app.route('/save_btc')
def save_btc():
    zaif = ZaifPublicApi()
    last_price = zaif.last_price('btc_jpy')
    price = Price(price=int(last_price['last_price']))
    price.put()

    return jsonify({'BTC/JPY': price.price})


@app.route('/ask_btc')
def ask_btc():
    ASK_PRICE_RATIO = 1.005 # 0.5%

    zaif = ZaifPublicApi()
    last_price = zaif.last_price('btc_jpy')
    now_price = int(last_price['last_price'])

    zaif_private = ZaifPrivateApi(KEY, SECRET)
    info = zaif_private.get_info()
    funds_jpy = info['funds']['jpy']
    funds_btc = info['funds']['btc']

    logging.info("The Balance JPY {}  BTC {}".format(funds_jpy, funds_btc))

    latest_bid_order = BTCBidOrder.get_latest()

    # ask BTC
    if latest_bid_order is not None and funds_btc > 0:
        ask_price = int(latest_bid_order.price * ASK_PRICE_RATIO)
        if now_price > ask_price:
            ask_price = now_price

        amount = funds_btc

        logging.info("The latest bid order price: {}, amount: {}".format(latest_bid_order.price, latest_bid_order.amount))

        zaif_private.trade(currency_pair='btc_jpy',
                            action='ask',
                            amount=amount,
                            price=int(ask_price))

        latest_bid_order.key.delete()

        return jsonify({
            'action': 'ask',
            'BTC/JPY': now_price,
            'bid order price': latest_bid_order.price,
            'ask price': ask_price,
            'amount': amount,
            'contract jpy': ask_price * amount,
            'funcs JPY': funds_jpy,
            'funcs BTC': funds_btc,
        })

    return jsonify({
        'action': None,
        'BTC/JPY': now_price,
        'funcs JPY': funds_jpy,
        'funcs BTC': funds_btc,
    })

@app.route('/bid_btc')
def bid_btc():
    MINITES_BEFORE = 30
    PERCENTAGE_THRESHOLD = 0.2

    today = datetime.today()
    half_hour_ago = today - timedelta(minutes=MINITES_BEFORE)
    price = Price.get_price_before(half_hour_ago)

    zaif = ZaifPublicApi()
    last_price = zaif.last_price('btc_jpy')

    if price is not None:
        now_price = float(last_price['last_price'])
        half_hour_ago_price = float(price.price)
        ratio = ((now_price / half_hour_ago_price) - 1) * 100

        logging.info("now {}, more than 30 mins ago {}".format(int(now_price), int(half_hour_ago_price)))
        if ratio > 0:
            logging.info("The price of BTC/JPY {:.3f}% up".format(ratio))
        else:
            logging.info("The price of BTC/JPY {:.3f}% down".format(ratio))

        zaif_private = ZaifPrivateApi(KEY, SECRET)
        info = zaif_private.get_info()
        funds_jpy = info['funds']['jpy']
        funds_btc = info['funds']['btc']

        logging.info("The Balance JPY {}  BTC {}".format(funds_jpy, funds_btc))

        # bid BTC
        # if price down PERCENTAGE_THRESHOLD
        if ratio <= -PERCENTAGE_THRESHOLD and funds_jpy > 100:
            amount = round_down4(funds_jpy/now_price)

            zaif_private.trade(currency_pair='btc_jpy',
                               action='bid',
                               amount=amount,
                               price=int(now_price))

            bid_order = BTCBidOrder(price=int(now_price), amount=amount)
            bid_order.put()

            logging.info("Bid BTC/JPY price: {}, amount: {}, JPY: {}".format(int(now_price), amount, funds_jpy))

            return jsonify({
                'action': 'bid',
                'BTC/JPY': now_price,
                'funcs JPY': funds_jpy,
                'funcs BTC': funds_btc,
                'amount': amount,
                'BTC changes(%)': "{}%".format(round(ratio, 3))
            })

        return jsonify({
            'action': None,
            'BTC/JPY': now_price,
            'funcs JPY': funds_jpy,
            'funcs BTC': funds_btc,
            'amount': 0,
            'BTC changes(%)': "{}%".format(round(ratio, 3))
        })

    return 'Could not get BTC/JPY price.', 500


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
