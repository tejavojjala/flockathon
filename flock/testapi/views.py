from django.shortcuts import render
import json,requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth1
from rest_framework.decorators import api_view
from django.http import HttpResponse,HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from pyflock import FlockClient, Views, HtmlView, WidgetView, Message, Attachment
from flock.settings import TRAVIS_APP_ID,TRAVIS_APP_SECRET,TRAVIS_BOT_TOKEN,TESTAPI_BOT_TOKEN,TESTAPI_APP_ID,TESTAPI_APP_SECRET

# Create your views here.
@xframe_options_exempt
def testapi(request):
	try:
		chat=json.loads(request.GET.get("flockEvent"))["chat"]
	except:
		chat=""
	return render(request,'testapi/testapi.html',{'chat':chat})

@csrf_exempt
def process_api_request(request):

	if(request.method != 'POST'):
		return HttpResponseBadRequest("Only Post Supported")
	content = json.loads(JSONRenderer().render(request))[0]
	content = json.loads(content)
	share = content["share"]
	api_endpoint = content["api_endpoint"]
	http_method = content["httpmethod"]
	headers_data = content["headers_data"].strip().split("\n")
	auth_data = json.loads(content["auth_data"])
	body_data = content["body_data"].strip()
	body_type = content["body_type"]
	response_data = content["response_data"].strip()
	chat = content["chatId"].strip()
	print chat
	print api_endpoint
	headers= {'accept':'application/json'}
	payload = {}
	for each in headers_data:
		each = each.split(":")
		if(len(each)==2):
			headers[each[0]]=each[1]

	if(share==1):
		share_response_string="Http Method   : "+http_method+"\n"+"API EndPoint  : "+api_endpoint+"\n"+"Headers       : "+"\n"
		for key,val in headers.items():
			share_response_string=share_response_string+"     "+key+" : "+val+"\n"		
		share_response_string=share_response_string+"Auth Details  :\n"
		for key,val in auth_data.items():
			share_response_string=share_response_string+"     "+key+" : "+val+"\n"		
		if(http_method=="POST"):
			if(body_data!=""):
				share_response_string=share_response_string+"Body Details  :"+"\n"+"     "+"Body Type  : "+body_type+"Body     : "+body_data		
		share_response_string=share_response_string+"\nResponse\n"+response_data
		bot_token = TESTAPI_BOT_TOKEN
		app_id = TESTAPI_APP_ID
		flock_client = FlockClient(token=bot_token,app_id=app_id)
		views = Views()
		print share_response_string
		html = HtmlView(inline=share_response_string,height=100)
		views.add_html(html)
		attachment = Attachment(title="Test Api Content", description=share_response_string, views=views)
		print chat
		message = Message(to=chat,attachments = [attachment])
		print share_response_string
		print flock_client
		print flock_client.send_chat(message)		
	
		print share_response_string+"\n"+"message passed"
		return HttpResponse(status=200)


	if(auth_data["auth_type"]=="basicauth"):
		auth = HTTPBasicAuth(auth_data["username"],auth_data["password"])
	elif(auth_data["auth_type"]=="oauth1.0"):
		auth = OAuth1(auth_data["consumerkey"],auth_data["consumersecret"],auth_data["token"],auth_data["tokensecret"])
	response = []		
	try:
		if(http_method=="GET" or body_data==""):
			if(auth_data["auth_type"]=="noauth"):
				response = requests.request(http_method,url=api_endpoint,headers=headers)
			else:
				response = requests.request(http_method,url=api_endpoint,headers=headers,auth=auth)
		else:
			payload = body_data
			if(body_type=="application/json"):
				payload = json.loads(payload)
			if(auth_data["auth_type"]=="noauth"):
				if(body_type=="application/json"):
					response = requests.request(http_method,url=api_endpoint,json=payload,headers=headers)
				else:
					response = requests.request(http_method,url=api_endpoint,data=payload,headers=headers)					
			else:
				if(body_type=="application/json"):
					response = requests.request(http_method,url=api_endpoint,json=payload,headers=headers,auth=auth)
				else:
					response = requests.request(http_method,url=api_endpoint,data=payload,headers=headers,auth=auth)					
		django_response = HttpResponse( content=response.content,status=response.status_code,
									   content_type=response.headers['Content-Type'])
		return django_response
	except:
		return HttpResponse("An error occured",status=400)
