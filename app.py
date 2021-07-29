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

@app.route('/') # this is the home page route
def hello_world(): # this is the home page function that generates the page code
    return "Hello world!"
    
@app.route('/webhook', methods=['POST'])
def webhook():
  req = request.get_json(silent=True, force=True)
  fulfillmentText = ''
  sum = 0
  query_result = req.get('queryResult')
  if query_result.get('action') == 'add.numbers':
    num1 = int(query_result.get('parameters').get('number'))
    num2 = int(query_result.get('parameters').get('number1'))
    sum = str(num1 + num2)
    print('here num1 = {0}'.format(num1))
    print('here num2 = {0}'.format(num2))
    fulfillmentText = 'The sum of the two numbers is '+sum
  elif query_result.get('action') == 'multiply.numbers':
    num1 = int(query_result.get('parameters').get('number'))
    num2 = int(query_result.get('parameters').get('number1'))
    product = str(num1 * num2)
    print('here num1 = {0}'.format(num1))
    print('here num2 = {0}'.format(num2))
    fulfillmentText = 'The product of the two numbers is '+product
  return {
        "fulfillmentText": fulfillmentText,
        "source": "webhookdata"
    }
    
 
# run Flask app
if __name__ == "__main__":
    app.run()
