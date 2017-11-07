from constants import Constants
from datetime import datetime as dt
class Parser(object):
	"""Parses the request from the main controller"""
	def __init__(self, mongo):
		super(Parser, self).__init__()
		self.userParameters = None
		self.contextParameters = None
		self.mongo = mongo

	def setUserParameters(self, userParameters):
		self.userParameters = userParameters

	def getUserParameters(self):
		return self.userParameters

	def setContextUserParameters(self, contextParameters):
		self.contextParameters = contextParameters

	def getContextUserParameters(self):
		return self.contextParameters



	'''
	Parsing of Regions
	'''

	'''
	Returns an array of cities (even if it is a single city)
	'''
	def parseUserRegion(self, parameters):
		if parameters.get('geo-city-us') != None and parameters.get('geo-city-us') != "" and parameters.get('geo-city-us') != []:
			return {'cities':[parameters.get('geo-city-us')],'context-geo-city-us': parameters.get('geo-city-us'),'context-geo-state-us': '','context-region': ''}
		elif parameters.get('geo-city') != None and parameters.get('geo-city') != "" and parameters.get('geo-city') != []:
			return {'cities':[parameters.get('geo-city')],'context-geo-city-us': parameters.get('geo-city'),'context-geo-state-us': '','context-region': ''}
		elif parameters.get('geo-state-us') != None and parameters.get('geo-state-us') != "" and parameters.get('geo-state-us') != []:
			return {'cities':self.parseState(parameters.get('geo-state-us')),'context-geo-city-us': '','context-geo-state-us': parameters.get('geo-state-us'),'context-region': ''}
		elif parameters.get('region') != None and parameters.get('region') != "":
			return {'cities':self.parseRegion(parameters.get('region')),'context-geo-city-us': '','context-geo-state-us': '','context-region': parameters.get('region')}
		else:
			return {'cities':self.getDefaultRegion(),'context-geo-city-us': '','context-geo-state-us': '','context-region': ''}


	'''
	TODO:: Fill with dummy data currently. Adding dummy comment
	'''
	def parseState(self, state):
		print ("This function should return a list of us cities linked to this state")

		stateData = self.mongo.db.states
		cities = []
		try:
			stateCur = stateData.find({            
		        "state":state
		        }, {
		        "city": 1
		        })

			for s in stateCur:
				print ("inside parse state the city is:" + s["city"])
				cities.append(s["city"])

			return cities

		except Exception:
			print("Could not query database")





	def parseRegion(self, region):
		print ("This function should return a list of us cities linked to this region")

		regionNotation = ""

		if region == "North East":
			regionNotation = "NE"
		elif region == "North West":
			regionNotation = "NW"
		elif region == "South East":
			regionNotation = "SE"
		elif region == "South West":
			regionNotation = "SW"
		else:
			region = ""


		regionData = self.mongo.db.region
		cities = []
		try:
			regionCur = regionData.find({            
			    "region":regionNotation
			    }, {
			    "city": 1
			    })

			for r in regionCur:
				cities.append(r["city"])
				print("The city is:"+ r["city"])

			#print("the list of cities is:"+ cities[0])
			#print("the list of cities is:"+ cities[1])
			return cities

		except Exception:
			print("Could not query database")

	def getDefaultRegion(self):
		print ("This function should return a list of us cities linked to the default region")
		return self.parseRegion(self.getStrDefaultRegion())

	def getStrDefaultRegion(self):
		return Constants.getStrDefaultRegion()

	'''
	Parses the context user region and returns the city
	'''
	def parseContextUserRegion(self, parameters, contextParameters):
		if parameters.get('geo-city-us') != None and parameters.get('geo-city-us') != "" and parameters.get('geo-city-us') != []:
			return {'cities':[parameters.get('geo-city-us')], 'context-geo-city-us': parameters.get('geo-city-us'),'context-geo-state-us': '','context-region': ''}
		elif parameters.get('geo-city') != None and parameters.get('geo-city') != "" and parameters.get('geo-city') != []:
			return {'cities':[parameters.get('geo-city')],'context-geo-city-us': parameters.get('geo-city'),'context-geo-state-us': '','context-region': ''}
		elif parameters.get('geo-state-us') != None and parameters.get('geo-state-us') != "" and parameters.get('geo-state-us') != []:
			return {'cities':self.parseState(parameters.get('geo-state-us')),'context-geo-city-us': '','context-geo-state-us': parameters.get('geo-state-us'),'context-region': ''}
		elif parameters.get('region') != None and parameters.get('region') != "":
			return {'cities':self.parseRegion(parameters.get('region')),'context-geo-city-us': '','context-geo-state-us': '','context-region': parameters.get('region')}
		elif contextParameters.get('context-geo-city-us') != None and contextParameters.get('context-geo-city-us') != "" and contextParameters.get('context-geo-city-us') != []:
			return {'cities':[contextParameters.get('context-geo-city-us')],'context-geo-city-us': contextParameters.get('context-geo-city-us'),'context-geo-state-us': '','context-region': ''}  
		elif contextParameters.get('context-geo-state-us') != None and contextParameters.get('context-geo-state-us') != "" and contextParameters.get('context-geo-state-us') != []:
			return {'cities':self.parseState(contextParameters.get('context-geo-state-us')),'context-geo-city-us': '','context-geo-state-us': contextParameters.get('context-geo-state-us'),'context-region': ''}
		elif contextParameters.get('context-region') != None and contextParameters.get('context-region') != "":
			return {'cities':self.parseRegion(contextParameters.get('context-region')),'context-geo-city-us': '','context-geo-state-us': '','context-region': contextParameters.get('context-region')}
		else:
			return {'cities':self.getDefaultRegion(),'context-geo-city-us': '','context-geo-state-us': '','context-region': ''}






	'''
	Parsing of Products
	'''
	def parseUserProducts(self, parameters):
		if parameters.get('product') != None and parameters.get('product') != "" and parameters.get('product') != []:
			return {'product': self.getPIdsFromPNames(parameters.get('product')), 'context-product': parameters.get('product')}
		else:
			return {'product': [self.getDefaultProduct()], 'context-product': []}

	'''
	Note should be depreciated to accomodate multiple products (Will require change in generating response and sales amount)
	'''
	def parseUserProduct(self, parameters):
		if parameters.get('product') != None and parameters.get('product') != "":
			return {'product': self.getPIdFromPName(parameters.get('product')), 'context-product': parameters.get('product')}
		else:
			return {'product': self.getDefaultProduct(), 'context-product': ''}

	def getDefaultProduct(self):
		print ("This function should return a list a single default product or a list of products")
		return self.getPIdFromPName(self.getStrDefaultProduct())

	def getAllProducts(self):
		print ("This function should return a list of all products in the database")

	def getStrDefaultProduct(self):
		return Constants.getStrDefaultProduct()
	'''
	Return an array of product ids
	{{pNames}} Array of product names
	'''
	def getPIdsFromPNames(self, pNames):
		pIds = []
		for index in range(0, len(pNames)):
			pIds.append(self.getPIdFromPName(pNames[index]))

		return pIds


	def getPIdFromPName(self, pName):
		print ("This function should return a product id from a product name")


		prodData = self.mongo.db.products
		try:
			prodCur = prodData.find({            
			    "pName":pName
			    }, {
			    "pId": 1
			    })

			for p in prodCur:
				pId = p["pId"]

			return pId

		except Exception:
			print("Could not query database")



	def getPNameFromPId(self, pId):
		print ("This function should return a product name from a product id")


		prodData = self.mongo.db.products
		try:
			prodCur = prodData.find({            
			    "pId":pId
			    }, {
			    "pName": 1
			    })

			for p in prodCur:
				pName = p["pName"]

			return pName

		except Exception:
			print("Could not query database")



	def parseContextUserProduct(self, parameters, contextParameters):
		if parameters.get('product') != None and parameters.get('product') != "":
			return {'product': self.getPIdFromPName(parameters.get('product')), 'context-product': parameters.get('product')}
		elif contextParameters.get('context-product') != None and contextParameters.get('context-product') != "":
			return {'product': self.getPIdFromPName(contextParameters.get('context-product')), 'context-product': contextParameters.get('context-product')}
		else:
			return {'product': self.getDefaultProduct(), 'context-product': ''}


	def parseContextUserProducts(self, parameters, contextParameters):
		if parameters.get('product') != None and parameters.get('product') != "" and parameters.get('product') != []:
			return {'product': self.getPIdsFromPNames(parameters.get('product')), 'context-product': parameters.get('product')}
		elif contextParameters.get('context-product') != None and contextParameters.get('context-product') != ""  and contextParameters.get('context-product') != []:
			return {'product': self.getPIdsFromPNames(contextParameters.get('context-product')), 'context-product': contextParameters.get('context-product')}
		else:
			return {'product': [self.getDefaultProduct()], 'context-product': ''}








	'''
	Parsing of Dates and Periods
	'''


	def parseUserPeriod(self, period):
		'''print ("Period at index 0 is:" + period[0])'''
		'''print ("trying to get date at index 0" + period[0].get('date'))'''
		if period == "":
			return {"startDate": self.getStrDefaultStartDate(), "endDate": self.getStrDefaultEndDate(), "context-period": ""}
		elif period.get('date') != None and period.get('date') != "":
			parsedDate = self.parseDate(period.get('date'))
			parseDate["context-period"] = {}
			parsedContextPeriod = parseDate["context-period"]
			parsedContextPeriod["date"] = period.get('date')
			parsedContextPeriod["date-period"] = "" 
			return parsedDate
		elif period.get('date-period') != None and period.get('date-period') != "":
			parsedDateRange = self.parseDateRange(period.get('date-period'))
			parsedDateRange["context-period"] = {}
			parsedContextPeriod = parsedDateRange["context-period"]
			parsedContextPeriod["date"] = ""
			parsedContextPeriod["date-period"] = period.get('date-period')
			return parsedDateRange
		else:
			# TODO: Include default date (This case should never arise)
			print ("Warning error condition reached in parse user period")
			return {"startDate": self.getStrDefaultStartDate(), "endDate": self.getStrDefaultEndDate(), "context-period": ""}
	                                 
	def parseDateRange(self, datePeriod):
		print("Inside Parse for Date Period")
		startDate = datePeriod.split('/')[0]
		print ("The start date is:" + startDate)
		endDate = datePeriod.split('/')[1]
		print ("The end date is:" + endDate)

		return {"startDate": startDate, "endDate": endDate}
	    

	def parseDate(self, date):
		print("Inside Parse for Date")
		return {"startDate": date, "endDate": ""}

	def getStrDefaultStartDate(self):
		return Constants.getStrDefaultStartDate()

	def getStrDefaultEndDate(self):
		return Constants.getStrDefaultEndDate()



	def parseContextUserPeriod(self, period, contextPeriod):
		'''print ("Period at index 0 is:" + period[0])'''
		'''print ("trying to get date at index 0" + period[0].get('date'))'''
		if period == "" and contextPeriod == "":
			return {"startDate": self.getStrDefaultStartDate(), "endDate": self.getStrDefaultEndDate(), "context-period": ""}
		elif period != None and period != "" and period.get('date') != None and period.get('date') != "":        
			parsedDate = self.parseDate(period.get('date'))
			parsedDate["context-period"] = {}
			parsedContextPeriod = parsedDate["context-period"]
			parsedContextPeriod["date"] = period.get('date')
			parsedContextPeriod["date-period"] = "" 
			return parsedDate
		elif period != None and period != "" and period.get('date-period') != None and period.get('date-period') != "":
			parsedDateRange = self.parseDateRange(period.get('date-period'))
			parsedDateRange["context-period"] = {}
			parsedContextPeriod = parsedDateRange["context-period"]
			parsedContextPeriod["date"] = ""
			parsedContextPeriod["date-period"] = period.get('date-period')
			return parsedDateRange
		elif contextPeriod != None and contextPeriod != "" and contextPeriod.get('date') != None and contextPeriod.get('date') != "":
			parsedDate = self.parseDate(contextPeriod.get('date'))
			parsedDate["context-period"] = {}
			parsedContextPeriod = parsedDate["context-period"]
			parsedContextPeriod["date"] = contextPeriod.get('date')
			parsedContextPeriod["date-period"] = "" 
			return parsedDate   
		elif contextPeriod != None and contextPeriod != "" and contextPeriod.get('date-period') != None and contextPeriod.get('date-period') != "":
			parsedDateRange = self.parseDateRange(contextPeriod.get('date-period'))
			parsedDateRange["context-period"] = {}
			parsedContextPeriod = parsedDateRange["context-period"]
			parsedContextPeriod["date"] = ""
			parsedContextPeriod["date-period"] = contextPeriod.get('date-period')
			return parsedDateRange
		else:
			# TODO: Include default date (This case should never arise)
			print ("Warning error condition reached in parse user period")
			return {"startDate": self.getStrDefaultStartDate(), "endDate": self.getStrDefaultEndDate(), "context-period": ""}






	'''
	Parsing of Chart Type
	'''

	def parseUserChartType(self, parameters):
		if parameters.get('chart-type') != None and parameters.get('chart-type') != "" and parameters.get('chart-type') != []:
			return {'chart-type': parameters.get('chart-type'), 'context-chart-type': parameters.get('chart-type')}
		else:
			return {'chart-type': self.getDefaultChartType(), 'context-chart-type': ""}


	'''
	This function should return the default chart type
	'''
	def getDefaultChartType(self):
		print ("This function should return the default chart type")
		return self.getStrDefaultChartType()


	def getStrDefaultChartType(self):
		return self.getStrBarChart()

	def getStrBarChart(self):
		return Constants.getStrBarChart()

	def getStrPieChart(self):
		return Constants.getStrPieChart()


	def parseContextUserChartType(self, parameters, contextParameters):
		if parameters.get('chart-type') != None and parameters.get('chart-type') != "" and parameters.get('chart-type') != []:
			return {'chart-type': parameters.get('chart-type'), 'context-chart-type': parameters.get('chart-type')}
		elif contextParameters.get('context-chart-type') != None and contextParameters.get('context-chart-type') != "" and parameters.get('context-chart-type') != []:
			return {'chart-type': contextParameters.get('context-chart-type'), 'context-chart-type': contextParameters.get('context-chart-type')}
		else:
			return {'chart-type': self.getDefaultChartType(), 'context-chart-type': ""}





	'''
	Parsing of Main Chart Feature
	'''

	def parseUserMainChartFeature(self, parameters):
		print("main chart feature:"+ parameters.get('main-chart-feature'))
		if parameters.get('main-chart-feature') != None and parameters.get('main-chart-feature') != "" and parameters.get('main-chart-feature') != []:
			return {'main-chart-feature': parameters.get('main-chart-feature'), 'context-main-chart-feature': parameters.get('main-chart-feature')}
		else:
			return {'main-chart-feature': self.getDefaultMainChartFeature(), 'context-main-chart-feature': ""}



	def getDefaultMainChartFeature(self):
		print ("This function should return the default main chart feature")
		return self.getStrDefaultMainChartFeature()


	def getStrDefaultMainChartFeature(self):
		return self.getStrProduct()

	def getStrProduct(self):
		return Constants.getStrProduct()

	def getStrCity(self):
		return Constants.getStrCity()

	def getStrState(self):
		return Constants.getStrState()

	def getStrRegion(self):
		return Constants.getStrRegion()



	def parseContextUserMainChartFeature(self, parameters, contextParameters):
		if parameters.get('main-chart-feature') != None and parameters.get('main-chart-feature') != "" and parameters.get('main-chart-feature') != []:
			return {'main-chart-feature': parameters.get('main-chart-feature'), 'context-main-chart-feature': parameters.get('main-chart-feature')}
		elif contextParameters.get('context-main-chart-feature') != None and contextParameters.get('context-main-chart-feature') != "" and parameters.get('context-main-chart-feature') != []:
			return {'main-chart-feature': contextParameters.get('context-main-chart-feature'), 'context-main-chart-feature': contextParameters.get('context-main-chart-feature')}
		else:
			return {'main-chart-feature': self.getDefaultMainChartFeature(), 'context-main-chart-feature': ""}



	'''
	This function parses the parameters and assumes that there is an attachment in the context
	'''
	def parseContextEmail(self, parameters, contextParameters):
		if parameters.get('contact-name') != None and parameters.get('contact-name') != "":
			return {'email-to': self.getEmailFromName(parameters.get('contact-name')), 'attachment-name': contextParameters.get('context-attachment-name')}
		else:
			return {'email-to': self.getDefaultEmail(), 'attachment-name': contextParameters.get('context-attachment-name')}


	def getEmailFromName(self, name):
		print ("This function should return email address from a name")


		contactData = self.mongo.db.contactInfo
		try:
			contactCur = contactData.find({            
			    "name":name
			    }, {
			    "email": 1
			    })

			for p in contactCur:
				emailAdd = p["email"]

			return emailAdd

		except Exception:
			print("Could not query database")

	def getDefaultEmail(self):
		print ("This function should return a list a single default email or a list of email")
		return self.getEmailFromName(self.getStrDefaultName())


	def getStrDefaultName(self):
		return Constants.getStrDefaultName()