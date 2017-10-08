
import logging
import math

from settings import KEY, SECRET
from google.appengine.ext import ndb
from flask import Flask
from flask import jsonify
from datetime import datetime, timedelta
from zaifapi import ZaifPublicApi, ZaifPrivateApi
from model import Price, BTCBidOrder, BTCAskOrder
from decimal import Decimal, ROUND_DOWN


def round_down4(value):
    value = Decimal(value).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
    return float(value)


def get_a_day_ago_price():
    today = datetime.today()
    a_day_ago = today - timedelta(days=1)
    price = Price.get_price_before(a_day_ago)

    if price is not None:
        return int(price.price)
    else:
        return None


def get_minutes_ago_price(minutes):
    today = datetime.today()
    half_hour_ago = today - timedelta(minutes=minutes)
    price = Price.get_price_before(half_hour_ago)

    if price is not None:
        return int(price.price)
    else:
        return None


def get_max_price():
    price = Price.get_max_price()

    if price is not None:
        return int(price.price)
    else:
        return None


def get_btc_last_price():
    zaif = ZaifPublicApi()
    last_price = zaif.last_price('btc_jpy')
    return int(last_price['last_price'])


def get_jpy_and_btc_funds():
    zaif_private = ZaifPrivateApi(KEY, SECRET)
    info = zaif_private.get_info()
    funds_jpy = info['funds']['jpy']
    funds_btc = info['funds']['btc']
    
    return funds_jpy, funds_btc


def get_latest_bid_order_price_and_amount():
    latest_bid_order = BTCBidOrder.get_latest()

    if latest_bid_order is not None:
        return latest_bid_order.price, latest_bid_order.amount
    else:
        return None, None


def delete_latest_order():
    latest_bid_order = BTCBidOrder.get_latest()
    return latest_bid_order.key.delete()
        

def trade_btc(action, amount, price):
    zaif_private = ZaifPrivateApi(KEY, SECRET)
    
    return zaif_private.trade(currency_pair='btc_jpy',
                              action=action,
                              amount=amount,
                              price=int(price))