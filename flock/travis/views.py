from rest_framework import status
import json,logging,requests
from travispy import TravisPy
from django.http import HttpResponse,HttpResponseBadRequest
from requests.auth import HTTPBasicAuth
from urlparse import parse_qs
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from pyflock import FlockClient, verify_event_token, Message
from travis.serializers import UserSerializer
from travis.models import User,TravisAccounts
from travis.functions import register_travis_user,check_authorized,_get_signature,_get_travis_public_key
from OpenSSL.crypto import Error as SignatureError
from rest_framework.renderers import JSONRenderer
from flock.settings import TRAVIS_APP_ID,TRAVIS_APP_SECRET,TRAVIS_BOT_TOKEN,TESTAPI_BOT_TOKEN,TESTAPI_APP_ID,TESTAPI_APP_SECRET
from pyflock import FlockClient, Views, HtmlView, WidgetView, Message, Attachment
# Create your views here.

@api_view(['GET','POST'])
def events(request, format=None):

	print "event called"
	if(request.method=='GET'):
		return HttpResponse("hii",status=200)		
	if(request.method == 'POST'):	
		event_token = request.META["HTTP_X_FLOCK_EVENT_TOKEN"]
		travis_app_secret = TRAVIS_APP_SECRET
		testapi_app_secret = TESTAPI_APP_SECRET
		which_app=0
		try:
			verify_event_token(event_token = event_token, app_secret = travis_app_secret)
			which_app=1
		except:
			print "hii1"

		try:
			verify_event_token(event_token = event_token, app_secret = testapi_app_secret)
			which_app=2
		except:
			print "hii2"
		if(which_app==1):		
			content = json.loads(JSONRenderer().render(request.data))
			if(content["name"]=="app.install"):
				serializer = UserSerializer(data = request.data)
				if(serializer.is_valid()):
					serializer.save()		
				return Response(request.data, status=200)
			elif(content["name"]=="client.slashCommand" and content["command"]=="travis"):
				command = content["text"].split(":")
				if(command[0]=="register"):
					command[1]=command[1].split()
					github_userId = command[1][0]
					print github_userId
					if(len(TravisAccounts.objects.filter(github_userId=github_userId))!=0):
						bot_token = TRAVIS_BOT_TOKEN
						app_id = TRAVIS_APP_ID
						flock_client = FlockClient(token=bot_token, app_id=app_id)
						text="You are already registered"
						success_message = Message(to=content["userId"],text=text)
						flock_client.send_chat(success_message)
						return Response(request.data,status=200)				
					github_password = command[1][1]
					print github_userId,github_password
					payload = "{\"scopes\":[\"admin:gpg_key\",\"admin:org\",\"admin:org_hook\",\"admin:public_key\",\"admin:repo_hook\",\"delete_repo\",\"gist\",\"notifications\",\"repo\",\"user\"],\"note\": \"Token to be used in Flock\"}"
					headers = {
						"content-type":"application/json",
						"cache-control" : "no-cache"
					}
					print "hii"
					auth = HTTPBasicAuth(github_userId,github_password)	
					print "hii"
					response = requests.request("GET","https://api.github.com/authorizations",data=payload,headers=headers,auth=auth)				
					print response.text
					github_token = json.loads(response.text)[0]["token"]					
					command[1]=github_token
					print "hii2 "+command[1]+" hii"
					return register_travis_user(request,content,command,github_userId)
				else:
					return Response(request.data, status=200)
			elif(content["name"]=="app.uninstall"):
				user = User.objects.get(userId=content["userId"])	
				user.delete()			
			else:
				return Response(request.data, status=200)								

		elif(which_app==2):
			content = json.loads(JSONRenderer().render(request.data))
			if(content["name"]=="app.install"):
				return Response(request.data, status=200)
			elif(content["name"]=="client.pressButton" and content["button"]=="chatTabButton"):
				print content
				print "hii"
			else:
				return Response(request.data, status=200)			
		else:
			return Response(request.data, status=200)
		return Response(request.data, status=200)

@api_view(['GET'])
def getusers(request):

	if(request.method == 'GET'):
		users = User.objects.all()
		serializer = UserSerializer(users, many = True)
		return Response(serializer.data)		

@api_view(['POST'])
def travis_incoming_webhook(request):

	'''
		Check whether travis sent the request or not
		If not return error response
	'''	
	signature = _get_signature(request)
	json_payload = parse_qs(request.body)['payload'][0]
	public_key=""
	try:
		public_key = _get_travis_public_key()
	except requests.Timeout:
		return HttpResponseBadRequest({'status':'failed'})
	except requests.RequestException as e:
		return HttpResponseBadRequest({'status':'failed'})
	try:
		check_authorized(signature,public_key,json_payload)
	except SignatureError:
		return HttpResponseBadRequest({'status':'unauthorized'})
	content = json.loads(json_payload)
	author = content['author_name']
	message_type = content['status_message']
	changes = content['compare_url']
	build_url = content['build_url']
	repository = content['repository']['name']
	owner = content['repository']['owner_name']
	q1 = TravisAccounts.objects.filter(github_userId=owner)
	if(len(q1)==0):
		return Response(request.data,status=200)
	user_guid = q1[0].flock_user.userId

	build_passed_choices = ['Passed', 'Fixed']
	build_failed_choices = ['Broken', 'Failed', 'Still Failing']
	bot_token = TRAVIS_BOT_TOKEN
	app_id = TRAVIS_APP_ID
	flock_client = FlockClient(token=bot_token,app_id=app_id)
	views = Views()
	html = ""
	msg = "Repository : "+repository+"\n"+"Owner : "+owner+"\n"+"Author : "+author+"\n"
	if(message_type in build_passed_choices):
		html = HtmlView(inline="Build Passed",height=50)
	elif(message_type in build_failed_choices):
		html = HtmlView(inline="Build Failed",height=50)
	else:
		return Response(request.data,status=200)	
	views.add_html(html)
	attachment = Attachment(title="Travis Build Details", description=msg, views=views)
	message = Message(to=user_guid,attachments = [attachment])
	flock_client.send_chat(message)		
	return Response(request.data,status=200)