from date_utils import DateUtils
class UserDataModel(object):
	"""docstring for UserData"""
	def __init__(self, mongo):
		super(UserDataModel, self).__init__()
		self.mongo = mongo
		self.accessToken = None
		self.email = None
		self.username = None

	def checkAndInsertGoogleData(self, email, username):
		if self.checkIfGoogleEmailExists(email) == False:
			self.insertGoogleData(email, username)
			self.setDefaultPermissions(email)

	def addFBData(self, email, profileId, fbUsername, fbEmail):
		self.insertFBData(email, profileId, fbUsername, fbEmail)


	def setDefaultPermissions(self, email):
		userdatacollection = self.mongo.db.userdata
		user = userdatacollection.find_one({'email' : email})

		userpermissionscollection = self.mongo.db.userpermissions
		userpermissionscollection.insert({'userId': user['_id'], 
			'locationPermissionGranted' : False, 
			'geolocation' : '',
			'offerSubscribed': False})


	def updateLogs(self):
		userdatacollection = self.mongo.db.userdata
		user = userdatacollection.find_one({'email' : self.email})

		userlogs = self.mongo.db.userlogs
		currentUserlog = userlogs.find_one({'userId': user['_id']})

		if currentUserlog:
			userlogs.update(
		    	{'userId' : currentUserlog['userId']},
		    	{
		    		'$inc': { 'views': int(1) },
		        	'$set': {
		        		"lastLogin": DateUtils.getStrCurrentDateAndTime()
		        	}
		    	}
			)
		else:
			userlogs.insert({'userId': user['_id'], 
			'createdOn' : DateUtils.getStrCurrentDateAndTime(), 
			'lastLogin' : DateUtils.getStrCurrentDateAndTime(),
			'views': 1})



	def setAccessToken(self, accessToken):
		self.accessToken = accessToken
		accessTokenEmail = self.getGoogleEmailFromAccessToken(accessToken) 
		if accessTokenEmail != False:
			self.email = accessTokenEmail
			#self.updateLogs()


	#Utility functions
	def checkIfGoogleEmailExists(self, email):
		userdatacollection = self.mongo.db.userdata
		user = userdatacollection.find_one({'email' : email})
		if user:
			return True
		else:
			return False

	def insertGoogleData(self, email, username):
		userdatacollection = self.mongo.db.userdata
		userdatacollection.insert({'email' : email, 'username' : username})


	def insertFBData(self, email, profileId, fbUsername, fbEmail):
		userdatacollection = self.mongo.db.userdata
		userdatacollection.update(
			{'email' : email},
			{
		    	'$set': {
		    		"fbprofileId": profileId,
		    		"fbUsername": fbUsername,
		    		"fbemail": fbEmail
		    	}
			}
		)

	def getGoogleEmailFromAccessToken(self, accessToken):
		tokens = self.mongo.db.tokens
		existing_token = tokens.find_one({'_id' : accessToken})
		if existing_token:
			return existing_token['userId']
		else:
			return False
		
	#Getter-Setter Functions
	def getUsername(self):
		if self.username != None and self.username != '':
			return self.username
		else:
			userdatacollection = self.mongo.db.userdata
			user = userdatacollection.find_one({'email' : self.email})
			if user:
				self.username = user['username']
				return self.username
			else:
				self.username = None
				return False