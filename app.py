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


logger = logging.getLogger() 
logger.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')


xls = pd.ExcelFile(r'Credit_Risk-Dummy Input Data-20190522.xlsx')
data = pd.read_excel(xls, 'Data')
sheet2 = pd.read_excel(xls, 'Dimensions')


#data = data.astype({"Exposure": int})

app = Flask(__name__)

@app.route('/') # this is the home page route
def hello_world(): # this is the home page function that generates the page code
    return "Hello world!"
 
# all requests from dialogflow will go throught webhook function
@app.route('/webhook', methods=['POST'])
def webhook():
    
    req = request.get_json(silent=True, force=True) # fetch data from diagnostic info in dialogFlow

    logger.info("Incoming request: %s", req)

    intent = get_intent_from_req(req)
    logger.info('Detected intent %s', intent)



    if intent == 'Main':
        data_hat = data
        dim = get_dim_from_req(req) #This creates a data dictionary of the dimensions
        kpi = req['queryResult']['parameters']['KPI'] #This stores the KPI privided by the user
        opn = get_operation_from_req(req)


        # This is used to filter the dataset based on the input from the user
        for param, index in dim.items():
          if (is_number(index)) == True:
                index = int(index)
          if not index: # If the dimension is empty, no filter is appled
            data_mdfd = data_hat
          else :
            data_mdfd = data_hat.loc[data[param] == index]
            data_hat = data_mdfd

        if not opn: # if user does not supply operation, default to sum
            total_value = sum(data_mdfd[kpi])
        else:
            opn = eval(opn) #to convert string to actual operation
            total_value = opn(data_mdfd[kpi])

        if total_value == 0:
           response = {
                'fulfillmentText': "No such data exists. Try again"

            }
           wb = data
        else:
           total_value = '{:,.2f}'.format(total_value)
           response = {
               'fulfillmentText': "The required value is  " + str(
                   total_value) + ".You can further refine your data by adding more dimensions to it."
            }
           wb = data_mdfd #This variable is later input into pickle

        #store_params = pd.DataFrame([dim])

        with open('my_dataset.pickle', 'wb') as output: # wb stands for write bytes, rb stands for read bytes. What is the significance of output?
            pickle.dump(wb, output)

        with open('params.pickle', 'wb') as output:
            pickle.dump(dim, output)

        with open('kp.pickle', 'wb') as output:
            pickle.dump(kpi, output)

        with open('inte.pickle', 'wb') as output:
            pickle.dump(intent, output)


    elif intent == 'Add_More_Data' :

        with open('params.pickle', 'rb') as dat:  #getting stored list of params from pickle and storing them in req_params (only stores dimensions, not KPI and operation)
            req_params = pickle.load(dat)  

        kpi = req['queryResult']['outputContexts'][0]['parameters']['KPI']  #getting KPI from output context
        DIM = get_dim_from_con(req)
        opn = get_operation_from_con(req)


        with open('my_dataset.pickle', 'rb') as datas:
            data_dwnld = pickle.load(datas)
            data_hat = data_dwnld

        #used to filter the dataset based on additional user input
        for param, index in DIM.items():
          if (is_number(index)) == True:
                index = int(index)
          if not index:
               data_mdfd = data_hat
          else :
               data_mdfd = data_hat.loc[data[param] == index]
               data_hat = data_mdfd
               #req_params[param][0] = index
               req_params[param] = index # important step: this updates the old dictionary by using data from the new output context

        if not opn:
            total_value = sum(data_mdfd[kpi])
        else:
            opn = eval(opn)
            total_value = opn(data_mdfd[kpi])

        if total_value == 0:
            response = {
                # 'fulfillmentText': total_value ,
                'fulfillmentText': "This data does not exist. Try again."

            }
            wb = data_dwnld

        else:
            total_value = '{:,.2f}'.format(total_value)
            response = {
                # 'fulfillmentText': total_value ,
                'fulfillmentText': "The aggregated value is  " + str(
                    total_value) + "."

            }
            wb = data_mdfd
        #store_params = pd.DataFrame([DIM])

        with open('my_dataset.pickle', 'wb') as output:
            pickle.dump(wb, output)

        with open('params.pickle', 'wb') as output:
            pickle.dump(req_params, output)

        with open('kp.pickle', 'wb') as output:
            pickle.dump(kpi, output)

        with open('inte.pickle', 'wb') as output:
            pickle.dump(intent, output)

    elif intent == 'reset': #this intent does not reset the whole data, but just one part, ex. zone
        with open('params.pickle', 'rb') as dat:
            req_params = pickle.load(dat)
        kpi = req['queryResult']['outputContexts'][0]['parameters']['KPI']
        DIM = get_dim_from_con(req)
        opn = get_operation_from_con(req)


        data_hat = data  # important step: since this is reset intent, we revert to original dataset

        for param, index in DIM.items():
          if (is_number(index)) == True:  #converting numerical string to int data type
                index = int(index)
          if not index: #if present output context does not provide some input field, we check our previously stored req_params dict (stored using pickle)
                index = req_params[param]
                #index = req_params[param][0]
                if not index: # req_param may still have some fields empty, for input which was never provided from the start
                    data_mdfd = data_hat
                else :
                    data_mdfd = data_hat.loc[data[param] == index]
                    data_hat = data_mdfd
          else :
                data_mdfd = data_hat.loc[data[param] == index]
                data_hat = data_mdfd
                req_params[param] = index

        if not opn:
            total_value = sum(data_mdfd[kpi])
        else:
            opn = eval(opn)
            total_value = opn(data_mdfd[kpi])

        if total_value == 0:
            response = {
                # 'fulfillmentText': total_value ,
                'fulfillmentText': "This data does not exist. Try again."

            }
            wb = data

        else:
            total_value = '{:,.2f}'.format(total_value)
            response = {
                # 'fulfillmentText': total_value ,
                'fulfillmentText': "The aggregated value is  " + str(total_value) + ". I hope I could help"

            }
            wb = data_mdfd

        #store_params = pd.DataFrame([DIM])

        with open('my_dataset.pickle', 'wb') as output:
            pickle.dump(wb, output)

        with open('params.pickle', 'wb') as output:
            pickle.dump(req_params, output)

        with open('kp.pickle', 'wb') as output:
            pickle.dump(kpi, output)

        with open('inte.pickle', 'wb') as output:
            pickle.dump(intent, output)

    elif intent == 'graph':

        responseid = req['queryResult']['queryText']  #this is unique to the graph intent only
        responseid = responseid.replace(" ", "_")

        data_hat = data  
        dim = get_dim_from_req(req)
        kpi = req['queryResult']['parameters']['KPI']
        dim_hdr = get_dim_header_from_req(req)  #eg. from Branch: Jaipur, the keyword branch will be extracted
        dict = {}

        for param, index in dim.items():
            if (is_number(index)) == True:
                index = int(index)
            if not index:
                data_mdfd = data_hat
            else:
                data_mdfd = data_hat.loc[data[param] == index]
                data_hat = data_mdfd

        dict['kpi'] = kpi  #these 3 lines are not part of creating graph
        dict['dim_hdr'] = dim_hdr
        dict['intent'] = intent

        if data_mdfd.empty :
            response = {
                # 'fulfillmentText': total_value ,
                'fulfillmentText': 'There is no info available for this data.',

            }
            wb = data_hat
        else:
            response = {
                # 'fulfillmentText': total_value ,
                #'fulfillmentText': 'Click on the link provided here: https://mdntest.herokuapp.com/plots',
                #'fulfillmentMessages': [
                 #   {
                  #      'image': {
                   #         'imageUri': str('https://mdntest.herokuapp.com/plots')
                    #    },
                     #   'platform': 'FACEBOOK'
                    #}
                #]

            }
            wb = data_mdfd

        #store_params = pd.DataFrame([dim])

        with open('my_datasets.pickle', 'wb') as output:
            pickle.dump(wb, output)

        with open('str_params.pickle', 'wb') as output:
            pickle.dump(dim, output)

        with open('dict.pickle', 'wb') as output:
            pickle.dump(dict, output)

    res = create_response(response)  # jsonifies the response(fulfilment text)

    return res

