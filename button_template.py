from suggestion_list import SuggestionList

class ButtonTemplate(object):
	"""docstring for ButtonTemplate"""
	def __init__(self):
		super(ButtonTemplate, self).__init__()
		self.text = None
		self.sugTitles = None
		self.outputContext = None
		self.source = None
		self.btnArr = []

	def addText(self, text):
		self.text = text

	def addSugTitles(self, sugTitles):
		self.sugTitles = sugTitles

	def addOutputContext(self, outputContext):
		self.outputContext = outputContext

	def setSource(self, source):
		self.source = source

	def addLinkButton(self, title, url):
		linkBtn = {}
		linkBtn["type"] = "web_url"
		linkBtn["url"] = url
		linkBtn["title"] = title
		self.btnArr.append(linkBtn)

	def addPostbackButton(self, title, postback):
		postbackBtn = {}
		postbackBtn["type"] = "postback"
		postbackBtn["title"] = title
		postbackBtn["postback"] = postback
		self.btnArr.append(postbackBtn)

	def getButtonTemplateJSON(self):
		btnResponse = {}


		btnResponse["data"] = {}
		btnResponse["source"] = "phillips-bot"

		#Adding context
		if self.outputContext == None or self.outputContext == "":
			outputContext = []
		else:
			outputContext = self.outputContext
			print("The length of context list in card response is:"+str(len(outputContext)))

		btnResponse["contextOut"] = outputContext

		dataDict = btnResponse["data"]
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
		payload["template_type"] = "button"

		if self.text != None and self.text != '':
			payload["text"] = self.text

		
		payload["buttons"] = self.btnArr	




		if self.sugTitles != "" and self.sugTitles != None:
			mySuggestionList = SuggestionList(self.sugTitles)
			mySuggestionList.setSource(self.source)
			#messageFacebook["quick_replies"] = mySuggestionList.getSuggestionListResponse()
			facebookDict["quick_replies"] = mySuggestionList.getSuggestionListResponse()



		return btnResponse

		