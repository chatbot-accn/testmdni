from flask import Flask, send_file, make_response
from flask import jsonify
from flask import request
from flask import make_response
from flask import session
import logging
import json
import random
import pandas as pd
import numpy as np
from numpy import mean
from numpy import median
import pickle
import matplotlib as mpl
import matplotlib.pyplot as plt
import io


app = Flask(__name__)

@app.route('/')  # this is the home page route
def welcome():  # this is the home page function that generates the page code
    return "Welcome!"

@app.route('/webhook', methods=['POST'])
def webhook():
    return {
        "fulfillmentText": 'Slot booking Success!!',
        "source": 'webhook'
    }

# run Flask app
if __name__ == "__main__":
    app.run()