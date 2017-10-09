from __future__ import print_function
import json
import os, sys, json, requests
from flask import Flask, request, make_response, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, validators
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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
from custom_email import Email

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['APP_SECRET']
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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

class User():

    def __init__(self, username):
        self.username = username
        self.email = None

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

@login_manager.user_loader
def load_user(username):
    u = mongo.db.users.find_one({"username": username})
    #u = mongo.db.users.find_one({"_id": ObjectId(username)})
    #u = mongo.db.users.find_one({"_id": username['_id']})
    if not u:
        return None
    #return User(u['_id'])
    return User(u['username'])

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    #email = StringField('email', validators=[InputRequired(), Length(max=50)])
    email = StringField('email', validators=[InputRequired(), validators.Email(message = 'Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
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


@app.route('/temp', methods=['GET'])
@login_required
def verifyTemp():
    print ("Hellow world")
    return "Hello world this is the login protected page", 200



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        users = mongo.db.users
        loginUser = users.find_one({'username' : form.username.data})
        if loginUser:
            if check_password_hash(loginUser['password'], form.password.data):
                #session['username'] = form.username.data
                #user_obj = loginUser['_id']
                user_obj = User(loginUser['username'])
                #user_obj = login_user['username']
                login_user(user_obj)
                return redirect(url_for('verifyTemp'))

        return 'Invalid username/password combination'
        '''
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        '''
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'You are now logged out'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        users = mongo.db.users
        existing_user = users.find_one({'username' : form.username.data})
        if existing_user is None:
            #hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            users.insert({'username' : form.username.data, 'password' : hashed_password})
            user_obj = User(form.username.data)
            login_user(user_obj)
            #return '<h1>New user has been created!</h1>'
            return redirect(url_for('verifyTemp'))
        
        return 'That username already exists!'
        '''
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        '''
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)




# Handling HTTP POST when APIAI sends us a payload of messages that have
# have been sent to our bot. 
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print("Request:")
    print(json.dumps(data, indent=4))
    res = processRequest(data)

    res = json.dumps(res, indent=4, cls=JSONEncoder)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print("Before final return")
    return r

    


def processRequest(req):
    print('hi')
    if req.get("result").get("action") == "sales.statistics":
        parsedData = parseUserParametersGetSalesAmount(req.get("result").get('parameters'))
        res = makeContextWebhookResult(parsedData["speech"], createDetailedSalesAndChartOutputContext(parsedData["context"], parsedData["draw-chart-context"]))
    elif req.get("result").get("action") == "detailed.statistics":
        parsedData = parseContextUserParametersGetSalesAmount(req.get("result"))
        res = makeContextWebhookResult(parsedData["speech"], createDetailedSalesAndChartOutputContext(parsedData["context"], parsedData["draw-chart-context"]))
    elif req.get("result").get("action") == "product.chart":
        res = generateProductChartController(req.get("result").get('parameters'))
        #res = generateProductChartController(req.get("result"))
        #parsedData = generateProductChartController(req.get("result").get('parameters'))
        #res = makeContextWebhookResult(parsedData["speech"], parsedData["context"])
        '''
        res = createCardResponse([parsedData["speech"]], ["Show digital employees", "Bye doctor dashboard"],
            "Dr. Dashboard", "Phillips bot a.k.a. Dr. Dashboard is designed for voice enabled financial reporting", "", 
            parsedData["awsImageFileName"], "Default accessibility text", [], [], True, parsedData["context"])
        '''
    elif req.get("result").get("action") == "detailed.chart":
        res = parseContextGenerateProductChartController(req.get("result"))
    elif req.get("result").get("action") == "convert.chart":
        res = convertTextToProductChartController(req.get("result"))
    elif req.get("result").get("action") == "send.customEmail":
        res = generateEmailController(req.get("result"))
    elif req.get("result").get("action") == "welcome.intent":
        res = showWelcomeIntent(req)
    elif req.get("result").get("action") == "showAllUsers":
        res = makeListOfAllUsers(req)
    elif req.get("result").get("action") == "detailed.bio":
        res = showDetailedBio(req)
    elif req.get("result").get("action") == "application.close":
        res = closeApplication(req)    
    elif req.get("result").get("action") == "time.timeperiod":
        ''' TODO REMOVE temp
        myCustomResult = getDummyParameters(req)
        res = makeWebhookResult(myCustomResult)
        '''
        return {}
    else:
        return {}
    return res
'''
This is a very temp function. It is used to just create a sample response in JSON format
'''
def makeWebhookResult(data):
    speech = data
    '''
    print("Response:")
    print(speech)
    '''
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "phillips-bot"
    }

'''
This is a very temp function. It is used to just create a sample response in JSON format
'''
def makeContextWebhookResult(speech, context):
    
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": context,
        "source": "phillips-bot"
    }
    
def itemSelected(app):
    # Get the user's selection
    param = app.getContextArgument('actions_intent_option','OPTION').value
    print ("There is no chance it comes here")

def showWelcomeIntent(resp):
    print ("Inside show welcome intent")

    #getSalesAmount(parseDateRange("2017-08-31/2017-09-01"),parseRegion("North East"),getDefaultProduct())


    '''
    Inserting a chart
    '''
    '''
    objects = ('DD', 'Ind', 'LO', 'GE', 'UK')

    incomes = [1000, 2300, 3000, 111, 1456]

    y_pos = np.arange(len(objects))

    plt.bar(y_pos, incomes, align='center')
    plt.xticks(y_pos, objects)
    plt.ylabel('Income')
    plt.xlabel('Country')
    plt.title('Average income by country')

    #fig = plt.figure()
    #print(fig)

    #data = open('incomes_country.png', 'rb')
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)

    
    s3 = boto3.resource(
        's3',
        aws_access_key_id=os.environ['S3_KEY'],
        aws_secret_access_key=os.environ['S3_SECRET'],
        config=Config(signature_version='s3v4')
        )
    


    s3.Bucket(BUCKET_NAME).put_object(Key='incomes7.png', Body=img_data, ContentType='image/png')

    print("Done")
    '''

    
    '''
    prodData = mongo.db.products
    #salesData = mongo.db.sales
    salesData = mongo.db.sales1
    try:
    '''
    '''
        pIdCur = prodData.find({
            "pName":"Fan"
            },{
            "pId": 1
            })

        for s in pIdCur:
            pId = s["pId"]

        print("pId")
        print(pId)
    '''
    '''
        Q1 First query Sales for Fan on September 1, 2017 for Chicago
    '''    
    '''
        salesAmountCur = salesData.find({
            "date":"2017-09-01",
            "city":"Chicago",
            "pId":pId
            }, {
            "salesRev": 1
            })

        for s in salesAmountCur:
            salesAmount = s["salesRev"]

        print("saless revenue")
        print(salesAmount)
    '''
    '''
        Q2 Second query Sales for Fan on Q3 (1/7/2017 - 30/9/2017) for Chicago
    ''' 
    '''
        salesAmountCur = salesData.find({
            "date": {'$gt': datetime(2017,7,1), '$lt': datetime(2017,9,30)},
            "city":"Chicago",
            "pId":"P3"
            }, {
            "salesRev": 1
            })

        for s in salesAmountCur:
            salesAmount = s["salesRev"]

        print("saless revenue")
        print(salesAmount)
    '''

       
    '''
    except Exception:
        print("Could not query database")
    '''

    '''
    Sending an email trial
    '''
    '''
    myAttachment = {}
    myAttachment["attachmentName"] = "1A0119.png"
    #myAttachment["attachmentPath"] = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/1A0119.png"
    myEmail = Email("charlesdavid2711@gmail.com", "abchaturvedi@deloitte.com","Product wise sales report","As requested please find attached the product wise sales report",myAttachment)
    myEmail.sendEmail()
    '''

    return createCardResponse(["Hi, I am Dr. Dashboard - a sales tracker. The suggestions below are some of the things I can do! At any time if you want to leave the application say Bye Dr. Dashboard! What can I do for you?"], 
        ["Show digital employees", "Bye doctor dashboard"], 
        "Dr. Dashboard", "Phillips bot a.k.a. Dr. Dashboard is designed for voice enabled financial reporting", "", 
        "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/incomes7.png", "Default accessibility text", [], [], True, None)


