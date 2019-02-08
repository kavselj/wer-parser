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
import glicko2

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
        db_insert_players(int(person["@id"]),str(person["@first"]),str(person["@last"]),str(person["@country"]),str(1500.0), str(350.0), str(0.06))

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

def update_glicko():

    event = json_data["event"]
    person_list = json_data["event"]["participation"]["person"]

    players_dci = []
    players_ratings = []

    players_newrating = []

    for player in db_fetch_players():
        players_dci.append(player[0])
        players_info = (player[1], player[2], player[3])
        players_ratings.append(players_info)

    players = dict(zip(players_dci, players_ratings))

    current_players = []

    for player in person_list:
        current_players.append(int(player["@id"]))

    # print(players)
    # print(current_players)

    # TO DO: Fetch players match data (outcome, player 1, player 2 and opponents rating, rd and vol)

    matches = []

    for round in db_fetch_rounds(str(event["@eventguid"])):
        for match in db_fetch_matches(round[0]):
            matches.append(match)

    # print(matches)

    for player in players:

        # print(f"{player} se začne")
        hasplayed = [ None for match in matches if player in match ]

        temp_player = glicko2.Player(
            rating = players.get(player)[0],
            rd = players.get(player)[1],
            vol = players.get(player)[2]
        )

        if not hasplayed:
            # print(f"Player {player} hasn't played in the current tournament")
            # print("Old Rating: " + str(players.get(player)[0]))
            # print("Old Rating Deviation: " + str(players.get(player)[1]))
            # print("Old Volatility: " + str(players.get(player)[2]))
            temp_player.did_not_compete()
            newrating = (temp_player.rating, temp_player.rd, temp_player.vol)
            players_newrating.append(newrating)
            # print("New Rating: " + str(temp_player.rating))
            # print("New Rating Deviation: " + str(temp_player.rd))
            # print("New Volatility: " + str(temp_player.vol))
        else:

            if player in current_players:

                opponents_rating = []
                opponents_rd = []
                outcomes = []

                # print(f"Player {player} has played in the current tournament")
                # print("Old Rating: " + str(players.get(player)[0]))
                # print("Old Rating Deviation: " + str(players.get(player)[1]))
                # print("Old Volatility: " + str(players.get(player)[2]))

                for match in matches:
                    if match[1] == None:
                        continue
                    elif match[0] == player:
                        if match[5] == 2:
                            # print("Draw "+str(match))
                            opponents_rating.append(players[match[1]][0])
                            opponents_rd.append(players[match[1]][1])
                            outcomes.append(int(0.5))
                        else:
                            # print("Win "+str(match))
                            opponents_rating.append(players[match[1]][0])
                            opponents_rd.append(players[match[1]][1])
                            outcomes.append(int(1))
                    elif match[1] == player:
                        if match[5] == 2:
                            # print("Draw "+str(match))
                            opponents_rating.append(players[match[0]][0])
                            opponents_rd.append(players[match[0]][1])
                            outcomes.append(int(0.5))
                        else:
                            # print("Loss "+str(match))
                            opponents_rating.append(players[match[0]][0])
                            opponents_rd.append(players[match[0]][1])
                            outcomes.append(int(0))


                temp_player.update_player([x for x in opponents_rating],
                    [x for x in opponents_rd], outcomes)
                newrating = (temp_player.rating, temp_player.rd, temp_player.vol)
                players_newrating.append(newrating)
                # print("New Rating: " + str(temp_player.rating))
                # print("New Rating Deviation: " + str(temp_player.rd))
                # print("New Volatility: " + str(temp_player.vol))


        # print(f"{player} se konča")



    newplayers = dict(zip(players_dci, players_newrating))

    # print(players_newrating)

    for player in newplayers:
        db_update_glicko(
            int(player),
            str(newplayers.get(player)[0]),
            str(newplayers.get(player)[1]),
            str(newplayers.get(player)[2])
        )

def check_duplicate():

    # Check if the tournament is already in database.

    tournament_uid = str(json_data["event"]["@eventguid"])
    if db_duplicate_check(tournament_uid) == None:
        tournament_to_db()
        players_to_db()
        rounds_matches_to_db()
        players_to_tournaments()
        print(f"Tournament ID {tournament_uid} successfully entered into the database!")
        update_glicko()
        print(f"Glicko ratings for {tournament_uid} successfully updated!")
    elif tournament_uid == db_duplicate_check(tournament_uid)[0]:
        print(f"Tournament ID {tournament_uid} already exists in the database!")

parse_all()
# update_glicko()
