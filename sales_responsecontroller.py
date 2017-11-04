from constants import Constants
class SalesResponseController(object):
	"""Class SalesResponseController creates the text response which is used to display the sales response as a simple response"""
	def __init__(self, userParameters, salesRev, period):
		super(SalesResponseController, self).__init__()
		self.userParameters = userParameters		
		self.salesRev = salesRev
		self.period = period
		self.removeIsContext()


	def setIsContext(self, contextParameters):
		self.isContext = True
		self.contextParameters = contextParameters

	def removeIsContext(self):
		self.isContext = False
		self.contextParameters = None

	def getIsContext(self):
		return self.isContext


	def getSalesResponseStr(self):
		if self.getIsContext() == False:
			return self.generateResponseForSales(self.userParameters)
		else:
			return self.generateContextResponseForSales(self.userParameters, self.contextParameters)




	def generateContextResponseForSales(userParameters, contextParameters):

		if self.salesRev == "":
			return "There was an error while querying the data and it returned null sales revenue"

		resStr = "The sales revenue of "

		#Here there should be product
		resStr += self.generateContextResponseForProduct(userParameters, contextParameters)

		#Here there should be region
		resStr += " for " + self.generateContextResponseForRegion(userParameters, contextParameters)

		#Here there should be date/period
		resStr += " " + self.generateContextResponseForPeriod(userParameters, contextParameters, self.period)

		#Adding the amount
		resStr += " is: " + str(self.salesRev)

		return resStr


	'''
	Returns a string which will be sent as response to the user when he/she queries for sales data

	'''
	def generateResponseForSales(userParameters):
	    
		if self.salesRev == "":
			return "There was an error while querying the data and it returned null sales revenue"

		resStr = "The sales revenue of "

		#Here there should be product
		resStr += self.generateResponseForProduct(userParameters)


		#Here there should be region
		resStr += " for " + self.generateResponseForRegion(userParameters)

		#Here there should be date/period
		resStr += " " + self.generateResponseForPeriod(userParameters, self.period)

		#Adding the amount
		resStr += " is: " + str(self.salesRev)

		return resStr


	'''
	Returns either the requested product name or the default product name
	'''
	def generateContextResponseForProduct(parameters, contextParameters):
		resStr = ""

		if parameters.get('product') != None and parameters.get('product') != "":
	    	resStr += parameters.get('product')
		elif contextParameters.get('context-product') != None and contextParameters.get('context-product') != "":
	    	resStr += contextParameters.get('context-product')
		else:
	    	resStr += Constants.getStrDefaultProduct()

		return resStr

	'''
	Returns either the requested product name or the default product name
	'''
	def generateResponseForProduct(parameters):
		resStr = ""

		if parameters.get('product') != None and parameters.get('product') != "":
			resStr += parameters.get('product')
		else:
			resStr += Constants.getStrDefaultProduct()

		return resStr


	'''
	Should return either the city or the state or the region or the default that the user has requested
	'''
	def generateContextResponseForRegion(parameters, contextParameters):
		resStr = ""

		if parameters.get('geo-city-us') != None and parameters.get('geo-city-us') != "" and parameters.get('geo-city-us') != []:
			resStr = parameters.get('geo-city-us')
		elif parameters.get('geo-city') != None and parameters.get('geo-city') != "" and parameters.get('geo-city') != []:
			resStr = parameters.get('geo-city')
		elif parameters.get('geo-state-us') != None and parameters.get('geo-state-us') != "" and parameters.get('geo-state-us') != []:
			resStr = parameters.get('geo-state-us')
		elif parameters.get('region') != None and parameters.get('region') != "":
			resStr = parameters.get('region')
		elif contextParameters.get('context-geo-city-us') != None and contextParameters.get('context-geo-city-us') != "" and contextParameters.get('context-geo-city-us') != []:
			resStr = contextParameters.get('context-geo-city-us') 
		elif contextParameters.get('context-geo-state-us') != None and contextParameters.get('context-geo-state-us') != "" and contextParameters.get('context-geo-state-us') != []:
			resStr = contextParameters.get('context-geo-state-us')    
		elif contextParameters.get('context-region') != None and contextParameters.get('context-region') != "":
			resStr = contextParameters.get('context-region')
		else:
			resStr = Constants.getStrDefaultRegion()

		return resStr

	'''
	Should return either the city or the state or the region or the default that the user has requested
	'''
	def generateResponseForRegion(parameters):
		resStr = ""

		if parameters.get('geo-city-us') != None and parameters.get('geo-city-us') != "" and parameters.get('geo-city-us') != []:
			resStr = parameters.get('geo-city-us')
		elif parameters.get('geo-city') != None and parameters.get('geo-city') != "" and parameters.get('geo-city') != []:
			resStr = parameters.get('geo-city')
		elif parameters.get('geo-state-us') != None and parameters.get('geo-state-us') != "" and parameters.get('geo-state-us') != []:
			resStr = parameters.get('geo-state-us')
		elif parameters.get('region') != None and parameters.get('region') != "":
			resStr = parameters.get('region')
		else:
			resStr = Constants.getStrDefaultRegion()

		return resStr


	def generateContextResponseForPeriod(parameters, contextParameters, period):
		resStr = ""
		startDate = period["startDate"]
		endDate = period["endDate"]
		userPeriod = parameters.get('period')
		contextPeriod = contextParameters.get('context-period')

		if userPeriod == "" and contextPeriod == "":
			resStr += "in the duration between " + Constants.getStrDefaultStartDate() + " and " + Constants.getStrDefaultEndDate()
		elif userPeriod != None and userPeriod != "" and userPeriod.get('date') != None and userPeriod.get('date') != "":
			resStr += "on " + startDate
		elif userPeriod != None and userPeriod != "" and userPeriod.get('date-period') != None and userPeriod.get('date-period') != "":
			resStr += "in the duration between " + startDate + " and " + endDate
		elif contextPeriod != None and contextPeriod != "" and contextPeriod.get('date') != None and contextPeriod.get('date') != "":
			resStr += "on " + startDate    
		elif contextPeriod != None and contextPeriod != "" and contextPeriod.get('date-period') != None and contextPeriod.get('date-period') != "":
			resStr += "in the duration between " + startDate + " and " + endDate
		else:
			# TODO: Include default date
			resStr += "in the duration between " + Constants.getStrDefaultStartDate() + " and " + Constants.getStrDefaultEndDate()

		return resStr


	def generateResponseForPeriod(parameters, period):
		resStr = ""
		startDate = period["startDate"]
		endDate = period["endDate"]
		userPeriod = parameters.get('period')

		if userPeriod == "":
			resStr += "in the duration between " + Constants.getStrDefaultStartDate() + " and " + Constants.getStrDefaultEndDate()
		elif userPeriod.get('date') != None:
			resStr += "on " + startDate
		elif userPeriod.get('date-period') != None:
			resStr += "in the duration between " + startDate + " and " + endDate
		else:
			# TODO: Include default date
			resStr += "in the duration between " + Constants.getStrDefaultStartDate() + " and " + Constants.getStrDefaultEndDate()

		return resStr
		