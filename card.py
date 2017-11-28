from suggestion_list import SuggestionList

class Card(object):
	providers = None
	"""creates and returns a JSON response for Card"""
	def __init__(self, provider_name, simpleResponse, formattedText, imgURL, imgAccText):
		super(Card, self).__init__()
		print("In Card Class")
		self.provider_name = provider_name
		self.simpleResponse = simpleResponse
		self.formattedText = formattedText
		self.imgURL = imgURL
		self.imgAccText = imgAccText
		self.hasText = False
		self.hasImage = False
		self.expectedUserResponse = True
		self.title = None
		self.subtitle = None
		self.linkTitle = None
		self.linkUrl = None
		self.outputContext = None
		self.sugTitles = None


		if self.formattedText != '' or self.formattedText != None:
			self.hasText = True


		if self.imgURL != '' or self.imgURL != None:
			self.hasImage = True


		if self.hasImage == False and self.hasText == False:
			print("Does not have text or image")
			#return ''


	def addTitle(self, title):
		self.title = title

	def addSubTitle(self, subtitle):
		self.subtitle = subtitle

	def addLinkBtn(self, linkTitle, linkUrl):
		self.linkTitle = linkTitle
		self.linkUrl = linkUrl

	def addOutputContext(self, outputContext):
		self.outputContext = outputContext

	def addSugTitles(self, sugTitles):
		self.sugTitles = sugTitles

	def removeExpectedUserResponse(self):
		self.expectedUserResponse = False

	def addExpectedUserResponse(self):
		self.expectedUserResponse = True


	def getCardResponse(self):
		pass

	@classmethod
	def get_provider(self, provider_name, simpleResponse, formattedText, imgURL, imgAccText):
		if self.providers is None:
			self.providers={}
			for provider_class in self.__subclasses__():
				provider = provider_class(simpleResponse, formattedText, imgURL, imgAccText)
				self.providers[provider.provider_name] = provider
		return self.providers[provider_name]


class GoogleCard(Card):
	"""docstring for GoogleCard"""
	def __init__(self, simpleResponse, formattedText, imgURL, imgAccText):
		super(GoogleCard, self).__init__('google', simpleResponse, formattedText, imgURL, imgAccText)
		
		

	def getCardResponse(self):
		cardResponse = {}
		itemsDict = {}
		itemsDict["simpleResponse"] = {}
		simpleResponseDict = itemsDict["simpleResponse"]
		simpleResponseDict["textToSpeech"] = self.simpleResponse[0]


		basicCardDict = {}
		basicCardDict["basicCard"] = self.getInteriorCardResponse()

		cardResponse["data"] = {}
		cardResponse["source"] = "phillips-bot"

		#Adding context
		if self.outputContext == None or self.outputContext == "":
			outputContext = []
		else:
			outputContext = self.outputContext
			print("The length of context list in card response is:"+str(len(outputContext)))

		cardResponse["contextOut"] = outputContext

		dataDict = cardResponse["data"]
		dataDict["google"] = {}
		googleDict = dataDict["google"]

		googleDict["expect_user_response"] = self.expectedUserResponse
		googleDict["rich_response"] = {}


		richResponseDict = googleDict["rich_response"]
		richResponseDict["items"] = []

		itemList = richResponseDict["items"]
		itemList.append(itemsDict)
		itemList.append(basicCardDict)

		if len(self.simpleResponse) > 1:
			secondItemsDict = {}
			secondItemsDict["simpleResponse"] = {}
			secondSimpleResponseDict = secondItemsDict["simpleResponse"]
			secondSimpleResponseDict["textToSpeech"] = simpleResponse[1]
			itemList.append(secondItemsDict)


		if self.sugTitles != "" and self.sugTitles != None:
			mySuggestionList = SuggestionList(self.sugTitles)
			mySuggestionList.setSource(self.provider_name)
			richResponseDict["suggestions"] = mySuggestionList.getSuggestionListResponse()



		return cardResponse



	def getInteriorCardResponse(self):
		basicCard = {}

		if self.title != "" and self.title != None:
			basicCard["title"] = self.title


		if self.hasText == True:
			basicCard["formattedText"] = self.formattedText

		if self.subtitle != "" and self.subtitle != None:
			basicCard["subtitle"] = self.subtitle

		if self.hasImage == True:
			basicCard["image"] = {}

			imageDict = basicCard["image"]
			imageDict["url"] = self.imgURL
			imageDict["accessibilityText"] = self.imgAccText


		if self.linkTitle != '' and self.linkTitle != None and self.linkTitle != []:
			basicCard["buttons"] = []

			buttonsList = basicCard["buttons"]
			buttonsList.append(self.getButtonResponse())

		return basicCard



	def getButtonResponse(self):
		btnDict = {}

		btnDict["title"] = self.linkTitle
		btnDict["openUrlAction"] = {}

		openUrlActionDict = btnDict["openUrlAction"]
		openUrlActionDict["url"] = self.linkUrl

		return btnDict





