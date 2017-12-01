from permission_response import PermissionResponse
from location_parser import LocationParser
class FreeDeliveryController(object):
	"""docstring for FreeDeliveryController"""
	def __init__(self, requestData, mongo):
		super(FreeDeliveryController, self).__init__()
		self.requestData = requestData
		self.mongo = mongo
		self.isPermissionGiven = False
		self.source = None


	def setIsPermissionGiven(self, isPermissionGiven):
		self.isPermissionGiven = isPermissionGiven

	def getIsPermissionGiven(self):
		return self.isPermissionGiven

	def getPermissionJSON(self):
		speech = self.parseFreeDeliveryRequest()
		return self.makePermissionsResult(speech["speech"], []) 

	def setSource(self, source):
		self.source = source

	def parseFreeDeliveryRequest(self):
	    
		return {
		    "speech" : "I need access to your device location to perform this task"
		}

	def makePermissionsResult(self, speech, context):

		#permissionResObj = PermissionResponse(speech, "To deliver your order")
		permissionResObj = PermissionResponse.get_provider(self.source, speech, "To deliver your order")
		permissionResObj.addNamePermission()
		permissionResObj.addPreciseLocationPermission()
		return permissionResObj.getPermissionResponseJSON()

		'''
	    dataJSON = {}
	    dataJSON["google"] = {}
	    googleJSON = dataJSON["google"]

	    googleJSON["expectUserResponse"] = True
	    googleJSON["systemIntent"] = {}

	    #possibleIntents = []

	    permissionDict = googleJSON["systemIntent"]
	    permissionDict["intent"] = "actions.intent.PERMISSION"
	    permissionDict["data"] = {}

	    inputValueDataDict = permissionDict["data"]
	    inputValueDataDict["@type"] = "type.googleapis.com/google.actions.v2.PermissionValueSpec"
	    inputValueDataDict["optContext"] = "To deliver your order"
	    inputValueDataDict["permissions"] = permissionList

	    #possibleIntents.append(permissionDict)

	    return {
	        "speech": speech,
	        "displayText": speech,
	        "data": dataJSON,
	        "contextOut": context,
	        "source": "phillips-bot"
	    }
	    '''

	def makePermissionsResultV1(self, speech, context, permissionList):
	    possibleIntents = []

	    permissionDict = {}
	    permissionDict["intent"] = "assistant.intent.actions.PERMISSION"
	    permissionDict["input_value_spec"] = {}

	    inputValueSpecDict = permissionDict["input_value_spec"]
	    inputValueSpecDict["permission_value_spec"] = {}

	    permission_value_spec = inputValueSpecDict["permission_value_spec"]

	    permission_value_spec["optContext"] = "To deliver your order"
	    permission_value_spec["permissions"] = permissionList

	    possibleIntents.append(permissionDict)

	    return {
	        "speech": speech,
	        "displayText": speech,
	        "possibleIntents": possibleIntents,
	        "contextOut": context,
	        "source": "phillips-bot"
	    }


	def compareDeliveryLocation(self):
		devcoords = None
		geoLat = None
		geoLong = None
		if self.requestData.get('originalRequest').get('data').get('device') != None:
			devcoords = self.requestData.get('originalRequest').get('data').get('device').get('location').get('coordinates')
			geoLat = devcoords.get('latitude')
			geoLong = devcoords.get('longitude')
		elif self.requestData.get('originalRequest').get('data').get('postback') != None:
			devcoords = self.requestData.get('originalRequest').get('data').get('postback').get('data')
			geoLat = devcoords.get('lat')
			geoLong = devcoords.get('long')

		print("The latitude is::" + str(geoLat))
		print("The longitude is::" + str(geoLong))

		#Check to see if the permission has already been given
		if geoLat != None:
		    #devcoords = self.requestData.get('originalRequest').get('data').get('device').get('location').get('coordinates')
		    #print("The latitude is::" + str(devcoords.get('latitude')))
		    #print("The longitude is::" + str(devcoords.get('longitude')))
		    print("The latitude is::" + str(geoLat))
		    print("The longitude is::" + str(geoLong))
		    #Code to get the nearest delivery location store
		    #freeDeliverySpeech = self.getFreeDeliveryResponse(devcoords.get('latitude'), devcoords.get('longitude'))
		    freeDeliverySpeech = self.getFreeDeliveryResponse(geoLat, geoLong)
		    '''
		    return {
		        "speech" : "Yes you are at::" + str(devcoords.get('latitude')) + " latitude and " + str(devcoords.get('longitude')) + " longitude"
		    }
		    '''
		    return {
		    	"speech" : freeDeliverySpeech
		    }

		return {
		    "speech" : "Could not get your location"
		}

	def getFreeDeliveryResponse(self, latitude, longitude):
		stores = self.mongo.db.stores
		storeLoc = list(stores.find())
		'''
		for s in storeLoc:
			print ("inside store location store is:" + s["name"])
		storeLocList = list(storeLoc)
		'''
		print("the length of store location is:::" + str(len(storeLoc)))
		locationParserObj = LocationParser()
		locationParserObj.setBaseLocation(latitude, longitude)
		locationParserObj.setObjectLocations(storeLoc)
		nearestStore = locationParserObj.getNNearestLocations(1)
		print("The nearest store distance in kms is:::" + str(nearestStore[0]["distance"]))
		return "Yes you have free delivery since you are only " + str(nearestStore[0]["distance"]) + " km away"
		