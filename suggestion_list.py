from suggestion import Suggestion

class SuggestionList(object):
	"""Creates and Returns a suggestion list response in SuggestionList"""
	def __init__(self, titleList):
		super(SuggestionList, self).__init__()
		self.titleList = titleList
		return self.getSuggestionListResponse()

	def getSuggestionListResponse(self):
		suggestionList = []
		for index in range(0, len(titleList)):
			suggestionList.append(Suggestion(titleList[index]))

		return suggestionList
		