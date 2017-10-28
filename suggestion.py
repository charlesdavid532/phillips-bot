class Suggestion(object):
	"""Creates and Returns a suggestion response in JSON format"""
	def __init__(self, title):
		super(Suggestion, self).__init__()
		self.title = title
		return self.getSuggestionResponse()

	def getSuggestionResponse(self):
		suggestionDict = {}
    	suggestionDict["title"] = self.title
    	return suggestionDict

    def setSuggestionTitle(self, title):
    	self.title = title

    def getSuggestionTitle(self):
    	return self.title
		