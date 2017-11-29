from suggestion_list import SuggestionList

class SuggestionChip(object):
	providers = None
	"""docstring for SuggestionChip"""
	def __init__(self, provider_name, simpleResponse):
		super(SuggestionChip, self).__init__()
		print("Inside Suggestion Chip")
		self.provider_name = provider_name
		self.simpleResponse = simpleResponse
		self.expectedUserResponse = True
		self.sugTitles = None
		self.outputContext = None
		self.linkOutSuggestion = None

	def addSugTitles(self, sugTitles):
		self.sugTitles = sugTitles

	def addLinkOutSuggestion(self, destinationName, url):
		self.linkOutSuggestion = {}
		self.linkOutSuggestion["destinationName"] = destinationName
		self.linkOutSuggestion["url"] = url

	def addOutputContext(self, outputContext):
		self.outputContext = outputContext

	def getSuggestionChipResponse(self):
		pass


	@classmethod
	def set_provider_none(self):
		self.providers = None

	@classmethod
	def get_provider(self, provider_name, simpleResponse):
		if self.providers is None:
			self.providers={}
			for provider_class in self.__subclasses__():
				provider = provider_class(simpleResponse)
				self.providers[provider.provider_name] = provider
		return self.providers[provider_name]


class GoogleSuggestionChip(SuggestionChip):
	"""docstring for GoogleSuggestionChip"""
	def __init__(self, simpleResponse):
		super(GoogleSuggestionChip, self).__init__('google', simpleResponse)

	def getSuggestionChipResponse(self):
		suggestionChipResponse = {}

		suggestionChipResponse["speech"] = self.simpleResponse[0]
		suggestionChipResponse["data"] = {}
		suggestionChipResponse["source"] = "flobot"
		dataDict = suggestionChipResponse["data"]

		dataDict["google"] = {}
		googleDict = dataDict["google"]

		googleDict["expect_user_response"] = self.expectedUserResponse
		googleDict["rich_response"] = {}


		richResponseDict = googleDict["rich_response"]
		richResponseDict["items"] = []


		itemList = richResponseDict["items"]
		

		itemsDict = {}
		itemsDict["simpleResponse"] = {}
		simpleResponseDict = itemsDict["simpleResponse"]
		simpleResponseDict["textToSpeech"] = self.simpleResponse[0]

		itemList.append(itemsDict)

		#Code to add multiple simple responses (Seems unwieldy & needs to be better done for a loop)
		for i in range(1, len(self.simpleResponse)):
			itemsDict1 = {}
			itemsDict1["simpleResponse"] = {}
			simpleResponseDict1 = itemsDict1["simpleResponse"]
			simpleResponseDict1["textToSpeech"] = self.simpleResponse[i]
			itemList.append(itemsDict1)

		if self.sugTitles != "" and self.sugTitles != None:
			mySuggestionList = SuggestionList(self.sugTitles)
			mySuggestionList.setSource(self.provider_name)
			richResponseDict["suggestions"] = mySuggestionList.getSuggestionListResponse()


		#Adding link out suggestion
		if self.linkOutSuggestion != "" and self.linkOutSuggestion != None:
			richResponseDict["linkOutSuggestion"] = self.linkOutSuggestion


		#googleDict["systemIntent"] = self.getInteriorCarouselResponse()

		#Adding the context
		#Adding context
		if self.outputContext == None or self.outputContext == "":
			outputContext = []
		else:
			outputContext = self.outputContext
			print("The length of context list in card response is:"+str(len(outputContext)))

		suggestionChipResponse["contextOut"] = outputContext

		return suggestionChipResponse


class FacebookSuggestionChip(SuggestionChip):
	"""docstring for FacebookSuggestionChip"""
	def __init__(self, simpleResponse):
		super(FacebookSuggestionChip, self).__init__('facebook', simpleResponse)

	def getButtonResponse(self, linkTitle, linkUrl):
		btnDict = {}

		#Note: By Default added the button as web_url. This can also be a postback button
		btnDict["type"] = "web_url"
		btnDict["title"] = linkTitle
		btnDict["url"] = linkUrl

		return btnDict
		

	def getSuggestionChipResponse(self):
		suggestionChipResponse = {}


		suggestionChipResponse["data"] = {}
		suggestionChipResponse["source"] = "phillips-bot"
		suggestionChipResponse["speech"] = self.simpleResponse[0]
		suggestionChipResponse["displayText"] = self.simpleResponse[0]

		#Adding context
		if self.outputContext == None or self.outputContext == "":
			outputContext = []
		else:
			outputContext = self.outputContext
			print("The length of context list in card response is:"+str(len(outputContext)))

		suggestionChipResponse["contextOut"] = outputContext

		dataDict = suggestionChipResponse["data"]
		dataDict["facebook"] = {}
		facebookDict = dataDict["facebook"]

		facebookDict["text"] = self.simpleResponse[0]

		#Adding link out suggestion
		if self.linkOutSuggestion != "" and self.linkOutSuggestion != None:
			facebookDict["buttons"] = []
			buttonsFB = facebookDict["buttons"]
			buttonsFB.append(self.getButtonResponse(self.linkOutSuggestion["destinationName"], self.linkOutSuggestion["url"]))


		if self.sugTitles != "" and self.sugTitles != None:
			mySuggestionList = SuggestionList(self.sugTitles)
			mySuggestionList.setSource(self.provider_name)
			#messageFacebook["quick_replies"] = mySuggestionList.getSuggestionListResponse()
			facebookDict["quick_replies"] = mySuggestionList.getSuggestionListResponse()


		return suggestionChipResponse


		