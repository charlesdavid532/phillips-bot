class Suggestion(object):
	providers = None
	"""Creates and Returns a suggestion response in JSON format"""
	def __init__(self, provider_name, title):		
		super(Suggestion, self).__init__()
		self.provider_name = provider_name
		self.title = title
		#return self.getSuggestionResponse()

	def getSuggestionResponse(self):
		pass

	def setSuggestionTitle(self, title):
		self.title = title

	def getSuggestionTitle(self):
		return self.title

	@classmethod
	def set_provider_none(self):
		self.providers = None

	@classmethod
	def get_provider(self, provider_name, title):
		if self.providers is None:
			self.providers={}
			for provider_class in self.__subclasses__():
				provider = provider_class(title)
				self.providers[provider.provider_name] = provider
		return self.providers[provider_name]


class GoogleSuggestion(Suggestion):
	"""docstring for GoogleSuggestion"""
	def __init__(self, title):
		super(GoogleSuggestion, self).__init__('google', title)


	def getSuggestionResponse(self):
		suggestionDict = {}
		suggestionDict["title"] = self.title
		return suggestionDict


class FacebookSuggestion(Suggestion):
	"""docstring for FacebookSuggestion"""
	def __init__(self, title):
		super(FacebookSuggestion, self).__init__('facebook', title)
		self.isLocationQuickReply = False

	def setLocationQuickReply(self):
		self.isLocationQuickReply = True


	def getSuggestionResponse(self):
		suggestionDict = {}
		#If condition used in SuggestionChip directly to access instead of via SuggestionList
		if self.isLocationQuickReply == True:
			suggestionDict["content_type"] = "location"
		else:
			suggestionDict["content_type"] = "text"
			suggestionDict["title"] = self.title
			suggestionDict["payload"] = self.title
		return suggestionDict
		
		