from geopy.distance import great_circle
class LocationParser(object):
	"""docstring for LocationParser"""
	def __init__(self):
		super(LocationParser, self).__init__()
		self.baseLocation = {}
		self.objectLocations = []

	def setBaseLocation(self, latitude, longitude):
		self.baseLocation["latitude"] = latitude
		self.baseLocation["longitude"] = longitude

	def getBaseLocation(self):
		return self.baseLocation["latitude"], self.baseLocation["longitude"]

	def setObjectLocations(self, objectLocations):
		self.objectLocations = objectLocations

	def getObjectLocations(self):
		return self.objectLocations

	def getNNearestLocations(self, n):
		return self.getSortedLocations()[:n]


	def getSortedLocations(self):
		baseLocation = (self.baseLocation["latitude"], self.baseLocation["longitude"])

		for i in range(0, len(self.objectLocations)):
			currentLocationObj = self.objectLocations[i]
			curLocation = (currentLocationObj["latitude"], currentLocationObj["longitude"])
			distance = great_circle(baseLocation, curLocation).km
			print("The distance is:::" + str(distance))
			self.objectLocations[i]["distance"] = distance

		sortedList = self.objectLocations.sort(key=lamda x:x["distance"])
		
		#Just for checking if logic is correct
		for i in range(0, len(sortedList)):
			print("The sorted distance is:::" + str(sortedList[i]["distance"]))

		return sortedList