
import logging
from settings import KEY, SECRET

# from google.cloud import datastore
from google.appengine.ext import ndb
from flask import Flask
from flask import jsonify
from datetime import datetime, timedelta
from zaifapi import ZaifPublicApi, ZaifPrivateApi
from model import Price
from google.appengine.api import urlfetch


urlfetch.set_default_fetch_deadline(45)

app = Flask(__name__)


@app.route('/save_btc')
def save_btc():
    zaif = ZaifPublicApi()
    last_price = zaif.last_price('btc_jpy')
    price = Price(price=int(last_price['last_price']))
    price.put()

    return jsonify({'BTC/JPY': price.price})


@app.route('/trade_btc')
def trade_btc():
    today = datetime.today()
    half_hour_ago = today - timedelta(minutes=3)

    q = Price.query(
        Price.datetime <= half_hour_ago)
    q = q.order(-Price.datetime)
    results = q.fetch(1)

    zaif = ZaifPublicApi()
    last_price = zaif.last_price('btc_jpy')

    if len(results) > 0:
        price = results[0]
        now_price = float(last_price['last_price'])
        half_hour_ago_price = float(price.price)
        ratio = (now_price - half_hour_ago_price) / now_price

        logging.info("now {}, more than 30 mins ago {}".format(int(now_price), int(half_hour_ago_price)))
        if ratio > 0:
            logging.info("The price of BTC/JPY {:.3f}% up".format(ratio * 100))
        else:
            logging.info("The price of BTC/JPY {:.3f}% down".format(ratio * 100))

        return jsonify({
            "btc_ratio": round(ratio * 100, 3)
        })

    logging.info("{} {}".format(KEY, SECRET))
    zaif = ZaifPrivateApi(KEY, SECRET)
    return jsonify({
        # 'info': zaif.get_info()
        # 'orders': zaif.active_orders()
    })


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
