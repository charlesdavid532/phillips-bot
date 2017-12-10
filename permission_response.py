from suggestion_list import SuggestionList
from suggestion_chip import SuggestionChip

class PermissionResponse(object):
	providers = None
	"""docstring for PermissionResponse"""
	def __init__(self, provider_name, speech, optContext):
		super(PermissionResponse, self).__init__()
		self.provider_name = provider_name
		self.speech = speech
		self.optContext = optContext
		self.expectedUserResponse = True
		self.outputContext = None
		self.permissionList = []

	def getPermissionResponseJSON(self):
		pass

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
		

	@classmethod
	def set_provider_none(self):
		self.providers = None

	@classmethod
	def get_provider(self, provider_name, speech, optContext):
		if self.providers is None:
			self.providers={}
			for provider_class in self.__subclasses__():
				provider = provider_class(speech, optContext)
				self.providers[provider.provider_name] = provider
		return self.providers[provider_name]


class GooglePermissionResponse(PermissionResponse):
	"""docstring for GooglePermissionResponse"""
	def __init__(self, speech, optContext):
		super(GooglePermissionResponse, self).__init__('google', speech, optContext)
		

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


class FacebookPermissionResponse(PermissionResponse):
	"""docstring for FacebookPermissionResponse"""
	def __init__(self, speech, optContext):
		super(FacebookPermissionResponse, self).__init__('facebook', speech, optContext)
		
	'''
	Intended just for FB location response
	'''
	def getPermissionResponseJSON(self):
		simpleResponse = []
		simpleResponse.append(self.speech)

		SuggestionChip.set_provider_none()
		mySuggestionChip = SuggestionChip.get_provider(self.provider_name, simpleResponse)
		mySuggestionChip.setLocationChip()					

		return mySuggestionChip.getSuggestionChipResponse()