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
from datetime import timedelta
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
from constants import Constants
from card import Card
from rauth import OAuth2Service
import urllib
from urllib.request import urlopen
import secrets
from facepy import GraphAPI

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

app.config['OAUTH_CREDENTIALS'] = {
    'google': {
            'id': os.environ['GOOGLE_LOGIN_CLIENT_ID'],
            'secret': os.environ['GOOGLE_LOGIN_CLIENT_SECRET']
    },
    'facebook': {
        'id': os.environ['FACEBOOK_LOGIN_CLIENT_ID'],
        'secret': os.environ['FACEBOOK_LOGIN_CLIENT_SECRET']
    }
}

mongo = PyMongo(app)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)



class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                        _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers={}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        #TODO this is an external file. Need to host it on my server        
        googleinfo = urlopen('https://accounts.google.com/.well-known/openid-configuration')
        google_params = json.load(googleinfo)
        self.service = OAuth2Service(
                name='google',
                client_id=self.consumer_id,
                client_secret=self.consumer_secret,
                authorize_url=google_params.get('authorization_endpoint'),
                base_url=google_params.get('userinfo_endpoint'),
                access_token_url=google_params.get('token_endpoint')
        )

    def authorize(self):
        print("the request arguments are:"+ str(request.args))
        print("the authorization endpoint url is:"+str(self.service.get_authorize_url(
            scope='email https://www.google.com/m8/feeds/',
            response_type='code',
            redirect_uri=self.get_callback_url())))
        print ("the callback url is:"+str(self.get_callback_url()))
        '''
        Storing all the values
        '''
        if 'scope' in request.args:
            self.scope = request.args['scope']
            print("scope::"+self.scope)


        if 'client_id' in request.args:
            self.client_id = request.args['client_id']
            print("client_id::"+self.client_id)
            #Checking if the client id passed is the same as the one registered with google
            if self.consumer_id != self.client_id:
                print("The consumer and client ids do not match")
                return '' #TODO:this return statement should be modified to fail gracefully

        else:
            return '' #TODO:this return statement should be modified to fail gracefully


        if 'redirect_uri' in request.args:
            self.redirect_uri = request.args['redirect_uri']
            session['redirect_uri'] = request.args['redirect_uri']
            print("redirect_uri::"+self.redirect_uri)
            #Checking if the redirect uri passed is the same as the one registered with google
            if self.redirect_uri != os.environ['GOOGLE_REDIRECT_URI']:
                print("The redirect uri does not match with the one registered on google")
                return '' #TODO:this return statement should be modified to fail gracefully                
        else:
            return '' #TODO:this return statement should be modified to fail gracefully

        if 'state' in request.args:
            self.state = request.args['state']
            session['state'] = request.args['state']
            print("state::"+self.state)


        if 'response_type' in request.args:
            self.response_type = request.args['response_type']
            print("response_type::"+self.response_type)
            #Checking if the redirect uri passed is the same as the one registered with google
            if self.response_type != 'code':
                print("The response type is not code")
                return '' #TODO:this return statement should be modified to fail gracefully                   
        else:
            return '' #TODO:this return statement should be modified to fail gracefully
        '''
        End of storing values
        '''
        return redirect(self.service.get_authorize_url(
            scope='email https://www.google.com/m8/feeds/',
            response_type='code',
            redirect_uri=self.get_callback_url())
            )

    def callback(self):
        print("the request arguments are:"+ str(request.args))
        if 'code' not in request.args:
            return None, None, None
        print("the code request arguments are:"+ str(request.args['code']))
        oauth_session = self.service.get_auth_session(
                data={'code': request.args['code'],
                      'grant_type': 'authorization_code',
                      'redirect_uri': self.get_callback_url()
                     },
                decoder = json.loads
        )
        me = oauth_session.get('').json()
        print("The me is:"+ str(me))
        return (me['name'],
                me['email'])

    def getCallbackURI(self, email, expiryTime):

        if session['redirect_uri'] != os.environ['GOOGLE_REDIRECT_URI']:
                print("The redirect uri does not match with the one registered on google")
                return '' #TODO:this return statement should be modified to fail gracefully 

        secureAuthCode = self.generateSecretToken()
        self.addSecretTokenToDb(secureAuthCode, email, expiryTime)
        print("the secret auth code is::"+secureAuthCode) 
        #getVars = {'code': 'abcdefgh','state': session['state']}
        getVars = {'code': secureAuthCode,'state': session['state']}
        callbackURI = session['redirect_uri'] + '?' + urllib.parse.urlencode(getVars)
        print('callback uri is::'+callbackURI)
        print("Adding comment")
        return callbackURI

    def generateSecretToken(self):
        return secrets.token_hex(32)

    def addSecretTokenToDb(self, id, email, expiryTime):
        tokenCodes = mongo.db.tokens
        tokenCodes.insert({'_id' : id, 'type' : 'AUTH_CODE',
                            'userId': email,'clientId': 'google',
                            'expiresAt': expiryTime})

    def addRefreshTokenToDb(self, id, email):
        tokenCodes = mongo.db.tokens
        tokenCodes.insert({'_id' : id, 'type' : 'REFRESH',
                            'userId': email,'clientId': 'google'})

    def addAccessTokenToDb(self, id, email, expiryTime):
        tokenCodes = mongo.db.tokens
        tokenCodes.insert({'_id' : id, 'type' : 'ACCESS',
                            'userId': email,'clientId': 'google',
                            'expiresAt': expiryTime})

    def getTokenResponse(self):
        print("Inside get token response")

        print("In token request args are::::::")
        print(str(list(request.form)))
        reqArgs = request.form
        print("the req args are:"+ str(reqArgs))

        if 'client_id' in reqArgs:
            #Checking if the client id passed is the same as the one registered with google
            if self.consumer_id != reqArgs['client_id']:
                print("The consumer and client ids do not match")
                return '' #TODO:this return statement should be modified to fail gracefully
        else:
            return '' #TODO:this return statement should be modified to fail gracefully


        if 'client_secret' in reqArgs:
            #Checking if the client secret passed is the same as the one registered with google
            if self.consumer_secret != reqArgs['client_secret']:
                print("The consumer and client secrets do not match")
                return '' #TODO:this return statement should be modified to fail gracefully
        else:
            return '' #TODO:this return statement should be modified to fail gracefully

        if 'grant_type' in reqArgs:
            grantType = reqArgs['grant_type']
            if grantType == 'authorization_code':
                if isTokenValid(reqArgs['code']) == True:
                    print("Token is valid")
                    tokenRecord = getTokenRecord(reqArgs['code'])
                    accessTokenId = self.generateSecretToken()
                    refreshTokenId = self.generateSecretToken()
                    self.addAccessTokenToDb(accessTokenId, tokenRecord['userId'], getStrFutureDateAndTime(60))
                    self.addRefreshTokenToDb(refreshTokenId, tokenRecord['userId'])
                    response = {}
                    response['token_type'] = "bearer"
                    response['access_token'] = accessTokenId
                    response['refresh_token'] = refreshTokenId
                    response['expires_in'] = 3600
                else:
                    response = {}
                    response['error'] = "invalid_grant"
                    response = json.dumps(response, indent=4, cls=JSONEncoder)
                    print(response)
                    r = make_response(response, 400)
                    return r
            elif grantType == 'refresh_token':
                print("Inside only refresh token")
                reqRefreshToken = reqArgs['refresh_token']
                if isRefreshTokenValid(reqRefreshToken) == True:
                    print("refresh token is valid")
                    refreshTokenRecord = getTokenRecord(reqRefreshToken)
                    accessTokenId = self.generateSecretToken()
                    self.addAccessTokenToDb(accessTokenId, refreshTokenRecord['userId'], getStrFutureDateAndTime(60))
                    response = {}
                    response['token_type'] = "bearer"
                    response['access_token'] = accessTokenId
                    response['expires_in'] = 3600
                else:
                    response = {}
                    response['error'] = "invalid_grant"
                    response = json.dumps(response, indent=4, cls=JSONEncoder)
                    print(response)
                    r = make_response(response, 400)
                    return r
            else:
                return ''#TODO:this return statement should be modified to fail gracefully
        else:
            return '' #TODO:this return statement should be modified to fail gracefully

        '''
        response = {}
        response['token_type'] = "bearer"
        response['access_token'] = "1234"
        response['expires_in'] = 100000
        '''
        print("response::")
        print(str(response))
        response = json.dumps(response, indent=4, cls=JSONEncoder)
        print(response)
        r = make_response(response)
        r.headers['Content-Type'] = 'application/json'

        return r

