from permission_response import PermissionResponse
class FreeDeliveryController(object):
	"""docstring for FreeDeliveryController"""
	def __init__(self, requestData, mongo):
		super(FreeDeliveryController, self).__init__()
		self.requestData = requestData
		self.mongo = mongo
		self.isPermissionGiven = False


	def setIsPermissionGiven(self, isPermissionGiven):
		self.isPermissionGiven = isPermissionGiven

	def getIsPermissionGiven(self):
		return self.isPermissionGiven

	def getPermissionJSON(self):
		speech = self.parseFreeDeliveryRequest()
		return self.makePermissionsResult(speech["speech"], []) 



	def parseFreeDeliveryRequest(self):
	    
		return {
		    "speech" : "I need access to your device location to perform this task"
		}

	def makePermissionsResult(self, speech, context):

		permissionResObj = PermissionResponse(speech, "To deliver your order")
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
		#Check to see if the permission has already been given
		if self.requestData.get('originalRequest').get('data').get('device') != None:
		    devcoords = self.requestData.get('originalRequest').get('data').get('device').get('location').get('coordinates')
		    print("The latitude is::" + str(devcoords.get('latitude')))
		    print("The longitude is::" + str(devcoords.get('longitude')))
		    return {
		        "speech" : "Yes you are at::" + str(devcoords.get('latitude')) + " latitude and " + str(devcoords.get('longitude')) + " longitude"
		    }

		return {
		    "speech" : "Could not get your location"
		}
		