'''
Draws the product chart basis the parameters passed
'''
def drawProductChart(productRevenues, chartType, xLabel, yLabel, title):
    print(" In draw product chart")
    print("THe chart type passed is:"+ chartType)
    xArr = []
    yArr = []
    for index in range(0, len(productRevenues)):
        prodRev = productRevenues[index]
        xArr.append(prodRev["product"])
        print ("the product is:" + prodRev["product"])
        yArr.append(prodRev["salesRevenue"])
        print ("the product revenue is:" + str(prodRev["salesRevenue"]))


    print ("xArr in create draw Product Chart is:")
    for i in range(0, len(xArr)):
        print ("the product is:" + xArr[i])


    if chartType == getStrBarChart():
        return createBarChart(tuple(xArr), yArr, xLabel, yLabel, title)
    elif chartType == getStrPieChart():
        return createPieChart(tuple(xArr), yArr, title)
    else:
        print ("there is an error in selecting the correct chart in drawProductChart")
        return createBarChart(tuple(xArr), yArr, xLabel, yLabel, title)

'''
Creates a bar chart with the passed values
'''
def createBarChart(xArr, yArr, xLabel, yLabel, title):

    print ("xArr in create Bar Chart is:")
    for i in range(0, len(xArr)):
        print ("the product is:" + xArr[i])
        print ("the product revenue is:" + str(yArr[i]))

    y_pos = np.arange(len(xArr))
    plt.gcf().clear()
    plt.bar(y_pos, yArr, align='center')
    plt.xticks(y_pos, xArr)
    plt.ylabel(yLabel)
    plt.xlabel(xLabel)
    plt.title(title)

    #fig = plt.figure()
    #print(fig)

    #data = open('incomes_country.png', 'rb')
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    return img_data


def createPieChart(xArr, yArr, title):
    #labels = 'Python', 'C++', 'Ruby', 'Java'
    #sizes = [215, 130, 245, 210]
    #colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    colors = getColorsForPieChart(len(yArr))
    #explode = (0.1, 0, 0, 0)  # explode 1st slice
    explode = getExplodeForPieChart(len(yArr))

    # Plot
    plt.gcf().clear()
    plt.pie(yArr, explode=explode, labels=xArr, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
     
    plt.axis('equal')
    plt.title(title)

    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    return img_data

'''
Returns an array of colors of specified length
'''
def getColorsForPieChart(length):
    return getColorsList()[:length]

'''
Returns an entire list of colors
'''
def getColorsList():
    return ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'gray', 'pink', 'purple', 'red']

'''
Returns a tuple of explode parameters of specified length
'''
def getExplodeForPieChart(length):
    return getExplodeTuple()[:length]
'''
Returns an entire list of explode tuple
'''
def getExplodeTuple():
    return (0.1, 0, 0, 0, 0, 0, 0, 0)
'''
Saves a resource to aws
'''
def saveResourceToAWS(img_data, img_name, content_type):
    print("saving resource to aws")  
    s3 = boto3.resource(
        's3',
        aws_access_key_id=os.environ['S3_KEY'],
        aws_secret_access_key=os.environ['S3_SECRET'],
        config=Config(signature_version='s3v4')
        )
    


    s3.Bucket(BUCKET_NAME).put_object(Key=img_name, Body=img_data, ContentType=content_type)

    print("Done")



'''
This function is a controller function and gateway for context which parses the context parameters and returns the sales amount
'''
def parseContextUserParametersGetSalesAmount(result):
    userParameters = result.get('parameters')
    userContext = result.get('contexts')

    # This context is an array. Parse this array until you get the required context
    detailedSalesContext = getAppropriateUserContext(userContext, "detailed_sales")

    # If the context is not set
    if detailedSalesContext == "Context was not found":
        return detailedSalesContext

    detailedSalesParameters = detailedSalesContext.get('parameters')

    cities = parseContextUserRegion(userParameters, detailedSalesParameters)
    product = parseContextUserProduct(userParameters, detailedSalesParameters)
    period = parseContextUserPeriod(userParameters.get('period'), detailedSalesParameters.get('context-period'))

    salesRev = getSalesAmount(period, cities["cities"], product["product"])

    return {
            "speech":generateContextResponseForSales(userParameters, detailedSalesParameters, period, salesRev),
            "context": createContextObject(cities["context-geo-city-us"], cities["context-geo-state-us"], cities["context-region"], product["context-product"], period["context-period"]),
            "draw-chart-context": createChartContextObject(cities["context-geo-city-us"], cities["context-geo-state-us"], cities["context-region"], product["context-product"], period["context-period"],"","")
            }

'''
This function returns the appropriate context
'''
def getAppropriateUserContext(userContext, contextName):
    for index in range(0, len(userContext)):
        if userContext[index]["name"] == contextName:
            print("found the right context")
            return userContext[index]

    # Could not find the right context
    return "Context was not found"

'''
Creates a list of the passed context objects
TODO:: Ideally should be a separate class with an add method
'''
def createOutputContextList(contextObjectList):
    print("inside createOutputContextList")
    contextList = []
    for index in range(0, 1):
        print("index is:"+str(index))
        contextList.append(contextObjectList)

    return contextList

'''
Creates and returns an output context object that can be returned as json in the response
'''
def createOutputContext(name, lifespan, contextObject):
    print("Inside create output context")
    print("The name of the passed context is:::"+name)
    outputContextObj ={}
    outputContextObj["name"] = name
    outputContextObj["lifespan"] = lifespan
    outputContextObj["parameters"] = contextObject

    return outputContextObj


def createDetailedSalesAndChartOutputContext(contextObject, chartContextObject):
    contextList = []
    contextList.append(createDetailedSalesOutputContext(contextObject))
    contextList.append(createDrawChartOutputContext(chartContextObject))
    return contextList
'''
Creates and returns the detailed sales output context
'''
def createDetailedSalesOutputContext(contextObject):
    #return createOutputContextList(createOutputContext("detailed_sales", 5, contextObject))
    return createOutputContext("detailed_sales", 1, contextObject)

def createDrawChartOutputContext(contextObject):
    return createOutputContext("draw_chart", 1, contextObject)


def createDetailedChartOutputContext(contextObject):
    #return createOutputContextList(createOutputContext("detailed_sales", 5, contextObject))
    return createOutputContext("detailed_chart", 1, contextObject)
'''
Creates an output context for emails
'''
def createEmailOutputContext(contextObject):
    #return createOutputContextList(createOutputContext("send_chart_email", 5, contextObject))
    #return [createOutputContext("chart_email", 3, contextObject)]
    return createOutputContext("chart_email", 5, contextObject)

'''
Creates and returns a context Object for emails which can be sent to api.ai as context parameters
'''
def createEmailContextObject(attachmentName):
    contextObj = {}
    contextObj["context-attachment-name"] = attachmentName
    return contextObj
'''
Creates and returns a context Object which can be sent to api.ai as context parameters
'''
def createContextObject(city, state, region, product, period):
    contextObj = {}
    contextObj["context-geo-city-us"] = city
    contextObj["context-geo-state-us"] = state
    contextObj["context-region"] = region
    contextObj["context-product"] = product
    contextObj["context-period"] = period
    return contextObj

'''
Creates and returns a context Object which can be sent to api.ai as context parameters for charting
'''
def createChartContextObject(city, state, region, product, period, chartType, mainChartFeature):
    contextObj = {}
    contextObj["context-geo-city-us"] = city
    contextObj["context-geo-state-us"] = state
    contextObj["context-region"] = region
    contextObj["context-product"] = product
    contextObj["context-period"] = period
    contextObj["context-chart-type"] = chartType
    contextObj["context-main-chart-feature"] = mainChartFeature
    return contextObj


'''
This is a controller function for sending an email to the specified user.
'''
def generateEmailController(result):
    userParameters = result.get('parameters')
    userContext = result.get('contexts')

    # This context is an array. Parse this array until you get the required context
    emailContext = getAppropriateUserContext(userContext, "chart_email")

    # If the context is not set
    if emailContext == "Context was not found":
        return emailContext

    emailAttachmentParameters = emailContext.get('parameters')

    emailParameters = parseContextEmail(userParameters, emailAttachmentParameters)
    print ("After email Parameters")
    print ("the attachment name is:"+ emailParameters['attachment-name'])
    print ("Email to be sent to:"+ emailParameters['email-to'])
    '''
    Sending an email trial
    '''
    myAttachment = {}
    myAttachment["attachmentName"] = emailParameters['attachment-name']
    #myAttachment["attachmentPath"] = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/1A0119.png"
    myEmail = Email("charlesdavid2711@gmail.com", emailParameters['email-to'], "Product wise sales report","As requested please find attached the product wise sales report",myAttachment)
    myEmail.sendEmail()

    return createCardResponse(["Email sent successfully! What else can I do for you?"], 
        ["Show digital employees", "Bye doctor dashboard"], 
        "Dr. Dashboard", "Phillips bot a.k.a. Dr. Dashboard is designed for voice enabled financial reporting", "", 
        "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/blue-bot.png", "Default accessibility text", [], [], True, None)