class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):

        print("In FB authorize the request arguments are:"+ str(request.args))
        print("In FB authorize the authorization endpoint url is:"+str(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())))
        print ("In FB authorize the callback url is:"+str(self.get_callback_url()))


        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        print("IN  FB callback the request arguments are:"+ str(request.args))

        if 'code' not in request.args:
            return None, None, None
        session['facebook_code'] = request.args['code']
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )
        me = oauth_session.get('me?fields=id,email').json()
        print("The users id is:::" + str(me.get('id')))
        print("The users name is:::" + str(me.get('email').split('@')[0]))
        print("The users email is:::" + str(me.get('email')))

        session['profile_id'] = me.get('id')

        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0],  # Facebook does not provide
                                            # username, so the email's user
                                            # is used instead
            me.get('email')
        )

    def getCallbackURI(self, email, expiryTime):
        print("In get callback URI of facebook")
        secureAuthCode = self.generateSecretToken()
        self.addSecretTokenToDb(secureAuthCode, email, expiryTime)
        print("the secret auth code is::"+secureAuthCode) 
        #getVars = {'code': 'abcdefgh','state': session['state']}
        #getVars = {'code': secureAuthCode,'state': session['state']}
        '''
        getVars = {'grant_type':'fb_exchange_token','client_id':self.consumer_id,
                    'client_secret':self.consumer_secret,'fb_exchange_token': secureAuthCode}
        '''
        '''
        getVars = {'grant_type':'client_credentials','client_id':self.consumer_id,
                    'client_secret':self.consumer_secret}
        '''
        getVars = {'code': session['facebook_code'],'client_id':self.consumer_id,
                    'client_secret':self.consumer_secret, 'redirect_uri': self.get_callback_url()}
        callbackURI = 'https://graph.facebook.com/oauth/access_token' + '?' + urllib.parse.urlencode(getVars)
        print("the callback uri is::"+ callbackURI)
        # Getting the token
        '''
        tokenReq = urllib.request.Request(callbackURI)
        tokenResponse = urlopen(tokenReq).read()
        #tokenResponse = urlopen(callbackURI)
        token_params = json.load(tokenResponse)
        print("The token response in getCallbackURI" + str(token_params))
        print('callback uri is::'+callbackURI)

        #Posting to wall
        access_token = token_params['access_token']
        '''
        '''
        graph = GraphAPI(access_token)
        og_path = "%d/feed" %session['profile_id']
        #og_path = session['profile_id'] + "/feed" 

        graph.post( path = og_path, message = "Because office parties rarely disappoint" )
        '''
        print("Adding comment")
        return callbackURI


    def generateSecretToken(self):
        return secrets.token_hex(32)

    def addSecretTokenToDb(self, id, email, expiryTime):
        tokenCodes = mongo.db.tokens
        tokenCodes.insert({'_id' : id, 'type' : 'AUTH_CODE',
                            'userId': email,'clientId': 'facebook',
                            'expiresAt': expiryTime})

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
def index():
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


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    # Flask-Login function
    '''
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    '''
    print("In authorize for google")
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>', methods=['GET', 'POST'])
def oauth_callback(provider):
    '''
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    '''
    print("In callback for google")
    oauth = OAuthSignIn.get_provider(provider)
    if provider == "facebook":
        myId, username, email = oauth.callback()
        print("the id is:"+myId)
        print("the username is:"+username)
        print("the email is:"+email)
        gCallbackURI = oauth.getCallbackURI(email, getStrFutureDateAndTime(10))
        return redirect(gCallbackURI)
    else:
        username, email = oauth.callback()
        print("the username is:"+username)
        print("the email is:"+email)
        if email is None:
            # I need a valid email address for my user identification
            print('Authentication failed')
            #flash('Authentication failed.')
            return redirect(url_for('index'))
        # Look if the user already exists
        users = mongo.db.users
        loginUser = users.find_one({'username' : email})
        
        #user=User.query.filter_by(email=email).first()
        if not loginUser:
            # Create the user. Try and use their name returned by Google,
            # but if it is not set, split the email address at the @.
            '''
            nickname = username
            if nickname is None or nickname == "":
                nickname = email.split('@')[0]
            '''
            # We can do more work here to ensure a unique nickname, if you 
            # require that.
            '''
            user=User(nickname=nickname, email=email)
            db.session.add(user)
            db.session.commit()
            '''
            user_obj = User(email)
        else:
            user_obj = User(loginUser['username'])
        # Log in the user, by default remembering them for their next visit
        # unless they log out.
        '''
        login_user(user, remember=True)
        '''
        login_user(user_obj)
        #return redirect(url_for('index'))
        gCallbackURI = oauth.getCallbackURI(email, getStrFutureDateAndTime(10))
        return redirect(gCallbackURI)

