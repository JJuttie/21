## Technisch ontwerp
### Controllers in helpers.py
def login_required():
		“”Make sure user logs in””

def apology():
	“”Return apology if user’s request is not valid””

### Controllers in application.py
def login():
“”Logs in user””
Request method: POST

def browse():
“”Let user match recipes””
Request method: POST

def register():
“”Register a new user””

def recipe():
Request method: POST

def match():
“”Let user see all their matches””
Request method: POST

def account()
“”Let user edit their account settings””
Request method: POST

def logout():
“”Let user log out””

### Extra functies in application.py
def Facebook_login():
“”Let user register with their Facebook account””
Request method: POST

def gps():
“”Use user’s GPS location to add a location to user’s account and let them filter on location””
Request method: POST

### Models/helpers
-	Allergieën helpers
-	Importeren van upload functie
-	Importeren van gps

### Plugins
Bootstrap:
https://getbootstrap.com

Flask bycrypt (for hashing passwords):
https://flask-bcrypt.readthedocs.io/en/latest/

Flask login:
https://flask-login.readthedocs.io/en/latest/
