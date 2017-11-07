from __future__ import print_function
import json
import os, sys, json, requests
from flask import Flask, request, make_response
from flask import jsonify
from flask.ext.pymongo import PyMongo
from pymessenger import Bot
from datetime import datetime as dt
from PIL import Image
from bson.objectid import ObjectId
import boto3
from botocore.client import Config
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import uuid
from main_requestcontroller import MainRequestController

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

app = Flask(__name__)


ACCESS_KEY_ID = ''
ACCESS_SECRET_KEY = ''
BUCKET_NAME = 'tonibot-bucket'

# Client Access Token for accessing our API AI Bot TODO: CHANGE THIS
CLIENT_ACCESS_TOKEN = '668999a33db140fa8fe2a7abcc79c77b'

# This seems waste
PAGE_ACCESS_TOKEN = "EAABlZAhiLCzsBAEPENnZC43ODWjX1X4VT43TBjHP8dx8WC7W6kqVRLiRz5AljcmkxSk1rfD2ZA4dDdE149D8JIurZBM67Afl6MRFyZBmqH55mTbJTSbHAjKlHSQrHGITB129ekYkdLqGb2ZBJnN7vyEH4HjgPiXzZAO0yW9wj3WXwZDZD"

# An endpoint to ApiAi, an object used for making requests to a particular agent.
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)


bot = Bot(PAGE_ACCESS_TOKEN)

app.config['MONGO_DBNAME'] = 'phillips-sales-data'
app.config['MONGO_URI'] = 'mongodb://admin:admin@ds123124.mlab.com:23124/phillips-sales-data'
app.config['ASSIST_ACTIONS_ON_GOOGLE'] = True

mongo = PyMongo(app)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

'''
@app.route('/')
def index():
    return 'Hello world!'
'''

@app.route('/', methods=['GET'])
def verify():
    print ("Hellow world")
	# Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world I am Charles", 200



# Handling HTTP POST when APIAI sends us a payload of messages that have
# have been sent to our bot. 
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print("Request:")
    print(json.dumps(data, indent=4))
    
    mainRequestControllerObj = MainRequestController(data, mongo)
    #res = processRequest(data)
    res = mainRequestControllerObj.processRequest()


    res = json.dumps(res, indent=4, cls=JSONEncoder)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print("Before final return")
    return r


def closeApplication(req):
    print("closing application")

    return createCardResponse(["It was a pleasure serving you!"], [], 
        "Dr. Digital", "Hope to see you again soon!", "", 
        "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/blue-bot.png", "Default accessibility text", [], [], False, None)

def showDetailedBio(req):
    print("wow")
    print("before the argument parameter")
    firstInput = req["originalRequest"]["data"]["inputs"][0]
    if 'arguments' in firstInput:
        optionVal = firstInput["arguments"][0]["textValue"]
        print(optionVal)
        
        baseUrl = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/"
        tempData = mongo.db.temp1
        try: 
            for s in tempData.find({'_id': ObjectId(optionVal)}):
                fullName = s['name']
                print ("The name is:" + s['name'])
                designation = s['designation']
                bio = s['bio']
                photoUrl = baseUrl + s['photo']
                profilePhoto = photoUrl

        except Exception:
            print("Could not query database")
            return makeWebhookResult('This name does not exist in the list! Say show digital employees to show all employees or say Bye doctor digital to exit')


        return createCardResponse(["The detailed bio of " + fullName, "Click on any one of the suggestions below or say Bye doctor digital to exit!"], ["Show digital employees", "Bye doctor digital"], 
            fullName, bio, designation, 
            profilePhoto, "Default accessibility text", [], [], True, None)
    else:
        print("In the else part of detailed bio")
        return makeWebhookResult('This name does not exist in the list! Say show digital employees to show all employees or say Bye doctor digital to exit')

@app.route('/add')

def add():
    
    sale = mongo.db.sales
    sale.insert({'city' : 'Mumbai', 'date': 'June', 'amount' : '1900'})
    return 'Added Sales row'

@app.route('/query')
def query():
    sale = mongo.db.sales
    output = []
    for s in sale.find({'city': 'Pune'}):
        output.append({'city' : s['city'], 'date' : s['date'], 'amount': s['amount']})
    return jsonify({'output':output})

if __name__ == "__main__":
    app.run()
    '''app.run(debug = True, port = 80)'''
    
'''
End of file!!!!
'''
