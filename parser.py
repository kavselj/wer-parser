'''
Script to parse .wer files and output the data as JSON.
Then process the JSON file and save it SQLite DB.
'''

import json
import xmltodict
import sqlite3
from db import *
import uuid
import os

def parse_all():
    opendecks()
    for filename in os.listdir('ELO'):
        wertojson(filename)
        check_duplicate()
    print("All tournaments successfully parsed!")

def wertojson(filename):

    # Open .wer file and output it as JSON

    with open("ELO/{}".format(filename), encoding="utf-8") as werdata:
        global json_data
        json_data = json.loads(json.dumps(xmltodict.parse(werdata.read()), indent=1))

def opendecks():

    with open("decks.json", encoding="utf-8") as decks:

        global deck_data
        deck_data = json.loads(decks.read())

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

    for rnd in round_list:
        temp_round_uid = str(uuid.uuid4())
        db_insert_rounds(temp_round_uid,str(rnd["@date"]),int(rnd["@number"]),str(event["@eventguid"]))
        for match in rnd["match"]:
            # print(temp_round_uid)
            if match["@outcome"] not in ("3","5"):
                db_insert_matches(str(uuid.uuid4()),temp_round_uid,str(match["@person"]),str(match["@opponent"]),int(match["@win"]),int(match["@loss"]),int(match["@draw"]),int(match["@outcome"]))
            else:
                db_insert_matches(str(uuid.uuid4()),temp_round_uid,str(match["@person"]),None,int(match["@win"]),int(match["@loss"]),int(match["@draw"]),int(match["@outcome"]))

def players_to_tournaments():

    event = json_data["event"]
    person_list = json_data["event"]["participation"]["person"]
    dates = deck_data["tournament"]

    # for person in person_list:
        # print(person["@id"]+" - "+person["@first"]+" "+person["@last"])
    for date in dates:
        if date["@date"] == event["@startdate"]:
            for deck in date["players"]:
                deck_id = db_deck_check(deck.get("@deck"))
                # print(deck_id)
                if deck_id == None:
                    temp_deck_uid = uuid.uuid4()
                    db_insert_decks(str(temp_deck_uid),str(deck.get("@deck")))
                    db_insert_players_to_tournaments(int(deck["@dci"]),str(event["@eventguid"]),str(temp_deck_uid))
                else:
                    db_insert_players_to_tournaments(int(deck["@dci"]),str(event["@eventguid"]),str(deck_id[0]))

def check_duplicate():

    # Check if the tournament is already in database.

    tournament_uid = str(json_data["event"]["@eventguid"])
    if db_duplicate_check(tournament_uid) == None:
        tournament_to_db()
        players_to_db()
        rounds_matches_to_db()
        players_to_tournaments()
        print(f"Tournament ID {tournament_uid} successfully entered into the database!")
    elif tournament_uid == db_duplicate_check(tournament_uid)[0]:
        print(f"Tournament ID {tournament_uid} already exists in the database!")

parse_all()
