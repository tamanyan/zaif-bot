# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging
from settings import KEY, SECRET

# from google.cloud import datastore
from google.appengine.ext import ndb
from flask import Flask
from flask import jsonify
from zaifapi import ZaifPublicApi, ZaifPrivateApi


app = Flask(__name__)


@app.route('/save_btc')
def save_btc():
    zaif = ZaifPublicApi()
    return jsonify({'BTC/JPY': zaif.last_price('btc_jpy')})


@app.route('/trade_btc')
def trade_btc():
    logging.info("{} {}".format(KEY, SECRET))
    zaif = ZaifPrivateApi(KEY, SECRET)
    return jsonify({
        'info': zaif.get_info(),
        'orders': zaif.active_orders()
    })


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
