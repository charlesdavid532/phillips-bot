class ContextRequest(object):
	"""Controller class for the context that is passed from api.ai"""
	def __init__(self, userContext):
		super(ContextRequest, self).__init__()
		self.userContext = userContext
		self.isContextSet = False


	def getAppropriateUserContext(self, contextName):

		for index in range(0, len(self.userContext)):
		    if self.userContext[index]["name"] == contextName:
		        print("found the right context")
		        self.isContextSet = True
		        return userContext[index]

		# Could not find the right context
		self.isContextSet = False
		return "Context was not found"


	def isContextSet(self):
		return self.isContextSet

		