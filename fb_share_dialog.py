from flask import redirect
class FBShareDialog(object):
	"""docstring for FBShareDialog"""
	def __init__(self, appId):
		super(FBShareDialog, self).__init__()
		self.appId = appId
		self.displayType = None
		self.caption = None
		self.link = None
		self.redirectURI = None


	def setDisplayType(self, displayType):
		self.displayType = displayType

	def setCaption(self, caption):
		self.caption = caption

	def setLink(self, link):
		self.link = link

	def setRedirectURI(self, redirectURI):
		self.redirectURI = redirectURI


	def showDialog(self):
		#Creating the params
		paramVars = {'app_id': self.appId, 'display':self.displayType,
		        'caption':self.caption, 'link': self.link, 'redirect_uri': self.redirectURI  }

		FBShareDialogCallbackURI = 'https://www.facebook.com/dialog/feed' + '?' + urllib.parse.urlencode(paramVars)

		return redirect(FBShareDialogCallbackURI)
		