'''
This function is a controller function for generating a product wise chart after parsing the user parameters
'''
def convertTextToProductChartController(result):
    img_data = None
    userParameters = result.get('parameters')
    userContext = result.get('contexts')

    # This context is an array. Parse this array until you get the required context
    drawChartContext = getAppropriateUserContext(userContext, "draw_chart")

    # If the context is not set
    if drawChartContext == "Context was not found":
        return drawChartContext
    
    drawChartParameters = drawChartContext.get('parameters')
    cities = parseContextUserRegion(userParameters, drawChartParameters)
    products = parseContextUserProducts(userParameters, drawChartParameters)
    period = parseContextUserPeriod(userParameters.get('period'), drawChartParameters.get('context-period'))
    chartType = parseContextUserChartType(userParameters, drawChartParameters)
    mainChartFeature = parseContextUserMainChartFeature(userParameters, drawChartParameters)
    


    img_data = drawMainChartFeatureChart(cities, products, period, chartType, mainChartFeature)

    imageFileName = uuid.uuid4().hex[:6].upper()
    #imageFileName = 'product'
    imageFileName += '.png'
    print ("The image file name is:"+ imageFileName)
    awsImageFileName = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/" + imageFileName

    saveResourceToAWS(img_data, imageFileName, 'image/png')

    # Creating Context

    # Creating email context
    outputContext = []
    outputContext.append(createEmailOutputContext(createEmailContextObject(imageFileName)))
    outputContext.append(createDetailedChartOutputContext(createChartContextObject(cities["context-geo-city-us"], 
        cities["context-geo-state-us"], cities["context-region"], products["context-product"], period["context-period"], chartType["context-chart-type"], mainChartFeature["context-main-chart-feature"])))

    # Call a function that creates the card response
    
    return createCardResponse(["Here is the product wise chart requested"], 
        ["Show digital employees", "Bye doctor dashboard"], 
        "Dr. Dashboard", "Phillips bot a.k.a. Dr. Dashboard is designed for voice enabled financial reporting", "", 
        awsImageFileName, "Default accessibility text", [], [], True, outputContext)
'''
This function is a controller function for generating a product wise chart after parsing the user parameters
'''
def generateProductChartController(userParameters):
    img_data = None
   
    cities = parseUserRegion(userParameters)
    products = parseUserProducts(userParameters)
    period = parseUserPeriod(userParameters.get('period'))
    chartType = parseUserChartType(userParameters)
    mainChartFeature = parseUserMainChartFeature(userParameters)

    img_data = drawMainChartFeatureChart(cities, products, period, chartType, mainChartFeature)

    imageFileName = uuid.uuid4().hex[:6].upper()
    #imageFileName = 'product'
    imageFileName += '.png'
    print ("The image file name is:"+ imageFileName)
    awsImageFileName = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/" + imageFileName

    saveResourceToAWS(img_data, imageFileName, 'image/png')

    # Creating Context

    # Creating email context
    outputContext = []
    outputContext.append(createEmailOutputContext(createEmailContextObject(imageFileName)))
    outputContext.append(createDetailedChartOutputContext(createChartContextObject(cities["context-geo-city-us"], 
        cities["context-geo-state-us"], cities["context-region"], products["context-product"], period["context-period"], chartType["context-chart-type"], mainChartFeature["context-main-chart-feature"])))


    # Call a function that creates the card response
    
    return createCardResponse(["Here is the product wise chart requested"], 
        ["Show digital employees", "Bye doctor dashboard"], 
        "Dr. Dashboard", "Phillips bot a.k.a. Dr. Dashboard is designed for voice enabled financial reporting", "", 
        awsImageFileName, "Default accessibility text", [], [], True, outputContext)
    



'''
This function is a controller function and gateway for context which parses the context parameters and returns the chart
'''
def parseContextGenerateProductChartController(result):
    userParameters = result.get('parameters')
    userContext = result.get('contexts')

    # This context is an array. Parse this array until you get the required context
    detailedChartContext = getAppropriateUserContext(userContext, "detailed_chart")

    # If the context is not set
    if detailedChartContext == "Context was not found":
        return detailedChartContext

    detailedChartParameters = detailedChartContext.get('parameters')

    img_data = None
    cities = parseContextUserRegion(userParameters, detailedChartParameters)
    products = parseContextUserProducts(userParameters, detailedChartParameters)
    period = parseContextUserPeriod(userParameters.get('period'), detailedChartParameters.get('context-period'))
    chartType = parseContextUserChartType(userParameters, detailedChartParameters)
    mainChartFeature = parseContextUserMainChartFeature(userParameters, detailedChartParameters)

    img_data = drawMainChartFeatureChart(cities, products, period, chartType, mainChartFeature)

    imageFileName = uuid.uuid4().hex[:6].upper()
    #imageFileName = 'product'
    imageFileName += '.png'
    print ("The image file name is:"+ imageFileName)
    awsImageFileName = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/" + imageFileName

    saveResourceToAWS(img_data, imageFileName, 'image/png')

    # Creating Context

    # Creating email context
    outputContext = []
    outputContext.append(createEmailOutputContext(createEmailContextObject(imageFileName)))
    outputContext.append(createDetailedChartOutputContext(createChartContextObject(cities["context-geo-city-us"], 
        cities["context-geo-state-us"], cities["context-region"], products["context-product"], period["context-period"], chartType["context-chart-type"], mainChartFeature["context-main-chart-feature"])))

   
    
    return createCardResponse(["Here is the product wise chart requested"], 
        ["Show digital employees", "Bye doctor dashboard"], 
        "Dr. Dashboard", "Phillips bot a.k.a. Dr. Dashboard is designed for voice enabled financial reporting", "", 
        awsImageFileName, "Default accessibility text", [], [], True, outputContext)



'''
This function parses the main chart feature and draws the appropriate chart
'''
def drawMainChartFeatureChart(cities, products, period, chartType, mainChartFeature):

    mChartFeature = mainChartFeature["main-chart-feature"]

    if mChartFeature == getStrProduct():
        print ("Correct if in draw Main chart feature")
        # Call a function that returns the product wise revenues
        productRevenues = getProductWiseRevenue(period, cities["cities"], products["product"])

        if productRevenues == []:
            print ("There is a problem no product revenues were generated")
            return ""
        # Call a function that generates the chart
        return drawProductChart(productRevenues, chartType["chart-type"], "Products", "Revenues", "Product wise Revenues")
    elif mChartFeature == getStrCity():
        print("This should return city wise revenues")
    elif mChartFeature == getStrState():
        print("This should return state wise revenues")
    elif mChartFeature == getStrRegion():
        print("This should return region wise revenues")
    else:
        print("Default returns product wise revenues")
        # Call a function that returns the product wise revenues
        productRevenues = getProductWiseRevenue(period, cities["cities"], products["product"])

        if productRevenues == []:
            print ("There is a problem no product revenues were generated")
            return ""
        # Call a function that generates the chart
        return drawProductChart(productRevenues, chartType["chart-type"], "Products", "Revenues", "Product wise Revenues")


'''
This function is a controller function which parses the parameters and then returns the sales amount
'''
def parseUserParametersGetSalesAmount(userParameters):

    cities = parseUserRegion(userParameters)
    product = parseUserProduct(userParameters)
    period = parseUserPeriod(userParameters.get('period'))

    salesRev = getSalesAmount(period, cities["cities"], product["product"])

    return {
            "speech": generateResponseForSales(userParameters, period, salesRev), 
            "context": createContextObject(cities["context-geo-city-us"], cities["context-geo-state-us"], cities["context-region"], product["context-product"], period["context-period"]),
            "draw-chart-context": createChartContextObject(cities["context-geo-city-us"], cities["context-geo-state-us"], cities["context-region"], product["context-product"], period["context-period"],"","")
            }


