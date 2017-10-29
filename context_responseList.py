from context_response import ContextResponse

class ContextResponseList(object):
	"""Holds the entire list of all contexts that are to be passed to api.ai"""
	def __init__(self):
		super(ContextResponseList, self).__init__()
		self.contextList = []


	def addContext(self, context):
		self.contextList.append(context)

	def getContextJSONResponse(self):
		contextResponseJSONList = []

		for index in range(0, len(self.contextList)):
			contextResponseJSONList.append(self.contextList[index].getContextJSON())
			
		return contextResponseJSONList
		