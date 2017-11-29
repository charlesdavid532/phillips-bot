class SelectedListItem(object):
	providers = None
	"""docstring for SelectedListItem"""
	def __init__(self, provider_name, data):
		super(SelectedListItem, self).__init__()
		self.provider_name = provider_name
		self.requestData = data

	def getSelectedListItem(self):
		pass

	@classmethod
	def set_provider_none(self):
		self.providers = None

	@classmethod
	def get_provider(self, provider_name, data):
		if self.providers is None:
			self.providers={}
			for provider_class in self.__subclasses__():
				provider = provider_class(data)
				self.providers[provider.provider_name] = provider
		return self.providers[provider_name]


class GoogleSelectedItem(SelectedListItem):
	"""docstring for GoogleSelectedItem"""
	def __init__(self, data):
		super(GoogleSelectedItem, self).__init__('google', data)
		
	def getSelectedListItem(self):
		firstInput = self.requestData.get("originalRequest").get("data").get("inputs")[0]
		if 'arguments' in firstInput:
			optionVal = firstInput["arguments"][0]["textValue"]
			print("The option chosen:::")
			print(optionVal)
			return optionVal

		return False


class FacebookSelectedItem(SelectedListItem):
	"""docstring for FacebookSelectedItem"""
	def __init__(self, data):
		super(FacebookSelectedItem, self).__init__('facebook', data)


	def getSelectedListItem(self):
		selectedItemData = self.requestData.get("originalRequest").get("data")
		if 'postback' in selectedItemData:
			postbackData = selectedItemData.get('postback')
			if 'payload' in postbackData:
				optionVal = postbackData.get('payload')
				print("The option chosen:::")
				print(optionVal)
				return optionVal

			return False

		return False