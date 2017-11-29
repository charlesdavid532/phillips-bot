from suggestion_list import SuggestionList

class Carousel(object):
	providers = None
	"""creates and returns a JSON response for Carousel"""
	def __init__(self, provider_name, simpleResponse):
		super(Carousel, self).__init__()
		print("Inside carousel")
		self.provider_name = provider_name
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



	

	def getCarouselResponse(self):
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


class GoogleCarousel(Carousel):
	"""docstring for GoogleCarousel"""
	def __init__(self, simpleResponse):
		super(GoogleCarousel, self).__init__('google', simpleResponse)


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
			mySuggestionList.setSource(self.provider_name)
			richResponseDict["suggestions"] = mySuggestionList.getSuggestionListResponse()

		googleDict["systemIntent"] = self.getInteriorCarouselResponse()

		return carouselResponse
		

class FacebookCarousel(Carousel):
	"""docstring for FacebookCarousel"""
	def __init__(self, simpleResponse):
		super(FacebookCarousel, self).__init__('facebook', simpleResponse)


	def getInteriorCarouselResponse(self, key, title, syn, description, imgURL, imgAccText):
		basicCarousel = {}

		if title != "" and title != None:
			basicCarousel["title"] = title

		'''
		if self.hasText == True:
			basicCard["formattedText"] = self.formattedText
		'''

		#Note: Added the formatted text to the subtitle
		if description != "" and description != None:
			basicCarousel["subtitle"] = description

		if imgURL != "" and imgURL != None:
			basicCarousel["image_url"] = imgURL			


		
		basicCarousel["buttons"] = []

		buttonsList = basicCarousel["buttons"]

		#Adding the default btn type
		#buttonsList.append(self.getButtonResponse("postback", title, "", key))
		buttonsList.append(self.getButtonResponse("postback", "Tap to view", "", key))

		return basicCarousel



	def getButtonResponse(self, btntype, title, url, payload):
		btnDict = {}

		#Note: By Default added the button as web_url. This can also be a postback button
		btnDict["type"] = btntype
		btnDict["title"] = title

		if btntype == "web_url":
			btnDict["url"] = url
		elif btntype == "postback":
			btnDict["payload"] = payload

		return btnDict


	def getCarouselResponse(self):
		carouselResponse = {}


		carouselResponse["data"] = {}
		carouselResponse["source"] = "phillips-bot"

		#Adding context
		'''
		if self.outputContext == None or self.outputContext == "":
			outputContext = []
		else:
			outputContext = self.outputContext
			print("The length of context list in card response is:"+str(len(outputContext)))

		carouselResponse["contextOut"] = outputContext
		'''
		
		dataDict = carouselResponse["data"]
		dataDict["facebook"] = {}
		facebookDict = dataDict["facebook"]


		#facebookDict["message"] = {}

		#messageFacebook = facebookDict["message"]
		#messageFacebook["attachment"] = {}
		facebookDict["attachment"] = {}

		#attachmentMessage = messageFacebook["attachment"]
		attachmentMessage = facebookDict["attachment"]
		attachmentMessage["type"] = "template"
		attachmentMessage["payload"] = {}

		payload = attachmentMessage["payload"]
		payload["template_type"] = "generic"
		payload["elements"] = []

		elementsPayload = payload["elements"]

		#Adding a loop to append all elements
		for index in range(0, len(self.titleArr)):
			elementsPayload.append(self.getInteriorCarouselResponse(self.keyArr[index], self.titleArr[index], 
				self.synArr[index], self.descriptionArr[index], self.imgURLArr[index], self.imgAccTextArr[index]))
		#elementsPayload.append(self.getInteriorCardResponse())




		if self.sugTitles != "" and self.sugTitles != None:
			mySuggestionList = SuggestionList(self.sugTitles)
			mySuggestionList.setSource(self.provider_name)
			#messageFacebook["quick_replies"] = mySuggestionList.getSuggestionListResponse()
			facebookDict["quick_replies"] = mySuggestionList.getSuggestionListResponse()



		return carouselResponse