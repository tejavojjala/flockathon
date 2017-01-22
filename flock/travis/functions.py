from rest_framework.response import Response
from travispy import TravisPy
import requests,json,base64
from OpenSSL.crypto import verify, load_publickey, FILETYPE_PEM, X509
from django.http import HttpResponse
from travis.models import User,TravisAccounts
from pyflock import FlockClient, Views, HtmlView, WidgetView, Message, Attachment
from flock.settings import TRAVIS_APP_ID,TRAVIS_APP_SECRET,TRAVIS_BOT_TOKEN,TESTAPI_BOT_TOKEN,TESTAPI_APP_ID,TESTAPI_APP_SECRET

def register_travis_user(request,content,command,github_userId):
	try:
		flock_user = User.objects.filter(userId=content["userId"])[0]
		flag = False
		if(len(TravisAccounts.objects.filter(github_userId=github_userId))==0):
			travisAccount = TravisAccounts.objects.create_travis_account(flock_user=flock_user,github_access_token=command[1],github_userId=github_userId)		
			travisAccount.save()
			flag = True
		bot_token = TRAVIS_BOT_TOKEN
		app_id = TRAVIS_APP_ID
		flock_client = FlockClient(token=bot_token, app_id=app_id)
		text=""
		if(flag):
			text="You are Successfully registered. You will receive travis build notifications for repo's you have in "+github_userId+" github account"
			success_message = Message(to=content["userId"],text=text)
			flock_client.send_chat(sucess_message)
		else:
			text="You are already Registered"
			message = Message(to=content["userId"],text=text)
			flock_client.send_chat(message)
		return Response(request.data,status=200)
	except:
		bot_token = TRAVIS_BOT_TOKEN
		app_id = TRAVIS_APP_ID
		flock_client = FlockClient(token=bot_token, app_id=app_id)
		failed_message = Message(to=content["userId"],text="An error occured. Please try again")
		res = flock_client.send_chat(failed_message)
		return Response(request.data,status=200)

def check_authorized(signature, public_key, payload):
	pkey_public_key = load_publickey(FILETYPE_PEM, public_key)
	certificate = X509()
	certificate.set_pubkey(pkey_public_key)
	verify(certificate, signature, payload, str('sha1'))


def _get_signature(request):
	signature = request.META['HTTP_SIGNATURE']
	return base64.b64decode(signature)

def _get_travis_public_key():
	response = requests.get("https://api.travis-ci.org/config", timeout=10.0)
	response.raise_for_status()
	return response.json()['config']['notifications']['webhook']['public_key']