@app.route('/callback/<provider>',methods=['POST'])
def oauth_callback_token(provider):
    print("In token callback for facebook")
    oauth = OAuthSignIn.get_provider(provider)
    print(str(list(request.form)))
    reqArgs = request.form
    print("the req args are:"+ str(reqArgs))

'''
@app.route('/token/<provider>')
def oauth_token(provider):
    print("In token exchange for google")
    oauth = OAuthSignIn.get_provider(provider)
    print("In token request args are:::::"+ str(request.args))
    return redirect(url_for('index'))
'''
@app.route('/token/<provider>',methods=['POST'])
def oauth_token(provider):
    '''
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    '''
    print("In token exchange for google")
    #oauth = OAuthSignIn.get_provider(provider)
    #data = request.get_json(force=True)
    '''
    print("In token request args are::::::")
    print(str(list(request.form)))
    reqArgs = request.form
    print("the req args are:"+ str(reqArgs))
    '''
    #print(json.dumps(data, indent=4))
    #print(json.loads(data))

    #Creating the oauth class
    oauth = OAuthSignIn.get_provider(provider)
    r = oauth.getTokenResponse()

    '''
    response = {}
    response['token_type'] = "bearer"
    response['access_token'] = "1234"
    response['expires_in'] = 100000
    print("response::")
    print(str(response))
    response = json.dumps(response, indent=4, cls=JSONEncoder)
    print(response)
    r = make_response(response)
    r.headers['Content-Type'] = 'application/json'
    '''
    print("End token exchange")
    #return redirect(url_for('index'))
    return r

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


    if data.get("result").get("action") == "free.delivery":
        simpleResponse = []
        simpleResponse.append("This is your coupon code")
        sugList = []
        sugList.append("Show digital employees")
        sugList.append("Bye doctor dashboard")

        title = "Dr. Dashboard"
        formattedText = "Coupon code"
        imgURL = Constants.getBlueBotURL()
        imgAccText = "Default accessibility text"

        myCard = Card(simpleResponse, formattedText, imgURL, imgAccText)
        myCard.addTitle(title)
        myCard.addSugTitles(sugList)
        myCard.addLinkBtn('Share on Facebook', 'https://phillipsbot.herokuapp.com/authorize/facebook')        
        myCard.addExpectedUserResponse()

        res = myCard.getCardResponse()

    else:
        mainRequestControllerObj = MainRequestController(data, mongo)
        #res = processRequest(data)
        res = mainRequestControllerObj.processRequest()

    '''
    print("In webhook for facebook")
    oauth = OAuthSignIn.get_provider("facebook")
    oauth.authorize()
    '''
    '''
    Checking if the token exists and if expired
    
    if hasTokenExpired(data) == True:
        response = {}
        response['error'] = "Unauthorized"
        response = json.dumps(response, indent=4, cls=JSONEncoder)
        print("Token has expired::" + response)
        r = make_response(response, 401)
        return r
    '''    
    '''
    mainRequestControllerObj = MainRequestController(data, mongo)
    #res = processRequest(data)
    res = mainRequestControllerObj.processRequest()
    '''

    res = json.dumps(res, indent=4, cls=JSONEncoder)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print("Before final return")
    return r