def do_plot():
    with open('my_datasets.pickle', 'rb') as datas:
        data_dwnld = pickle.load(datas)

    with open('str_params.pickle', 'rb') as dat:
        req_params = pickle.load(dat)

    with open('dict.pickle', 'rb') as date:
        req_dict = pickle.load(date)

    f = plt.bar(data_dwnld[req_dict['dim_hdr']], data_dwnld[req_dict['kpi']])
   # plt.margins(.06)
    plt.title(req_dict['kpi'] +' vs ' + req_dict['dim_hdr'] )
    plt.xticks(rotation = 25)
    plt.xticks(fontsize = 6)
    plt.xlabel(req_dict['dim_hdr'])
    plt.ylabel(req_dict['kpi'])

    list_fr_lgnd = []   # creating legend for graph
    for key, value in req_params.items() :
        if not value:
            pass
        else:
            list_fr_lgnd.append(value)

    if not list_fr_lgnd :
        pass
    else :
        plt.legend([[str(item) for item in list_fr_lgnd]])


    # here is the trick save your figure into a bytes object and you can afterwards expose it via flask
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png', orientation='landscape', align= 'center')
    bytes_image.seek(0)

    plt.clf() #this is important to refresh the page every time
    return bytes_image

#with open('string.pickle', 'rb') as dater:
    #responseid = pickle.load(dater)

