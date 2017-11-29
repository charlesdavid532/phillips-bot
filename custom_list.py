from suggestion_list import SuggestionList

class List(object):
	providers = None
	"""creates and returns a JSON response for List"""
	def __init__(self, provider_name, simpleResponse):
		super(List, self).__init__()
		print("Inside custom list")
		self.provider_name = provider_name
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


	def getListResponse(self):
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


class GoogleList(List):
	"""docstring for GoogleList"""
	def __init__(self, arg):
		super(GoogleList, self).__init__('google', simpleResponse)


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


class FacebookList(List):
	"""docstring for FacebookList"""
	def __init__(self, arg):
		super(FacebookList, self).__init__('facebook', simpleResponse)


	def getInteriorListResponse(self, key, title, syn, description, imgURL, imgAccText):
		basicList = {}

		if title != "" and title != None:
			basicList["title"] = title

		'''
		if self.hasText == True:
			basicCard["formattedText"] = self.formattedText
		'''

		#Note: Added the formatted text to the subtitle
		if description != "" and description != None:
			basicList["subtitle"] = description

		if imgURL != "" and imgURL != None:
			basicList["image_url"] = imgURL			


		
		basicList["buttons"] = []

		buttonsList = basicList["buttons"]

		#Adding the default btn type
		#buttonsList.append(self.getButtonResponse("postback", title, "", key))
		buttonsList.append(self.getButtonResponse("postback", "Tap to view", "", key))

		return basicList



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


	def getListResponse(self):
		listResponse = {}


		listResponse["data"] = {}
		listResponse["source"] = "phillips-bot"

		#Adding context
		'''
		if self.outputContext == None or self.outputContext == "":
			outputContext = []
		else:
			outputContext = self.outputContext
			print("The length of context list in card response is:"+str(len(outputContext)))

		carouselResponse["contextOut"] = outputContext
		'''
		
		dataDict = listResponse["data"]
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
		payload["template_type"] = "list"
		payload["top_element_style"] = "compact"
		payload["elements"] = []

		elementsPayload = payload["elements"]

		#Adding a loop to append all elements
		for index in range(0, len(self.titleArr)):
			elementsPayload.append(self.getInteriorListResponse(self.keyArr[index], self.titleArr[index], 
				self.synArr[index], self.descriptionArr[index], self.imgURLArr[index], self.imgAccTextArr[index]))
		#elementsPayload.append(self.getInteriorCardResponse())




		if self.sugTitles != "" and self.sugTitles != None:
			mySuggestionList = SuggestionList(self.sugTitles)
			mySuggestionList.setSource(self.provider_name)
			#messageFacebook["quick_replies"] = mySuggestionList.getSuggestionListResponse()
			facebookDict["quick_replies"] = mySuggestionList.getSuggestionListResponse()



		return listResponse
		