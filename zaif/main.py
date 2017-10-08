
import logging
import math

from helpers import *
from settings import KEY, SECRET
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from flask import Flask
from flask import jsonify
from datetime import datetime, timedelta
from zaifapi import ZaifPublicApi, ZaifPrivateApi
from model import Price, BTCBidOrder, BTCAskOrder
from decimal import Decimal, ROUND_DOWN


app = Flask(__name__)


@app.route('/cleanup')
def cleanup():
    # delete prices of 2 days ago
    today = datetime.today()
    two_day_ago = today - timedelta(days=2)
    Price.cleanup(two_day_ago)

    return jsonify({'cleanup': Price.cleanup(two_day_ago)})


@app.route('/save_btc')
def save_btc():
    price = Price(price=int(get_btc_last_price()))
    price.put()

    return jsonify({'BTC/JPY': price.price})


@app.route('/ask_btc')
def ask_btc():
    taskqueue.add(
            url='/ask_btc_worker',
            target='worker',
            params={})

    return jsonify({
        'message': 'enqueue ask BTC worker',
    })


@app.route('/bid_btc')
def bid_btc():
    taskqueue.add(
            url='/bid_btc_worker',
            target='worker',
            params={})

    return jsonify({
        'message': 'enqueue bid BTC worker',
    })


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500