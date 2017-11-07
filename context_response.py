class ContextResponse(object):
	"""This class maintains a single context and returns its JSON for passing to api.ai"""
	def __init__(self, contextName, lifespan):
		super(ContextResponse, self).__init__()
		self.contextName = contextName
		self.lifespan = lifespan
		self.featureList = []

	def addFeature(self, featureName, featureValue):
		self.featureList.append({'featureName':featureName, 'featureValue':featureValue})

	def addCompleteFeatureList(self, featureNameArr, featureValueArr):
		self.featureList = []
		for index in range(0, len(featureNameArr)):
			self.featureList.append({'featureName':featureNameArr[index], 'featureValue':featureValueArr[index]})

	def setContextName(self, contextName):
		self.contextName = contextName

	def getContextName(self):
		return self.contextName

	def setLifespan(self, lifespan):
		self.lifespan = lifespan

	def getLifespan(self):
		return self.lifespan

	def getContextJSON(self):

		outputContextObj ={}
		outputContextObj["name"] = self.contextName
		outputContextObj["lifespan"] = self.lifespan

		contextObj = {}

		for index in range(0, len(self.featureList)):
			contextObj[(self.featureList[index])["featureName"]] = (self.featureList[index])["featureValue"]


		outputContextObj["parameters"] = contextObj

		return outputContextObj


		