'''
Script to parse .wer files and output the data as JSON.
Then process the JSON file and save it SQLite DB.
'''

import json
import xmltodict
import sqlite3
from db import *
import uuid

def wertojson():

    # Open .wer file and output it as JSON

    with open("20180319.wer", encoding="utf-8") as werdata:
        global json_data
        json_data = json.loads(json.dumps(xmltodict.parse(werdata.read()), indent=1))
        # print(json_data["event"])
        # with open("20180319.json", 'w') as f:
        #     f.write(json.dumps(parsed_wer, indent=4))

def tournament_to_db():

    event = json_data["event"]
    db_insert_tournament(str(event["@eventguid"]),str(event["@startdate"]),str(event["@format"]).title(),int(event["@numberofrounds"]))

def players_to_db():

    # Parse the players in the tournament and add them to the DB
    # if they don't exist yet.

    person_list = json_data["event"]["participation"]["person"]
    for person in person_list:
        db_insert_players(int(person["@id"]),str(person["@first"]),str(person["@last"]),str(person["@country"]))

def rounds_matches_to_db():

    # Parse the rounds and each match played.
    # Keep track of byes as well even though it's not a real match.

    event = json_data["event"]
    round_list = json_data["event"]["matches"]["round"]
    match_list = json_data["event"]["matches"]["round"][0]["match"]

    for rnd in round_list:
        temp_round_uid = str(uuid.uuid4())
        db_insert_rounds(temp_round_uid,str(rnd["@date"]),int(rnd["@number"]),str(event["@eventguid"]))
        for match in match_list:
            # print(temp_round_uid)
            if match["@outcome"] != "3":
                db_insert_matches(str(uuid.uuid4()),temp_round_uid,str(match["@person"]),str(match["@opponent"]),int(match["@win"]),int(match["@loss"]),int(match["@draw"]),int(match["@outcome"]))
            else:
                db_insert_matches(str(uuid.uuid4()),temp_round_uid,str(match["@person"]),None,int(match["@win"]),int(match["@loss"]),int(match["@draw"]),int(match["@outcome"]))

def pairings():
    plist = []
    dci = []
    names = []

    person_list = json_data["event"]["participation"]["person"]
    for person in person_list:
        dci.append(person["@id"])
        names.append(person["@first"]+" "+person["@last"])
    players = dict(zip(dci, names))

    event_list = json_data["event"]["matches"]["round"]
    for event in event_list:
        match_list = event["match"]
        for match in match_list:
            if match["@win"] == "-1":
                plist.append(players.get(match["@person"], "")+" <=> "+players.get(match["@opponent"], ""))
    with open("pairings.txt", 'w', encoding="utf-8") as f:
        f.write('\n'.join(plist))

wertojson()
tournament_to_db()
players_to_db()
rounds_matches_to_db()
# pairings()