'''
This function returns product wise revenues (List of objects : product, salesRevenue) for the specified productId, cities, period
TODO: Change query into an aggregation function of mongo db in order to expedite the process & lift load from python
'''
def getProductWiseRevenue(period, cities, productIds):
    print ("In get product wise revenue")
    print ("The start date is:" + str(period["startDate"]))
    print ("The end date is:" + str(period["endDate"]))
    print ("the first city is:" + cities[0])
    print ("The first product id is:" + productIds[0])


    productRevenues = []
    salesRev = 0
    salesData = mongo.db.sales1
    startDate = period["startDate"]
    endDate = period["endDate"]
    '''
    If it is a single date else it is a range
    '''
    if endDate == "":
        for id in range(0, len(productIds)):
            prodRev = {}
            salesRev = 0

            try: 
                for s in salesData.find({'pId': productIds[id], 'city': {'$in':cities},'date': startDate}):
                    print("The sales revenue is:"+s['salesRev'])
                    salesRev = salesRev + int(s['salesRev'])
                
                print("The cumulative sales revenue for this product is:" + str(salesRev))
                
                prodRev['product'] = getPNameFromPId(productIds[id])
                prodRev['salesRevenue'] = salesRev
                productRevenues.append(prodRev)
            
            except Exception:
                print("Could not query database")
                return []

        return productRevenues
    else:
        for id in range(0, len(productIds)):
            prodRev = {}
            salesRev = 0

            try:
                for s in salesData.find({'pId': productIds[id], 'city': {'$in':cities}}):
                    print ("The date is:" + s['date'])
                    if (dt.strptime(s['date'], "%Y-%m-%d") >= dt.strptime(startDate, "%Y-%m-%d")) and (dt.strptime(s['date'], "%Y-%m-%d") <= dt.strptime(endDate, "%Y-%m-%d")):
                        print ("Inside if")
                        print("The sales revenue is:"+s['salesRev'])
                        salesRev = salesRev + int(s['salesRev'])
            
                print("The cumulative sales revenue for date range for this product is:" + str(salesRev))

                prodRev['product'] = getPNameFromPId(productIds[id])
                prodRev['salesRevenue'] = salesRev
                productRevenues.append(prodRev)

            except Exception:
                print("Could not query database")
                return []


        return productRevenues
'''
This function returns the sales for the specified productId, cities, period
TODO: Change query into an aggregation function of mongo db in order to expedite the process & lift load from python
'''
def getSalesAmount(period, cities, productId):
    print ("In get sales amount")
    print ("The start date is:" + str(period["startDate"]))
    print ("The end date is:" + str(period["endDate"]))
    print ("the first city is:" + cities[0])
    print ("The product id is:" + productId)

    salesRev = 0
    salesData = mongo.db.sales1
    startDate = period["startDate"]
    endDate = period["endDate"]
    '''
    If it is a single date else it is a range
    '''
    if endDate == "":
        try: 
            for s in salesData.find({'pId': productId, 'city': {'$in':cities},'date': startDate}):
                print("The sales revenue is:"+s['salesRev'])
                salesRev = salesRev + int(s['salesRev'])
            
            print("The cumulative sales revenue for date is:" + str(salesRev))
            #return "The cumulative sales revenue is:" + str(salesRev)
            return salesRev
            
        except Exception:
            print("Could not query database")
            return ''
    else:
        try: 
            for s in salesData.find({'pId': productId, 'city': {'$in':cities}}):
                print ("The date is:" + s['date'])
                if (dt.strptime(s['date'], "%Y-%m-%d") >= dt.strptime(startDate, "%Y-%m-%d")) and (dt.strptime(s['date'], "%Y-%m-%d") <= dt.strptime(endDate, "%Y-%m-%d")):
                    print ("Inside if")
                    print("The sales revenue is:"+s['salesRev'])
                    salesRev = salesRev + int(s['salesRev'])
            
            print("The cumulative sales revenue for date range is:" + str(salesRev))
            #return "The cumulative sales revenue is:" + str(salesRev)
            return salesRev

        except Exception:
            print("Could not query database")
            return ''



def generateContextResponseForSales(userParameters, contextParameters, period, salesRev):

    if salesRev == "":
        return "There was an error while querying the data and it returned null sales revenue"

    resStr = "The sales revenue of "
    
    #Here there should be product
    resStr += generateContextResponseForProduct(userParameters, contextParameters)

    #Here there should be region
    resStr += " for " + generateContextResponseForRegion(userParameters, contextParameters)

    #Here there should be date/period
    resStr += " " + generateContextResponseForPeriod(userParameters, contextParameters, period)

    #Adding the amount
    resStr += " is: " + str(salesRev)

    return resStr

'''
Returns a string which will be sent as response to the user when he/she queries for sales data

'''
def generateResponseForSales(userParameters, period, salesRev):
    
    if salesRev == "":
        return "There was an error while querying the data and it returned null sales revenue"

    resStr = "The sales revenue of "
    
    #Here there should be product
    resStr += generateResponseForProduct(userParameters)


    #Here there should be region
    resStr += " for " + generateResponseForRegion(userParameters)

    #Here there should be date/period
    resStr += " " + generateResponseForPeriod(userParameters, period)

    #Adding the amount
    resStr += " is: " + str(salesRev)

    return resStr


'''
Returns either the requested product name or the default product name
'''
def generateContextResponseForProduct(parameters, contextParameters):
    resStr = ""

    if parameters.get('product') != None and parameters.get('product') != "":
        resStr += parameters.get('product')
    elif contextParameters.get('context-product') != None and contextParameters.get('context-product') != "":
        resStr += contextParameters.get('context-product')
    else:
        resStr += getStrDefaultProduct()

    return resStr

'''
Returns either the requested product name or the default product name
'''
def generateResponseForProduct(parameters):
    resStr = ""

    if parameters.get('product') != None and parameters.get('product') != "":
        resStr += parameters.get('product')
    else:
        resStr += getStrDefaultProduct()

    return resStr


'''
Should return either the city or the state or the region or the default that the user has requested
'''
def generateContextResponseForRegion(parameters, contextParameters):
    resStr = ""

    if parameters.get('geo-city-us') != None and parameters.get('geo-city-us') != "" and parameters.get('geo-city-us') != []:
        resStr = parameters.get('geo-city-us')
    elif parameters.get('geo-city') != None and parameters.get('geo-city') != "" and parameters.get('geo-city') != []:
        resStr = parameters.get('geo-city')
    elif parameters.get('geo-state-us') != None and parameters.get('geo-state-us') != "" and parameters.get('geo-state-us') != []:
        resStr = parameters.get('geo-state-us')
    elif parameters.get('region') != None and parameters.get('region') != "":
        resStr = parameters.get('region')
    elif contextParameters.get('context-geo-city-us') != None and contextParameters.get('context-geo-city-us') != "" and contextParameters.get('context-geo-city-us') != []:
        resStr = contextParameters.get('context-geo-city-us') 
    elif contextParameters.get('context-geo-state-us') != None and contextParameters.get('context-geo-state-us') != "" and contextParameters.get('context-geo-state-us') != []:
        resStr = contextParameters.get('context-geo-state-us')    
    elif contextParameters.get('context-region') != None and contextParameters.get('context-region') != "":
        resStr = contextParameters.get('context-region')
    else:
        resStr = getStrDefaultRegion()

    return resStr

'''
Should return either the city or the state or the region or the default that the user has requested
'''
def generateResponseForRegion(parameters):
    resStr = ""

    if parameters.get('geo-city-us') != None and parameters.get('geo-city-us') != "" and parameters.get('geo-city-us') != []:
        resStr = parameters.get('geo-city-us')
    elif parameters.get('geo-city') != None and parameters.get('geo-city') != "" and parameters.get('geo-city') != []:
        resStr = parameters.get('geo-city')
    elif parameters.get('geo-state-us') != None and parameters.get('geo-state-us') != "" and parameters.get('geo-state-us') != []:
        resStr = parameters.get('geo-state-us')
    elif parameters.get('region') != None and parameters.get('region') != "":
        resStr = parameters.get('region')
    else:
        resStr = getStrDefaultRegion()

    return resStr


