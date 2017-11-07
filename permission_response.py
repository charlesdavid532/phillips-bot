class PermissionResponse(object):
	"""docstring for PermissionResponse"""
	def __init__(self, speech, optContext):
		super(PermissionResponse, self).__init__()
		self.speech = speech
		self.optContext = optContext
		self.expectedUserResponse = True
		self.permissionList = []

	def getPermissionResponseJSON(self):

		permissionJSON = {}
		permissionJSON["speech"] = self.speech
		permissionJSON["displayText"] = self.speech
		permissionJSON["data"] = {}

		dataJSON = permissionJSON["data"]
	    dataJSON["google"] = {}
	    googleJSON = dataJSON["google"]

	    googleJSON["expectUserResponse"] = self.expectedUserResponse
	    googleJSON["systemIntent"] = {}

	    #possibleIntents = []

	    permissionDict = googleJSON["systemIntent"]
	    permissionDict["intent"] = "actions.intent.PERMISSION"
	    permissionDict["data"] = {}

	    inputValueDataDict = permissionDict["data"]
	    inputValueDataDict["@type"] = "type.googleapis.com/google.actions.v2.PermissionValueSpec"
	    inputValueDataDict["optContext"] = self.optContext
	    inputValueDataDict["permissions"] = self.permissionList

	    #Adding context
		if self.outputContext == None or self.outputContext == "":
			outputContext = []
		else:
			outputContext = self.outputContext
			print("The length of context list in permission response is:"+str(len(outputContext)))

	    #possibleIntents.append(permissionDict)
	    permissionJSON["contextOut"] = outputContext
	    permissionJSON["source"] = "phillips-bot"

	    return permissionJSON

	def addOutputContext(self, outputContext):
		self.outputContext = outputContext


	def removeExpectedUserResponse(self):
		self.expectedUserResponse = False

	def addExpectedUserResponse(self):
		self.expectedUserResponse = True

	def addNamePermission(self):
		self.permissionList.append("NAME")

	def addPreciseLocationPermission(self):
		self.permissionList.append("DEVICE_PRECISE_LOCATION")
		