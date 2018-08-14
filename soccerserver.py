from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse, Message
from bs4 import BeautifulSoup
import re
import requests

app = Flask(__name__)


"""
Retrieves details about a specific persons team based on their given ID
"""
def getMyTeam(ID):
	# This URL uses draft ID specific to my league
	drafturl = 'https://draft.premierleague.com/api/draft/37518/choices'
	playersurl = 'https://draft.premierleague.com/api/bootstrap-static'
	myID = ID
	myPlayersID = []
	myPlayersName = []

	# Get JSON
	resp1 = requests.get(url=drafturl)
	resp2 = requests.get(url=playersurl)
	mydata = resp1.json()
	playerdata = resp2.json()

	# Get players by ID owned by specific manager
	for player in mydata['element_status']:
		if player['owner'] == myID:
			myPlayersID.append(player['element'])

    # Convert player IDs to Names
	for d in playerdata['elements']:
		if d['id'] in myPlayersID:
			myPlayersName.append(d['first_name'] + " " + d['second_name'])

	return myPlayersName


"""
Scrapes for predicted starters from persons specific team
"""
def parseStarters(myPlayersName):
	# Website with predicted weekly lineups
	startersUrl = 'https://www.rotowire.com/soccer/lineups.php'
	startsPage = requests.get(startersUrl)
	startPlayers = []

	c = startsPage.content

	soup = BeautifulSoup(c, "html.parser")
	
	starters = soup.find_all('li', class_="lineup__player")

	# Get starters from specific manager's team
	for player in starters:
		parsed = " ".join(player.text.split())
		if any(parsed.split()[-1] in s for s in myPlayersName):
			startPlayers.append(parsed)
	return startPlayers


"""
Sorts team's starters by position
"""
def getStarters(startPlayers):
	goalies = []
	mids= []
	forwards = []
	defenders = []

	# Make lists of starters by position
	for player in startPlayers:
		pos = player.split()[0]
		player = " ".join(player.split()[1:])
		if 'G' in pos:
			goalies.append(player)
		if 'M' in pos:
			mids.append(player)
		if 'F' in pos:
			forwards.append(player)
		if 'D' in pos:
			defenders.append(player)
	return goalies, mids, forwards, defenders


"""
Generates message text
"""
def createMessage(ID):
	goalies, mids, forwards, defenders = getStarters(parseStarters(getMyTeam(ID)))

	# Make strings from lists by position
	goalies = ", ".join(goalies)
	mids = ", ".join(mids)
	forwards = ", ".join(forwards)
	defenders = ", ".join(defenders)

	# Check for invalid ID from text
	if not defenders and not forwards and not mids and not goalies:
		body = ""
	else:
		body="Hi! Here are your current predicted starters\n\n" + "GOALIES: " + goalies + "\n\nMIDS: " + mids + "\n\nFORWARDS: " + forwards + "\n\nDEFENDERS: " + defenders
	return(body)

@app.route("/sms", methods=['GET', 'POST'])
"""
Retrieves message and sends appropriate response
"""
def sms_reply():
	# Create and send text
	message_body = request.form['Body']
	if message_body.isdigit():
		reply = createMessage(int(message_body))
	else:
		reply = ""
	resp = MessagingResponse()
	if reply == "":
		resp.message("Your ID was invalid. Please try again")
	else:
		resp.message(reply)
	return str(resp)


if __name__ == "__main__":
	app.run(debug=True)