def generateContextResponseForPeriod(parameters, contextParameters, period):
    resStr = ""
    startDate = period["startDate"]
    endDate = period["endDate"]
    userPeriod = parameters.get('period')
    contextPeriod = contextParameters.get('context-period')

    if userPeriod == "" and contextPeriod == "":
        resStr += "in the duration between " + getStrDefaultStartDate() + " and " + getStrDefaultEndDate()
    elif userPeriod != None and userPeriod != "" and userPeriod.get('date') != None and userPeriod.get('date') != "":
        resStr += "on " + startDate
    elif userPeriod != None and userPeriod != "" and userPeriod.get('date-period') != None and userPeriod.get('date-period') != "":
        resStr += "in the duration between " + startDate + " and " + endDate
    elif contextPeriod != None and contextPeriod != "" and contextPeriod.get('date') != None and contextPeriod.get('date') != "":
        resStr += "on " + startDate    
    elif contextPeriod != None and contextPeriod != "" and contextPeriod.get('date-period') != None and contextPeriod.get('date-period') != "":
        resStr += "in the duration between " + startDate + " and " + endDate
    else:
        # TODO: Include default date
        resStr += "in the duration between " + getStrDefaultStartDate() + " and " + getStrDefaultEndDate()

    return resStr


def generateResponseForPeriod(parameters, period):
    resStr = ""
    startDate = period["startDate"]
    endDate = period["endDate"]
    userPeriod = parameters.get('period')

    if userPeriod == "":
        resStr += "in the duration between " + getStrDefaultStartDate() + " and " + getStrDefaultEndDate()
    elif userPeriod.get('date') != None:
        resStr += "on " + startDate
    elif userPeriod.get('date-period') != None:
        resStr += "in the duration between " + startDate + " and " + endDate
    else:
        # TODO: Include default date
        resStr += "in the duration between " + getStrDefaultStartDate() + " and " + getStrDefaultEndDate()

    return resStr
    

def parseContextUserPeriod(period, contextPeriod):
    '''print ("Period at index 0 is:" + period[0])'''
    '''print ("trying to get date at index 0" + period[0].get('date'))'''
    if period == "" and contextPeriod == "":
        return {"startDate": getStrDefaultStartDate(), "endDate": getStrDefaultEndDate(), "context-period": ""}
    elif period != None and period != "" and period.get('date') != None and period.get('date') != "":        
        parsedDate = parseDate(period.get('date'))
        parsedDate["context-period"] = {}
        parsedContextPeriod = parsedDate["context-period"]
        parsedContextPeriod["date"] = period.get('date')
        parsedContextPeriod["date-period"] = "" 
        return parsedDate
    elif period != None and period != "" and period.get('date-period') != None and period.get('date-period') != "":
        parsedDateRange = parseDateRange(period.get('date-period'))
        parsedDateRange["context-period"] = {}
        parsedContextPeriod = parsedDateRange["context-period"]
        parsedContextPeriod["date"] = ""
        parsedContextPeriod["date-period"] = period.get('date-period')
        return parsedDateRange
    elif contextPeriod != None and contextPeriod != "" and contextPeriod.get('date') != None and contextPeriod.get('date') != "":
        parsedDate = parseDate(contextPeriod.get('date'))
        parsedDate["context-period"] = {}
        parsedContextPeriod = parsedDate["context-period"]
        parsedContextPeriod["date"] = contextPeriod.get('date')
        parsedContextPeriod["date-period"] = "" 
        return parsedDate   
    elif contextPeriod != None and contextPeriod != "" and contextPeriod.get('date-period') != None and contextPeriod.get('date-period') != "":
        parsedDateRange = parseDateRange(contextPeriod.get('date-period'))
        parsedDateRange["context-period"] = {}
        parsedContextPeriod = parsedDateRange["context-period"]
        parsedContextPeriod["date"] = ""
        parsedContextPeriod["date-period"] = contextPeriod.get('date-period')
        return parsedDateRange
    else:
        # TODO: Include default date (This case should never arise)
        print ("Warning error condition reached in parse user period")
        return {"startDate": getStrDefaultStartDate(), "endDate": getStrDefaultEndDate(), "context-period": ""}


def parseUserPeriod(period):
    '''print ("Period at index 0 is:" + period[0])'''
    '''print ("trying to get date at index 0" + period[0].get('date'))'''
    if period == "":
        return {"startDate": getStrDefaultStartDate(), "endDate": getStrDefaultEndDate(), "context-period": ""}
    elif period.get('date') != None and period.get('date') != "":
        parsedDate = parseDate(period.get('date'))
        parseDate["context-period"] = {}
        parsedContextPeriod = parseDate["context-period"]
        parsedContextPeriod["date"] = period.get('date')
        parsedContextPeriod["date-period"] = "" 
        return parsedDate
    elif period.get('date-period') != None and period.get('date-period') != "":
        parsedDateRange = parseDateRange(period.get('date-period'))
        parsedDateRange["context-period"] = {}
        parsedContextPeriod = parsedDateRange["context-period"]
        parsedContextPeriod["date"] = ""
        parsedContextPeriod["date-period"] = period.get('date-period')
        return parsedDateRange
    else:
        # TODO: Include default date (This case should never arise)
        print ("Warning error condition reached in parse user period")
        return {"startDate": getStrDefaultStartDate(), "endDate": getStrDefaultEndDate(), "context-period": ""}
                                     
def parseDateRange(datePeriod):
    print("Inside Parse for Date Period")
    startDate = datePeriod.split('/')[0]
    print ("The start date is:" + startDate)
    endDate = datePeriod.split('/')[1]
    print ("The end date is:" + endDate)
    
    return {"startDate": startDate, "endDate": endDate}
    

def parseDate(date):
    print("Inside Parse for Date")
    
    return {"startDate": date, "endDate": ""}


'''
Parses the context user region and returns the city
'''
def parseContextUserRegion(parameters, contextParameters):
    if parameters.get('geo-city-us') != None and parameters.get('geo-city-us') != "" and parameters.get('geo-city-us') != []:
        return {'cities':[parameters.get('geo-city-us')], 'context-geo-city-us': parameters.get('geo-city-us'),'context-geo-state-us': '','context-region': ''}
    elif parameters.get('geo-city') != None and parameters.get('geo-city') != "" and parameters.get('geo-city') != []:
        return {'cities':[parameters.get('geo-city')],'context-geo-city-us': parameters.get('geo-city'),'context-geo-state-us': '','context-region': ''}
    elif parameters.get('geo-state-us') != None and parameters.get('geo-state-us') != "" and parameters.get('geo-state-us') != []:
        return {'cities':parseState(parameters.get('geo-state-us')),'context-geo-city-us': '','context-geo-state-us': parameters.get('geo-state-us'),'context-region': ''}
    elif parameters.get('region') != None and parameters.get('region') != "":
        return {'cities':parseRegion(parameters.get('region')),'context-geo-city-us': '','context-geo-state-us': '','context-region': parameters.get('region')}
    elif contextParameters.get('context-geo-city-us') != None and contextParameters.get('context-geo-city-us') != "" and contextParameters.get('context-geo-city-us') != []:
        return {'cities':[contextParameters.get('context-geo-city-us')],'context-geo-city-us': contextParameters.get('context-geo-city-us'),'context-geo-state-us': '','context-region': ''}  
    elif contextParameters.get('context-geo-state-us') != None and contextParameters.get('context-geo-state-us') != "" and contextParameters.get('context-geo-state-us') != []:
        return {'cities':parseState(contextParameters.get('context-geo-state-us')),'context-geo-city-us': '','context-geo-state-us': contextParameters.get('context-geo-state-us'),'context-region': ''}
    elif contextParameters.get('context-region') != None and contextParameters.get('context-region') != "":
        return {'cities':parseRegion(contextParameters.get('context-region')),'context-geo-city-us': '','context-geo-state-us': '','context-region': contextParameters.get('context-region')}
    else:
        return {'cities':getDefaultRegion(),'context-geo-city-us': '','context-geo-state-us': '','context-region': ''}

'''
Returns an array of cities (even if it is a single city)
'''
def parseUserRegion(parameters):
    if parameters.get('geo-city-us') != None and parameters.get('geo-city-us') != "" and parameters.get('geo-city-us') != []:
        return {'cities':[parameters.get('geo-city-us')],'context-geo-city-us': parameters.get('geo-city-us'),'context-geo-state-us': '','context-region': ''}
    elif parameters.get('geo-city') != None and parameters.get('geo-city') != "" and parameters.get('geo-city') != []:
        return {'cities':[parameters.get('geo-city')],'context-geo-city-us': parameters.get('geo-city'),'context-geo-state-us': '','context-region': ''}
    elif parameters.get('geo-state-us') != None and parameters.get('geo-state-us') != "" and parameters.get('geo-state-us') != []:
        return {'cities':parseState(parameters.get('geo-state-us')),'context-geo-city-us': '','context-geo-state-us': parameters.get('geo-state-us'),'context-region': ''}
    elif parameters.get('region') != None and parameters.get('region') != "":
        return {'cities':parseRegion(parameters.get('region')),'context-geo-city-us': '','context-geo-state-us': '','context-region': parameters.get('region')}
    else:
        return {'cities':getDefaultRegion(),'context-geo-city-us': '','context-geo-state-us': '','context-region': ''}


