from suggestion_list import SuggestionList

class Carousel(object):
	"""creates and returns a JSON response for Carousel"""
	def __init__(self, simpleResponse):
		super(Carousel, self).__init__()
		print("Inside carousel")
		self.simpleResponse = simpleResponse
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


	def addCarouselItem(self, key, title, syn, description, imgURL, imgAccText):
		self.keyArr.append(key)
		self.titleArr.append(title)
		self.synArr.append(syn)
		self.descriptionArr.append(description)
		self.imgURLArr.append(imgURL)
		self.imgAccTextArr.append(imgAccText)

	def addCompleteCarouselItem(self, keyArr, titleArr, synArr, descriptionArr, imgURLArr, imgAccTextArr):
		self.keyArr = keyArr
		self.titleArr = titleArr
		self.synArr = synArr
		self.descriptionArr = descriptionArr
		self.imgURLArr = imgURLArr
		self.imgAccTextArr = imgAccTextArr



	def getCarouselItemResponse(self, key, title, syn, description, imgURL, imgAccText):
		carouselItemDict = {}
		carouselItemDict["optionInfo"] = {}

		optionInfoDict = carouselItemDict["optionInfo"]
		optionInfoDict["key"] = key
		optionInfoDict["synonyms"] = []

		synList = optionInfoDict["synonyms"]
		synList.append(syn)

		carouselItemDict["title"] = title
		carouselItemDict["description"] = description

		carouselItemDict["image"] = {}

		imageDict = carouselItemDict["image"]
		imageDict["url"] = imgURL
		imageDict["accessibilityText"] = imgAccText

		return carouselItemDict


	def getInteriorCarouselResponse(self):
		systemIntentDict = {}
		systemIntentDict["intent"] = "actions.intent.OPTION"
		systemIntentDict["data"] = {}

		dataDict = systemIntentDict["data"]
		dataDict["@type"] = "type.googleapis.com/google.actions.v2.OptionValueSpec"
		dataDict["carouselSelect"] = {}

		carouselSelectDict = dataDict["carouselSelect"]

		carouselSelectDict["items"] = []

		itemList = carouselSelectDict["items"]

		for index in range(0, len(self.titleArr)):
			itemList.append(self.getCarouselItemResponse(self.keyArr[index], self.titleArr[index], 
				self.synArr[index], self.descriptionArr[index], self.imgURLArr[index], self.imgAccTextArr[index]))


		return systemIntentDict

	def getCarouselResponse(self):
		carouselResponse = {}
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

		
		carouselResponse["speech"] = self.simpleResponse[0]
		carouselResponse["data"] = {}
		carouselResponse["source"] = "phillips-bot"
		dataDict = carouselResponse["data"]

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

		googleDict["systemIntent"] = self.getInteriorCarouselResponse()

		return carouselResponse