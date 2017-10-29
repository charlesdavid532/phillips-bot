class ContextRequest(object):
	"""Controller class for the context that is passed from api.ai"""
	def __init__(self, userContext):
		super(ContextRequest, self).__init__()
		self.userContext = userContext


	def getAppropriateUserContext(self, contextName):

		for index in range(0, len(self.userContext)):
		    if self.userContext[index]["name"] == contextName:
		        print("found the right context")
		        return userContext[index]

		# Could not find the right context
		return "Context was not found"
		