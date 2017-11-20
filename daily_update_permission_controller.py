class DailyUpdatePermissionController(object):
	"""docstring for DailyUpdatePermissionController"""
	def __init__(self):
		super(DailyUpdatePermissionController, self).__init__()
		self.intentName = None
		self.resultText = None

	def setIntentName(self, intentName):
		self.intentName = intentName


	def getInteriorRequestPermissionResponse(self):
		systemIntentDict = {}
		systemIntentDict["intent"] = "actions.intent.REGISTER_UPDATE"
		systemIntentDict["data"] = {}

		dataDict = systemIntentDict["data"]
		dataDict["@type"] = "type.googleapis.com/google.actions.v2.RegisterUpdateValueSpec"
		dataDict["intent"] = self.intentName
		dataDict["updateContextValueSpec"] = {}

		updateContextValueSpecDict = dataDict["updateContextValueSpec"]
		updateContextValueSpecDict["timeContext"] = {}

		timeContextDict = updateContextValueSpecDict["timeContext"]
		timeContextDict["frequency"] = "DAILY"

		return systemIntentDict

	def getRequestPermissionJSON(self):
		dailyUpdatePermissionResponse = {}	

		
		dailyUpdatePermissionResponse["speech"] = "Some dummy speech"
		dailyUpdatePermissionResponse["data"] = {}
		#carouselResponse["source"] = "phillips-bot"
		dataDict = dailyUpdatePermissionResponse["data"]

		dataDict["google"] = {}
		googleDict = dataDict["google"]

		

		googleDict["systemIntent"] = self.getInteriorRequestPermissionResponse()

		return dailyUpdatePermissionResponse
		
	def setResultText(self, resultText):
		self.resultText = resultText

	def getResultPermissionJSON(self):
		return self.resultText