class FacebookCard(Card):
	"""docstring for FacebookCard"""
	def __init__(self, simpleResponse, formattedText, imgURL, imgAccText):
		super(FacebookCard, self).__init__('facebook', simpleResponse, formattedText, imgURL, imgAccText)


	def getCardResponse(self):
		cardResponse = {}

		itemsDict = {}
		itemsDict["simpleResponse"] = {}
		simpleResponseDict = itemsDict["simpleResponse"]
		simpleResponseDict["textToSpeech"] = self.simpleResponse[0]

		cardResponse["data"] = {}
		cardResponse["source"] = "phillips-bot"

		#Adding context
		if self.outputContext == None or self.outputContext == "":
			outputContext = []
		else:
			outputContext = self.outputContext
			print("The length of context list in card response is:"+str(len(outputContext)))

		cardResponse["contextOut"] = outputContext

		dataDict = cardResponse["data"]
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
		elementsPayload.append(self.getInteriorCardResponse())


		#Attaching the response
		facebookDict["rich_response"] = {}


		richResponseDict = facebookDict["rich_response"]
		richResponseDict["items"] = []

		itemList = richResponseDict["items"]
		itemList.append(itemsDict)

		if len(self.simpleResponse) > 1:
			secondItemsDict = {}
			secondItemsDict["simpleResponse"] = {}
			secondSimpleResponseDict = secondItemsDict["simpleResponse"]
			secondSimpleResponseDict["textToSpeech"] = simpleResponse[1]
			itemList.append(secondItemsDict)

		if self.sugTitles != "" and self.sugTitles != None:
			mySuggestionList = SuggestionList(self.sugTitles)
			mySuggestionList.setSource(self.provider_name)
			#messageFacebook["quick_replies"] = mySuggestionList.getSuggestionListResponse()
			facebookDict["quick_replies"] = mySuggestionList.getSuggestionListResponse()



		return cardResponse



	def getInteriorCardResponse(self):
		basicCard = {}

		if self.title != "" and self.title != None:
			basicCard["title"] = self.title

		'''
		if self.hasText == True:
			basicCard["formattedText"] = self.formattedText
		'''

		#Note: Added the formatted text to the subtitle
		if self.subtitle != "" and self.subtitle != None and self.hasText == True:
			basicCard["subtitle"] = self.subtitle + '' + self.formattedText
		elif self.hasText == True:
			basicCard["subtitle"] = self.formattedText
		elif self.subtitle != "" and self.subtitle != None:
			basicCard["subtitle"] = self.subtitle

		if self.hasImage == True:
			basicCard["image_url"] = self.imgURL			


		if self.linkTitle != '' and self.linkTitle != None and self.linkTitle != []:
			basicCard["buttons"] = []

			buttonsList = basicCard["buttons"]
			buttonsList.append(self.getButtonResponse())

		return basicCard



	def getButtonResponse(self):
		btnDict = {}

		#Note: By Default added the button as web_url. This can also be a postback button
		btnDict["type"] = "web_url"
		btnDict["title"] = self.linkTitle
		btnDict["url"] = self.linkUrl

		return btnDict