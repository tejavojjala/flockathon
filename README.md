# flockathon

This project is developed during Flockathon(https://www.hackerearth.com/sprints/flockathon)

I have built two apps to integrete on top of flock.

1)Travis-CI:- With this app you can get notified about the build status whenever a build completes on a push or pull request on github. 


2)TestApi:- With this app you can open a widget to test your api. Like you do with Postman.

#Instructions To Run


Download the source code:

cd flock/

Create a virtual environment:

virtualenv venv

source venv/bin/activate

Install requirements:

pip install -r requirements.txt

You also need to install pyflock.One of the following commands should help you:

pip install git+git://github.com/flockchat/pyflock

pip install git+https://github.com/flockchat/pyflock

If you don't have ngrok please install it

sudo apt-get install ngrok

Again cd flock/

Make migrations

python manage.py make migrations

python manage.py migrate

Now run the server

python manage.py runserver 8080

Open a new terminal:

cd flock/

source venv/bin/activate

ngrok http 8080

Copy the link which is of the form http://XXXXX.ngrok.io.Lets call this base url.

Now go to dev.flock.co

Steps for creating Travis App:

Basic Information:

App name: Travis-CI

App description: Get notified for build status from github

Advanced Information:

Event listener url: baseurl/events (i.e. http://XXXXX.ngrok.io/events)

Enable slash command:

Name of command:travis

Short description:register your github account

Syntax hint: "register:user_name user_password"(without quotes. Also note the gap between

user_name and user_password)

Action for slash command:Send to event listener url

Enable bot

Hit Save

You will get Appid,App secret,Bot Guid,Bot token.

Open settings.py file in the project you just downloaded.

Copy the relevant contents at bottom of the file.

Don't forget to publish your app

Steps for creating TestApi App:

Basic Information:

App name: TestApi

App description: Test your api like you do with postman

Advanced Information:

Event listener url: baseurl/events (i.e. http://XXXXX.ngrok.io/events)

Enable App launcher button:

Tooltip Text: TestApi

Action for App launcher: Open widget

Type of widget in desktop: Modal

Action url:  https://XXXXX.ngrok.io/testapi(please note that it is https)

Enable bot

Hit Save

You will get Appid,App secret,Bot Guid,Bot token.

Open settings.py file again.

Copy the relevant contents at bottom of the file.

Open testapi/templates/testapi/testapi.html

In line number 155(in ajax call) replace url with (https://XXXXX.ngrok.io/processapi) i.e. your base url/processapi

Now install both the apps.

How to use Travis App:

Enter the following slashCommand in flock

/travis register:your_github_userId your_github_password

Now in your .travis.yml file in your github project:

Add the following:

notifications: webhooks: baseurl/webhook (i.e. http://XXXXX.ngrok.io/webhook)

Now you get a notification whenever a build has completed.

How to use TestApi:

Just click the app launcher button. Everything will be self explanatory.
