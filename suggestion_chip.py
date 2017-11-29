from suggestion_list import SuggestionList

class SuggestionChip(object):
	"""docstring for SuggestionChip"""
	def __init__(self, simpleResponse):
		super(SuggestionChip, self).__init__()
		print("Inside Suggestion Chip")
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
		