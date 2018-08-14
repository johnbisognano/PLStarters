from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from bs4 import BeautifulSoup
import re
import requests


app = Flask(__name__)

def getMyTeam(ID):
	drafturl = 'https://draft.premierleague.com/api/draft/37518/choices'
	playersurl = 'https://draft.premierleague.com/api/bootstrap-static'
	myID = ID
	myPlayersID = []
	myPlayersName = []
	resp1 = requests.get(url=drafturl)
	resp2 = requests.get(url=playersurl)
	mydata = resp1.json()
	playerdata = resp2.json()
	for player in mydata['element_status']:
		if player['owner'] == myID:
			myPlayersID.append(player['element'])

	for d in playerdata['elements']:
		if d['id'] in myPlayersID:
			myPlayersName.append(d['first_name'] + " " + d['second_name'])

	return myPlayersName

def parseStarters(myPlayersName):
	startersUrl = 'https://www.rotowire.com/soccer/lineups.php'
	startsPage = requests.get(startersUrl)

	c = startsPage.content

	soup = BeautifulSoup(c, "html.parser")

	startPlayers = []

	starters = soup.find_all('li', class_="lineup__player")
	for player in starters:
		parsed = " ".join(player.text.split())
		if any(parsed.split()[-1] in s for s in myPlayersName):
			startPlayers.append(parsed)
	return startPlayers

def getStarters(startPlayers):
	goalies = []
	mids= []
	forwards = []
	defenders = []

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

def createMessage(ID):
	goalies, mids, forwards, defenders = getStarters(parseStarters(getMyTeam(ID)))
	goalies = ", ".join(goalies)
	mids = ", ".join(mids)
	forwards = ", ".join(forwards)
	defenders = ", ".join(defenders)
	if not defenders and not forwards and not mids and not goalies:
		body = ""
	else:
		body="Hi! Here are your current predicted starters\n\n" + "GOALIES: " + goalies + "\n\nMIDS: " + mids + "\n\nFORWARDS: " + forwards + "\n\nDEFENDERS: " + defenders
	return(body)

print(createMessage(142880))




