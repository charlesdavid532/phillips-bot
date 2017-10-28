from suggestion_list import SuggestionList

class List(object):
	"""creates and returns a JSON response for List"""
	def __init__(self, simpleResponse):
		super(List, self).__init__()
		self.simpleResponse = simpleResponse
		self.listTitle = None
		self.expectedUserResponse = True
		self.sugTitles = None
		self.keyArr = []
		self.titleArr = []
		self.synArr = []
		self.descriptionArr = []
		self.imgURLArr = []
		self.imgAccTextArr = []



	def removeExpectedUserResponse(self):
		self.expectedUserResponse = False

	def addExpectedUserResponse(self):
		self.expectedUserResponse = True

	def addSugTitles(self, sugTitles):
		self.sugTitles = sugTitles

	def addListTitle(self, listTitle):
		self.listTitle = listTitle

	def addListItem(self, key, title, syn, description, imgURL, imgAccText):
		self.keyArr.append(key)
		self.titleArr.append(title)
		self.synArr.append(syn)
		self.descriptionArr.append(description)
		self.imgURLArr.append(imgURL)
		self.imgAccTextArr.append(imgAccText)

	def addCompleteListItem(self, keyArr, titleArr, synArr, descriptionArr, imgURLArr, imgAccTextArr):
		self.keyArr = keyArr
		self.titleArr = titleArr
		self.synArr = synArr
		self.descriptionArr = descriptionArr
		self.imgURLArr = imgURLArr
		self.imgAccTextArr = imgAccTextArr

	def getListItemResponse(self, key, title, syn, description, imgURL, imgAccText):
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
		imageDict["accessibilityText"] = imgAccText

		return listItemDict

	def getInteriorListResponse(self):
		systemIntentDict = {}
		systemIntentDict["intent"] = "actions.intent.OPTION"
		systemIntentDict["data"] = {}

		dataDict = systemIntentDict["data"]
		dataDict["@type"] = "type.googleapis.com/google.actions.v2.OptionValueSpec"
		dataDict["listSelect"] = {}

		listSelectDict = dataDict["listSelect"]

		if self.listTitle != "" and self.listTitle != None:
			listSelectDict["title"] = self.listTitle

		listSelectDict["items"] = []

		itemList = listSelectDict["items"]

		for index in range(0, len(self.titleArr)):
			itemList.append(self.getListItemResponse(self.keyArr[index], self.titleArr[index], 
				self.synArr[index], self.descriptionArr[index], self.imgURLArr[index], self.imgAccTextArr[index]))


		return systemIntentDict


	def getListResponse(self):
		listResponse = {}
		itemsDict = {}
		itemsDict["simpleResponse"] = {}
		simpleResponseDict = itemsDict["simpleResponse"]
		simpleResponseDict["textToSpeech"] = self.simpleResponse[0]

		#Code to add multiple simple responses (Seems unwieldy & needs to be better done for a loop)
		if len(self.simpleResponse) > 1:
			itemsDict1 = {}
			itemsDict1["simpleResponse"] = {}
			simpleResponseDict1 = itemsDict1["simpleResponse"]
			simpleResponseDict1["textToSpeech"] = self.simpleResponse[1]

		
		listResponse["data"] = {}
		listResponse["source"] = "phillips-bot"
		dataDict = listResponse["data"]

		dataDict["google"] = {}
		googleDict = dataDict["google"]

		googleDict["expect_user_response"] = self.expectedUserResponse
		googleDict["rich_response"] = {}


		richResponseDict = googleDict["rich_response"]
		richResponseDict["items"] = []


		itemList = richResponseDict["items"]
		itemList.append(itemsDict)

		if len(self.simpleResponse) > 1:
		    itemList.append(itemsDict1)



		if self.sugTitles != "" and self.sugTitles != None:
			mySuggestionList = SuggestionList(self.sugTitles)
			richResponseDict["suggestions"] = mySuggestionList.getSuggestionListResponse()

		googleDict["systemIntent"] = self.getInteriorListResponse()

		return listResponse