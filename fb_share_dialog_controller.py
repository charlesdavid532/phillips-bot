from fb_share_dialog import FBShareDialog
import os
class FBShareDialogController(object):
	"""docstring for FBShareDialogController"""
	def __init__(self):
		super(FBShareDialogController, self).__init__()

	def getJSONResponse(self):
		fbShareDialogObj = FBShareDialog(os.environ['FACEBOOK_LOGIN_CLIENT_ID'])
		fbShareDialogObj.setDisplayType('popup')
		fbShareDialogObj.setCaption('An example caption')
		fbShareDialogObj.setLink('https://developers.facebook.com/docs/')
		fbShareDialogObj.setRedirectURI('https://developers.facebook.com/tools/explorer')

		return fbShareDialogObj.showDialog()
		