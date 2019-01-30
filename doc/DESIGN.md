## Technisch ontwerp
### Controllers in helpers.py
def login_required():
“”Make sure user logs in””
- Pagina's alleen toegankelijk maken wanneer er is ingelogd.

def apology():
“”Return apology if user’s request is not valid””
- errorcode plus foutmelding

def check_matches(userid):
"""Returns a set of all matches for the given id"""
- Check waar matches zijn in de tabel like
- Verzameld een set met alle user_id's waarmee de gebruiker matcht

def check_liked(userid):
"""Returns a set of all likes given by the given id"
- Verzameld een set van iedereen die is geliked door deze gebruiker.

### Controllers in application.py
def login():
“”Logs in user””
Request method: POST and GET
- check voor bestaande gebruiker
- controleert de vakjes
- controleert wachtwoord
- stuurt door naar de browse pagina

def index():
“”Let user match recipes””
Request method: POST en GET
- bij een swipe naar rechts:
	- match noteren in de database, wie liket wie?
	- controleren of de andere jou ook al heeft geliket:
		- zoja, melding("je hebt een match!")
	- nieuw gerecht tonen
- bij een swipe naar links:
	- nieuw gerecht tonen
- gerechten die je al eerder hebt geswiped niet meer tonen.

def register():
“”Register a new user””
- gegevens opslaan
- controleren of confirmation wachtwoord gelijk is aan wachtwoord
- doorsturen naar pagina waar je je gerecht invoert
- bevestigingsmail sturen naar opgegeven emailadres

def recipe():
Request method: POST
- verwerken van een gerecht bij registratie
	- afbeelding/gif kunnen uploaden
	- alfbeelding/gif scannen op ongepast beeldmateriaal dmv API "SightEngine"
	- allergie-tags kiezen met een keuzemenu
	- afbeelding/gif, bio, tags en titel opslaan in database
	- koppelen aan huidige gebruiker
	- afbeelding bestandsnaam aanpassen naar user_id
- doorsturen naar browse pagina

def changerecipe():
Request method: POST
- huidige recept ophalen en tonen
- mogelijkheid geven om deze te wijzigen
	- bij opslaan:
			- oude gerecht verwijderen
			- nieuwe afbeelding/gif wederom scannen op ongepast beeldmateriaal dmv API "SightEngine"
			- nieuwe gerecht opslaan

def matches():
“”Let user see all their matches””
- tonen van alle matches van huidige gebruiker
	- het gerecht en de contact gegevens
	- dit doen door:
		- met check_matches() uit helpers.py de user-id's opzoeken
		- het gerecht en de contactgegevens van deze user vervolgens ophalen
		- deze verzenden naar de matches.html
Request method: POST

def like():
"""Het invoeren van een like naar de database"""
- In de tabel likes wordt opgenomen wie wie heeft geliked.
- Vervolgens kunnen we deze tabel checken op matches.

def account()
“”Let user edit their account settings””
- tonen van gegevens
- mogelijkheid om wachtwoord te bekijken.
	- met def password():
		- wachtwoord controleren
		- wachtwoord updaten
Request method: POST

def logout():
“”Let user log out””
- session clear
- doorsturen naar login

def forgot():
"""Wachtwoord vergeten"""
- controleert ingevoerde gegevens
- indien juist, mogelijkheid om wachtwoord te updaten
- daarna doorsturen naar login

def delete():
"""Delete account""""
- controleert het wachtwoord dat je moet invoeren om te bevestigen
- verwijdert usergegevens uit de tabel users
- verwijdert het gerecht uit de tabel recipes
- verwijdert het fotobestand uit de repository
- verwijdert de acties waarin jij iemand hebt geliket, en de acties waarin jij bent geliket.


### Extra functies in application.py
def Facebook_login():
“”Let user register with their Facebook account””
Request method: POST

def gps():
“”Use user’s GPS location to add a location to user’s account and let them filter on location””
Request method: POST

### API
- SightEngine
	- Beoordeeld het uploaden van afbeeldingen en gifs op nudity, weapons, alcohol, enz.
	- Op deze manier kunnen we afbeeldingen van alles behalve gerechten weigeren.
	- https://sightengine.com

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

SightEngine:
https://sightengine.com/demo