def hasTokenExpired(req):
    accessTokenFromRequest = req.get('originalRequest').get('data').get('user').get('accessToken')
    print("accessTokenFromRequest:: "+ accessTokenFromRequest) 

    if isTokenValid(accessTokenFromRequest) == True:
        return False
    else:
        return True









def getCurrentDateAndTime():
    return dt.now()

def getStrCurrentDateAndTime():
    return getCurrentDateAndTime().strftime("%Y-%m-%d %H:%M:%S")

def getFutureDateAndTime(mins):
    #print("The current date time now is::" + str(getCurrentDateAndTime()))
    #print("The current string date time is::" + getStrCurrentDateAndTime())
    return getCurrentDateAndTime() + timedelta(minutes=mins)

def getStrFutureDateAndTime(mins):
    #print("the future date time is:"+ getFutureDateAndTime(mins).strftime("%Y-%m-%d %H:%M:%S"))
    return getFutureDateAndTime(mins).strftime("%Y-%m-%d %H:%M:%S")

'''
Returns the record from the db containing the token id
'''
def getTokenRecord(id):
    print("Inside getTokenRecord")
    tokens = mongo.db.tokens
    existing_token = tokens.find_one({'_id' : id})

    if not existing_token:
        return 'Token does not exist in db'

    return existing_token
'''
Checks and returns whether the token is valid or not
'''
def isTokenValid(id):
    print("Inside isTokenValid")
    tokens = mongo.db.tokens
    existing_token = tokens.find_one({'_id' : id})

    if not existing_token:
        return 'Token does not exist in db'

    dbDateTime = existing_token['expiresAt']
    return compareDateAndTime(getStrCurrentDateAndTime(), dbDateTime)

def isRefreshTokenValid(id):
    print("Inside isRefreshTokenValid")
    tokens = mongo.db.tokens
    existing_token = tokens.find_one({'_id' : id})

    if not existing_token:
        return False

    return True

'''
Compares date time 1 with date time 2
Returns True if 1 < 2
Else False
'''
def compareDateAndTime(dateTime1, dateTime2):
    if dt.strptime(dateTime1, "%Y-%m-%d %H:%M:%S")  < dt.strptime(dateTime2, "%Y-%m-%d %H:%M:%S"):
        return True
    else:
        return False

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
