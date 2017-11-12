class SelectedListItem(object):
	"""docstring for SelectedListItem"""
	def __init__(self, data):
		super(SelectedListItem, self).__init__()
		self.requestData = data

	def getSelectedListItem(self):
		firstInput = self.requestData.get("originalRequest").get("data").get("inputs")[0]
		if 'arguments' in firstInput:
			optionVal = firstInput["arguments"][0]["textValue"]
			print("The option chosen:::")
			print(optionVal)
			return optionVal

		return False
		