'''
TODO:: Fill with dummy data currently. Adding dummy comment
'''
def parseState(state):
    print ("This function should return a list of us cities linked to this state")

    stateData = mongo.db.states
    cities = []
    try:
        stateCur = stateData.find({            
            "state":state
            }, {
            "city": 1
            })

        for s in stateCur:
            print ("inside parse state the city is:" + s["city"])
            cities.append(s["city"])

        return cities

    except Exception:
        print("Could not query database")





def parseRegion(region):
    print ("This function should return a list of us cities linked to this region")

    regionNotation = ""

    if region == "North East":
        regionNotation = "NE"
    elif region == "North West":
        regionNotation = "NW"
    elif region == "South East":
        regionNotation = "SE"
    elif region == "South West":
        regionNotation = "SW"
    else:
        region = ""


    regionData = mongo.db.region
    cities = []
    try:
        regionCur = regionData.find({            
            "region":regionNotation
            }, {
            "city": 1
            })

        for r in regionCur:
            cities.append(r["city"])
            print("The city is:"+ r["city"])

        #print("the list of cities is:"+ cities[0])
        #print("the list of cities is:"+ cities[1])
        return cities

    except Exception:
        print("Could not query database")






def getDefaultRegion():
    print ("This function should return a list of us cities linked to the default region")
    return parseRegion(getStrDefaultRegion())


def getStrDefaultRegion():
    return "North East"

def getStrDefaultStartDate():
    return dt(2017,1,1,00,00).date().strftime("%Y-%m-%d")

def getStrDefaultEndDate():
    return dt.today().strftime('%Y-%m-%d')

def getStrDefaultProduct():
    return "Fan"

def getStrDefaultName():
    return "secretary"

def getStrDefaultChartType():
    return getStrBarChart()

def getStrBarChart():
    return "bar"

def getStrPieChart():
    return "pie"

def getStrDefaultMainChartFeature():
    return getStrProduct()

def getStrProduct():
    return "product-wise"

def getStrCity():
    return "city-wise"

def getStrState():
    return "state-wise"

def getStrRegion():
    return "region-wise"    

def getAllRegions():
    print ("This function should return a list of us cities in the database")


def getAllStates():
    print ("This function should return a list of us states in the database")


def getAllCities():
    print ("This function should return a list of us cities in the database")


def parseContextUserProduct(parameters, contextParameters):
    if parameters.get('product') != None and parameters.get('product') != "":
        return {'product': getPIdFromPName(parameters.get('product')), 'context-product': parameters.get('product')}
    elif contextParameters.get('context-product') != None and contextParameters.get('context-product') != "":
        return {'product': getPIdFromPName(contextParameters.get('context-product')), 'context-product': contextParameters.get('context-product')}
    else:
        return {'product': getDefaultProduct(), 'context-product': ''}


def parseContextUserProducts(parameters, contextParameters):
    if parameters.get('product') != None and parameters.get('product') != "" and parameters.get('product') != []:
        return {'product': getPIdsFromPNames(parameters.get('product')), 'context-product': parameters.get('product')}
    elif contextParameters.get('context-product') != None and contextParameters.get('context-product') != ""  and contextParameters.get('context-product') != []:
        return {'product': getPIdsFromPNames(contextParameters.get('context-product')), 'context-product': contextParameters.get('context-product')}
    else:
        return {'product': [getDefaultProduct()], 'context-product': ''}

def parseUserProducts(parameters):
    if parameters.get('product') != None and parameters.get('product') != "" and parameters.get('product') != []:
        return {'product': getPIdsFromPNames(parameters.get('product')), 'context-product': parameters.get('product')}
    else:
        return {'product': [getDefaultProduct()], 'context-product': []}

'''
Note should be depreciated to accomodate multiple products (Will require change in generating response and sales amount)
'''
def parseUserProduct(parameters):
    if parameters.get('product') != None and parameters.get('product') != "":
        return {'product': getPIdFromPName(parameters.get('product')), 'context-product': parameters.get('product')}
    else:
        return {'product': getDefaultProduct(), 'context-product': ''}

def getDefaultProduct():
    print ("This function should return a list a single default product or a list of products")
    return getPIdFromPName(getStrDefaultProduct())

def getAllProducts():
    print ("This function should return a list of all products in the database")


'''
Return an array of product ids
{{pNames}} Array of product names
'''
def getPIdsFromPNames(pNames):
    pIds = []
    for index in range(0, len(pNames)):
        pIds.append(getPIdFromPName(pNames[index]))

    return pIds


def getPIdFromPName(pName):
    print ("This function should return a product id from a product name")


    prodData = mongo.db.products
    try:
        prodCur = prodData.find({            
            "pName":pName
            }, {
            "pId": 1
            })

        for p in prodCur:
            pId = p["pId"]

        return pId

    except Exception:
        print("Could not query database")



def getPNameFromPId(pId):
    print ("This function should return a product name from a product id")


    prodData = mongo.db.products
    try:
        prodCur = prodData.find({            
            "pId":pId
            }, {
            "pName": 1
            })

        for p in prodCur:
            pName = p["pName"]

        return pName

    except Exception:
        print("Could not query database")


def parseUserChartType(parameters):
    if parameters.get('chart-type') != None and parameters.get('chart-type') != "" and parameters.get('chart-type') != []:
        return {'chart-type': parameters.get('chart-type'), 'context-chart-type': parameters.get('chart-type')}
    else:
        return {'chart-type': getDefaultChartType(), 'context-chart-type': ""}

def parseContextUserChartType(parameters, contextParameters):
    if parameters.get('chart-type') != None and parameters.get('chart-type') != "" and parameters.get('chart-type') != []:
        return {'chart-type': parameters.get('chart-type'), 'context-chart-type': parameters.get('chart-type')}
    elif contextParameters.get('context-chart-type') != None and contextParameters.get('context-chart-type') != "" and parameters.get('context-chart-type') != []:
        return {'chart-type': contextParameters.get('context-chart-type'), 'context-chart-type': contextParameters.get('context-chart-type')}
    else:
        return {'chart-type': getDefaultChartType(), 'context-chart-type': ""}
'''
This function should return the default chart type
'''
def getDefaultChartType():
    print ("This function should return the default chart type")
    return getStrDefaultChartType()

def parseUserMainChartFeature(parameters):
    print("main chart feature:"+ parameters.get('main-chart-feature'))
    if parameters.get('main-chart-feature') != None and parameters.get('main-chart-feature') != "" and parameters.get('main-chart-feature') != []:
        return {'main-chart-feature': parameters.get('main-chart-feature'), 'context-main-chart-feature': parameters.get('main-chart-feature')}
    else:
        return {'main-chart-feature': getDefaultMainChartFeature(), 'context-main-chart-feature': ""}


def parseContextUserMainChartFeature(parameters, contextParameters):
    if parameters.get('main-chart-feature') != None and parameters.get('main-chart-feature') != "" and parameters.get('main-chart-feature') != []:
        return {'main-chart-feature': parameters.get('main-chart-feature'), 'context-main-chart-feature': parameters.get('main-chart-feature')}
    elif contextParameters.get('context-main-chart-feature') != None and contextParameters.get('context-main-chart-feature') != "" and parameters.get('context-main-chart-feature') != []:
        return {'main-chart-feature': contextParameters.get('context-main-chart-feature'), 'context-main-chart-feature': contextParameters.get('context-main-chart-feature')}
    else:
        return {'main-chart-feature': getDefaultMainChartFeature(), 'context-main-chart-feature': ""}

def getDefaultMainChartFeature():
    print ("This function should return the default main chart feature")
    return getStrDefaultMainChartFeature()

def getDefaultEmail():
    print ("This function should return a list a single default email or a list of email")
    return getEmailFromName(getStrDefaultName())

