from suggestion import Suggestion

class SuggestionList(object):
	"""Creates and Returns a suggestion list response in SuggestionList"""
	def __init__(self, titleList):
		super(SuggestionList, self).__init__()
		self.titleList = titleList
		#return self.getSuggestionListResponse()

	def setSource(self, source):
		self.source = source

	def getSuggestionListResponse(self):
		suggestionList = []
		
		for index in range(0, len(self.titleList)):
			#mySuggestion = Suggestion(self.titleList[index])
			Suggestion.set_provider_none()
			mySuggestion = Suggestion.get_provider(self.source, self.titleList[index])
			print("The suggestion title is::" + str(self.titleList[index]))
			print("The suggestion response is::" + str(mySuggestion.getSuggestionResponse()))
			suggestionList.append(mySuggestion.getSuggestionResponse())

		return suggestionList
		