@app.route('/plots', methods=['GET']) #whenever we do @app.route, the function below the @app.route runs automatically upon calling the app
def correlation_matrix(): #change the name of this function to image_to_web
    #variable = responseid
    bytes_obj = do_plot()

    return send_file(bytes_obj,   #this is all Flask stuff
                     attachment_filename='plot.png',
                     mimetype='image/png')

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def get_intent_from_req(req):
    """ Get intent name from dialogflow request"""
    try:
        intent_name = req['queryResult']['intent']['displayName']
    except KeyError:
        return None

    return intent_name

def get_operation_from_req(req):
    """ Get operation name from dialogflow request. This uses parameters to get data"""
    try:
        operation = req['queryResult']['parameters']['operation']
    except KeyError:
        return None

    return operation

def get_operation_from_con(req):
    """ Get operation name from dialogflow request. This uses output contexts to get data"""
    try:
        operation = req['queryResult']['outputContexts'][0]['parameters']['operation']
    except KeyError:
        return None

    return operation

def get_dim_header_from_req(req):
    """ This func takes dimension headers from the dimension entity. This is used in the graph intent"""
    try:
        dim_hdr = req['queryResult']['parameters']['Dimensions']
    except KeyError:
        return None

    return dim_hdr

def get_dim_from_req(req):
    """ This func takes dimension from parameters (found under diagnostic info tab)"""
    i = 0
    dim_from_param = {}
    for dim in sheet2.Dimensions:
        value = req['queryResult']['parameters'][sheet2.Dimensions[i]]
        dim_from_param[sheet2.Dimensions[i]] = value
        i = i + 1

    return dim_from_param

def get_dim_from_con(req):
    i = 0
    dim_from_param = {}
    for dim in sheet2.Dimensions:
        value = req['queryResult']['outputContexts'][0]['parameters'][sheet2.Dimensions[i]]
        dim_from_param[sheet2.Dimensions[i]] = value
        i = i + 1

    return dim_from_param

def create_response(response):
    """ Creates a JSON with provided response parameters """

    # convert dictionary with our response to a JSON string
    res = json.dumps(response, indent=4) #indent = 4 don't know, jsonify

    logger.info(res) #logger displays response

    r = make_response(res) #here r is a flask make_response object
    r.headers['Content-Type'] = 'application/json' 

    return r

@app.route('/', methods=['POST'])
def main():
    return render_template('ajax.html')  #connect the html code with python through flask

@app.route('/htmlcode', methods=['POST'])
def htm():

    empty = {}
    #link = 'http://127.0.0.1:5000/' + responseid

    with open('inte.pickle', 'rb') as diti:
        intent = pickle.load(diti)

    with open('params.pickle', 'rb') as dit:
        html_dim = pickle.load(dit)

    for param, index in html_dim.items():
        if param == 'Financial_Year':
            index = str(index) #converting year back to string

    with open('kp.pickle', 'rb') as out:
        kpi = pickle.load(out)

    html_dim['KPI'] = kpi #adding KPI to the dimensions dictionsry
    #html_dim['Link'] = link

    if not intent:
        return jsonify(empty)
    else:
        return jsonify(html_dim)


if __name__ == '__main__':
    app.run(debug=False, threaded=True)