def getEmailFromName(name):
    print ("This function should return email address from a name")


    contactData = mongo.db.contactInfo
    try:
        contactCur = contactData.find({            
            "name":name
            }, {
            "email": 1
            })

        for p in contactCur:
            emailAdd = p["email"]

        return emailAdd

    except Exception:
        print("Could not query database")

'''
This function parses the parameters and assumes that there is an attachment in the context
'''
def parseContextEmail(parameters, contextParameters):
    if parameters.get('contact-name') != None and parameters.get('contact-name') != "":
        return {'email-to': getEmailFromName(parameters.get('contact-name')), 'attachment-name': contextParameters.get('context-attachment-name')}
    else:
        return {'email-to': getDefaultEmail(), 'attachment-name': contextParameters.get('context-attachment-name')}

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


def makeListOfAllUsers(resp):
    '''
    resp.card(text='Dummy Card',title='Card title',img_url='https://drive.google.com/open?id=0BzU--BJmmVjua0dSVnZNYVJCLXc')

    return resp
    '''
    print("Inside make card")
    '''
    return {
        "simpleResponse": {
                                "textToSpeech": "Math and prime numbers it is!"
                            },
        "basicCard": {
                                "title": "Math & prime numbers",
                                "formattedText": "42 is an even composite number. It \n      is composed of three distinct prime numbers multiplied together. It \n      has a total of eight divisors. 42 is an abundant number, because the \n      sum of its proper divisors 54 is greater than itself. To count from \n      1 to 42 would take you about twenty-one…",
                                "image": {
                                    "url": "https://drive.google.com/open?id=0BzU--BJmmVjua0dSVnZNYVJCLXc",
                                    "accessibilityText": "Image alternate text"
                                },
                                "buttons": []
                            }
    }
    
    return {
        "simpleResponse": {
                                "textToSpeech": "Howdy! I can tell you fun facts about almost any number, like 42. What do you have in mind?",
                                "displayText": "Howdy! I can tell you fun facts about almost any number. What do you have in mind?"
                            },
         "source": "DDAsisstant"
    }
    '''

    # This is the database query to fetch the appropriate data (TODO: Move to another function)
    fullName = []
    designation = []
    bio = []
    profilePhoto = []
    keys = []
    baseUrl = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/"
    tempData = mongo.db.temp1
    try: 
        for s in tempData.find():
            keys.append(s['_id'])
            fullName.append(s['name'])
            print ("The name is:" + s['name'])
            designation.append(s['designation'])
            bio.append(s['bio'])
            photoUrl = baseUrl + s['photo']
            profilePhoto.append(photoUrl)

    except Exception:
        print("Could not query database")
        return makeWebhookResult('This name does not exist in the list!')
    
    print("Before opening image")
   
    #createImage()

    print("Before printing list item")
    #print(json.dumps(createListItem(fullName,fullName,designation,"https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png"), indent=4))
    #print(json.dumps(createListResponse("My sample response",["sug1","sug2"],"My list title",[fullName, "Charlie"],[fullName, "Dans"],[designation, "Cons"],["https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png","https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png"]), indent=4))

    return createListResponse(["Here are the employees of Deloitte Digital. Click on any one of them or say their names to view their detailed bio"],[],"DD Resources", keys, fullName, fullName, designation, profilePhoto, False)
    '''
    return {
        "speech": "Howdy",
        "displayText": "Howdy",
        "data": {
          "google": {
          "expect_user_response": True,
          "rich_response": {
          "items": [
            {
              "simpleResponse": {
                  "textToSpeech":"Here are all the employees of Deloitte Digital"
              }
            },
            {
              "basicCard": {
                "title":fullName,
                "formattedText":"Charles is an MBA from NMIMS",
                "subtitle":designation,
                "image": {
                  "url":"https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png",
                  "accessibilityText":"Image alternate text"
                },
                "buttons": [
                  {
                    "title":"View Profile",
                    "openUrlAction":{
                      "url":"https://assistant.google.com/"
                    }
                  }
                ]
              }
            }
          ],
          "suggestions":
          [
            {"title":"I have a new project"},
            {"title":"Search people with skills"}
          ]
        }
        }
        },
         #"contextOut": [],
        "source": "DDAsisstant"
    }
    '''
    '''
    return {
        "speech": "Howdy",
        "displayText": "Howdy",
        "data": {
          "google": {
          "expect_user_response": True,
          "rich_response": {
          "items": [
                {
                    "simpleResponse": {
                        "textToSpeech":"This is a simple response for a list"
                    }
                }
            ],
            "suggestions": [
                {
                    "title":"List"
                },
                {
                    "title":"Carousel"
                },
                {
                    "title":"Suggestions"
                }
            ]
        },
        "systemIntent": {
            "intent":"actions.intent.OPTION",
            "data": {
                "@type" : "type.googleapis.com/google.actions.v2.OptionValueSpec",
                "listSelect": {
                    "title":"List Title","items": [
                        {
                            "optionInfo": {
                                "key":"title",
                                "synonyms": [
                                "synonym of title 1",
                                "synonym of title 2",
                                "synonym of title 3"
                            ]
                        },
                        "title":"Title of First ListItem",
                        "description":"This is a description of a list item",
                        "image": {
                            "url":"https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png",
                            "accessibilityText":"Image alternate text"
                            }
                        },
                        {
                            "optionInfo": {
                                "key":"googleHome",
                                "synonyms": [
                                    "Google Home Assistant","Assistant on the Google Home"
                                ]
                            },
                            "title":"Google Home",
                            "description":"Google Home is a voice-activated speaker powered by the Google Assistant.",
                            "image": {
                                "url":"https://lh3.googleusercontent.com/Nu3a6F80WfixUqf_ec_vgXy_c0-0r4VLJRXjVFF_X_CIilEu8B9fT35qyTEj_PEsKw",
                                "accessibilityText":"Google Home"
                            }
                        },
                        {
                            "optionInfo": {
                                "key":"googlePixel",
                                "synonyms": [
                                    "Google Pixel XL",
                                    "Pixel","Pixel XL"
                                ]
                            },
                            "title":"Google Pixel",
                            "description":"Pixel. Phone by Google.",
                            "image": {
                                "url":"https://storage.googleapis.com/madebygoog/v1/Pixel/Pixel_ColorPicker/Pixel_Device_Angled_Black-720w.png",
                                "accessibilityText":"Google Pixel"
                            }
                        },
                        {
                            "optionInfo": {
                                "key":"googleAllo",
                                "synonyms": [
                                    "Allo"
                                ]
                            },
                            "title":"Google Allo",
                            "description":"Introducing Google Allo, a smart messaging app that helps you say more and do more.",
                            "image": {
                                "url":"https://allo.google.com/images/allo-logo.png",
                                "accessibilityText":"Google Allo Logo"
                            }
                        }
                    ]
                }
            }
        }
        }
        },
         #"contextOut": [],
        "source": "DDAsisstant"
    }
    '''


def createImage():
    image = Image.open('profile.jpg')
    image.show()

'''
This function returns a card response
'''
def createCardResponse(simpleResponse, sugList, title, formattedText, subtitle, imgURL, imgAccText, btnTitleList, btnUrlList, expectedUserResponse, contextList):
    cardResponse = {}

    itemsDict = {}
    itemsDict["simpleResponse"] = {}
    simpleResponseDict = itemsDict["simpleResponse"]
    simpleResponseDict["textToSpeech"] = simpleResponse[0]

    basicCardDict = {}
    basicCardDict["basicCard"] = createCard(title, formattedText, subtitle, imgURL, imgAccText, btnTitleList, btnUrlList)

    cardResponse["data"] = {}
    cardResponse["source"] = "phillips-bot"

    #Adding context
    if contextList == None or contextList == "":
        outputContext = []
    else:
        outputContext = contextList
        print("The length of context list in card response is:"+str(len(outputContext)))

    cardResponse["contextOut"] = outputContext

    dataDict = cardResponse["data"]

    dataDict["google"] = {}
    googleDict = dataDict["google"]

    googleDict["expect_user_response"] = expectedUserResponse
    googleDict["rich_response"] = {}
    

    richResponseDict = googleDict["rich_response"]
    richResponseDict["items"] = []
    

    itemList = richResponseDict["items"]
    itemList.append(itemsDict)
    itemList.append(basicCardDict)

    if len(simpleResponse) > 1:
        secondItemsDict = {}
        secondItemsDict["simpleResponse"] = {}
        secondSimpleResponseDict = secondItemsDict["simpleResponse"]
        secondSimpleResponseDict["textToSpeech"] = simpleResponse[1]
        itemList.append(secondItemsDict)

    richResponseDict["suggestions"] = createSuggestionList(sugList)

    

    return cardResponse

'''
This function creates a card
'''
def createCard(title, formattedText, subtitle, imgURL, imgAccText, btnTitleList, btnUrlList):
    basicCard = {}

    if title != "":
        basicCard["title"] = title

    basicCard["formattedText"] = formattedText

    if subtitle != "":
        basicCard["subtitle"] = subtitle

    basicCard["image"] = {}

    imageDict = basicCard["image"]
    imageDict["url"] = imgURL
    imageDict["accessibilityText"] = imgAccText

    basicCard["buttons"] = []

    buttonsList = basicCard["buttons"]

    for index in range(len(btnTitleList)):
        buttonsList.append(createButton(btnTitleList[index], btnUrlList[index]))

    return basicCard


def createButton(title, openUrlAction):
    btnDict = {}

    btnDict["title"] = title
    btnDict["openUrlAction"] = {}

    openUrlActionDict = btnDict["openUrlAction"]
    openUrlActionDict["url"] = openUrlAction

    return btnDict
'''
This function creates a single list item to be used for generating the list card item
'''
def createListItem(key, title, syn, description, imgURL):
    listItemDict = {}
    listItemDict["optionInfo"] = {}

    optionInfoDict = listItemDict["optionInfo"]
    optionInfoDict["key"] = key
    optionInfoDict["synonyms"] = []

    synList = optionInfoDict["synonyms"]
    synList.append(syn)

    listItemDict["title"] = title
    listItemDict["description"] = description

    listItemDict["image"] = {}

    imageDict = listItemDict["image"]
    imageDict["url"] = imgURL
    imageDict["accessibilityText"] = "This is a temporary accessibility text"

    return listItemDict


'''
This function creates an entire list that is used for generating the list card
'''
def createList(listTitle, keyArr, titleArr, synArr, descriptionArr, imgUrlArr):
    systemIntentDict = {}
    systemIntentDict["intent"] = "actions.intent.OPTION"
    systemIntentDict["data"] = {}

    dataDict = systemIntentDict["data"]
    dataDict["@type"] = "type.googleapis.com/google.actions.v2.OptionValueSpec"
    dataDict["listSelect"] = {}

    listSelectDict = dataDict["listSelect"]
    listSelectDict["title"] = listTitle
    listSelectDict["items"] = []

    itemList = listSelectDict["items"]

    for index in range(len(titleArr)):
        itemList.append(createListItem(keyArr[index], titleArr[index], synArr[index], descriptionArr[index], imgUrlArr[index]))


    return systemIntentDict


def createListResponse(simpleResponseArr, sugList, listTitle, keyArr, titleArr, synArr, descriptionArr, imgUrlArr, expectedUserResponse):
    listResponse = {}
    itemsDict = {}
    itemsDict["simpleResponse"] = {}
    simpleResponseDict = itemsDict["simpleResponse"]
    simpleResponseDict["textToSpeech"] = simpleResponseArr[0]

    #Code to add multiple simple responses (Seems unwieldy & needs to be better done for a loop)
    if len(simpleResponseArr) > 1:
        itemsDict1 = {}
        itemsDict1["simpleResponse"] = {}
        simpleResponseDict1 = itemsDict1["simpleResponse"]
        simpleResponseDict1["textToSpeech"] = simpleResponseArr[1]

    listResponse["data"] = {}
    listResponse["source"] = "DDAsisstant"
    dataDict = listResponse["data"]

    dataDict["google"] = {}
    googleDict = dataDict["google"]

    googleDict["expect_user_response"] = expectedUserResponse
    googleDict["rich_response"] = {}
    

    richResponseDict = googleDict["rich_response"]
    richResponseDict["items"] = []
    

    itemList = richResponseDict["items"]
    itemList.append(itemsDict)

    if len(simpleResponseArr) > 1:
        itemList.append(itemsDict1)

    richResponseDict["suggestions"] = createSuggestionList(sugList)

    googleDict["systemIntent"] = createList(listTitle, keyArr, titleArr, synArr, descriptionArr, imgUrlArr)

    return listResponse


def createSuggestion(title):
    suggestionDict = {}
    suggestionDict["title"] = title
    return suggestionDict

def createSuggestionList(titleList):
    suggestionList = []
    for index in range(len(titleList)):
        suggestionList.append(createSuggestion(titleList[index]))

    return suggestionList

def getParameters(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("city")
    print("The city is:")
    print(city)
    '''
    duration = parameters.get("Duration")
    print("The duration is:")
    print(duration)
    sales = queryData(city, duration)
    '''
    period = parameters.get("period")
    print("The period is:")
    print(period)
    sales = parsePeriod(period, city)
    print("The sales are:")
    print(sales)
    
    '''return "The sales data for " + city + "and duration" + duration + "is 12345"'''
    return "The sales data for " + city + " and duration is " + sales
    '''return "abcd"'''

'''
TODO: REMOVE
'''
def getDummyParameters(req):
    result = req.get("result")
    parameters = result.get("parameters")
    period = parameters.get("period")
    print("The period is:")
    print(period)
    amount = parsePeriod(period)
    
    return "The amount for this duration is " + amount
    

def parsePeriod(period, city):
    '''print ("Period at index 0 is:" + period[0])'''
    '''print ("trying to get date at index 0" + period[0].get('date'))'''
    if period.get('date') != None:
        return queryDataForDate(period.get('date'), city)
    elif period.get('date-period') != None:
        return queryDateForDateRange(period.get('date-period'), city)
    else:
        return 'does not exist in the database'
                                     
def queryDateForDateRange(datePeriod, city):
    print("Inside Query for Date Period")
    startDate = datePeriod.split('/')[0]
    print ("The start date is:" + startDate)
    endDate = datePeriod.split('/')[1]
    print ("The end date is:" + endDate)
    startAmount = None
    amount = 0
    sale = mongo.db.sales  
    
    try: 
        for s in sale.find({'city': city}):
            print ("The date is:" + s['date'])
            if (dt.strptime(s['date'], "%Y-%m-%d") >= dt.strptime(startDate, "%Y-%m-%d")) and (dt.strptime(s['date'], "%Y-%m-%d") <= dt.strptime(endDate, "%Y-%m-%d")):
                print ("Inside if")
                startAmount = 0
                amount = amount + int(s['amount'])
        if startAmount != None:
            return str(amount)
        else:
            return 'not there in the database'
    except Exception:
        print("Could not query database")
        return ''
    

def queryDataForDate(date, city):
    print("Inside Query for Date")
    sale = mongo.db.sales
    startAmount = None
    amount = 0
    
    try: 
        for s in sale.find({'city': city,'date': date}):
            print("The sales amount is:"+s['amount'])
            startAmount = 0
            amount = amount + int(s['amount'])
        if startAmount != None:
            return str(amount)
        else:
            return 'not there in the database'
    except Exception:
        print("Could not query database")
        return ''


# Sending a message back through Messenger.
def send_message(sender_id, message_text):
    print('in send msg')
    r = requests.post("https://api.api.ai/v1/",
 
        
 
        headers={"Content-Type": "application/json"},
 
        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }))



# Takes a string of natural language text, passes it to ApiAI, returns a
# response generated by an ApiAI bot.
def parse_natural_text(user_text):
    print('hi there!')
    # Sending a text query to our bot with text sent by the user.
    request = ai.text_request()
    request.query = user_text
 
    # Receiving the response.
    response = json.loads(request.getresponse().read().decode('utf-8'))
    responseStatus = response['status']['code']
    if (responseStatus == 200):
        # Sending the textual response of the bot.
        return (response['result']['fulfillment']['speech'])
 
    else:
        return ("Sorry, I couldn't understand that question")
 
    # NOTE:
    # At the moment, all messages sent to ApiAI cannot be differentiated,
    # they are processed as a single conversation regardless of concurrent
    # conversations. We need to perhaps peg a session id (ApiAI) to a recipient
    # id (Messenger) to fix this.
 
    # request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
 
# Sends the message in segments delimited by a period.
def send_message_staggered(sender_id, message_text):
    print('staggered') 
    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)
   
    for message in messages:
        send_message(sender_id, message)

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
