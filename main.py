#!/usr/bin/python
# -*- coding: UTF-8 -*-
# system imports
import asyncio
import xmltodict
import requests
import sqlite3
import json

from discord.ext.commands import Bot

# local imports
import players

# settings
BOT_PREFIX = ("|", "!")
BOT_TOKEN = "NTQ2MjUyMTcxMjI2OTA2NjU0.D0lhTw.D-yjfvCYulT8hY5fXlrcjXy_Iw0"


# define db helper functions
def open_db(db_filename):
    """
    :param db_filename: file name of database
    :return: connection to database (sqlite.connect object)
    """
    conn = sqlite3.connect(db_filename)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS players (uid INTEGER NOT NULL UNIQUE, firstname TEXT NOT NULL, "
                "lastname TEXT NOT NULL, discordnick TEXT NOT NULL, PRIMARY KEY(uid))")
    conn.commit()
    return conn


def db_insert_player(db_connection, dci_number, firstname, lastname, discordnick):
    """
    :param db_connection: connection returned by open_db function
    :param dci_number: unique ID
    :param firstname: first name, duh
    :param lastname: last name, duh
    :param discordnick: discord nick + unique #. this can be also be a unique number ID returned by discord's API
    :return: nothing
    """
    cur = db_connection.cursor()
    cur.execute("INSERT OR IGNORE INTO players VALUES (?,?,?,?)", (dci_number, firstname, lastname, discordnick))
    db_connection.commit()


def db_get_player_translation_dictionary(db_connection):
    """
    :param db_connection: database connection returned by open_db function
    :return: a dictionary in the following format:
    {
        f"{firstname} {lastname}": f"{discordnick}"  # values from DB
    }
    this dictionary is later used to match WER pairings output with a discord nickname.
    Note that č/ž/š should all be c/z/s for simplicity's sake
    """
    # fetch data from players table
    # and make a dict out of it
    cur = db_connection.cursor()
    cur.execute("SELECT firstname, lastname, discordnick FROM players")
    player_raw_data = cur.fetchall()
    player_data = dict()
    for player in player_raw_data:
        # "{firstname} {lastname}": discordnick
        player_data[f"{player[0]} {player[1]}".title()] = player[2].title()
    return player_data


def db_close(db_connection):
    """
    :param db_connection: db connection to close
    :return: nothing
    """
    db_connection.commit()
    db_connection.close()


# start the client
client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print("*" * 10)


@client.command(name="send_pairings",
                brief="sends PMs with pairings to all participants",
                description=""", sends PMs with pairings to all participants
                            Syntax:
                            !send_pairings <attach WER file>
                            !pairings <attach WER file>
                            """,
                aliases=["pairings"],
                pass_context=True)
async def send_pairings(context):
    # this command expects an attached WER file and parses its contents then sends out pairings
    channel = context.message.channel

    # obtain attachment
    try:
        wer_file = context.message.attachments[0]
    except IndexError:
        await client.send_message(channel, "Ni priponke. Pripni .WER file sporočilu \"!pairings\"")

    # fetch contents
    loop = asyncio.get_event_loop()
    fetch_loop = loop.run_in_executor(None, requests.get, wer_file["url"])
    fetch_response = await fetch_loop
    wer_file_text = fetch_response.text

    # make data out of it
    try:
        json_data = json.loads(json.dumps(xmltodict.parse(wer_file_text), indent=1))
    except Exception as e:
        print(f"Exception pri parsanju WER fajla: {e}")
        await client.send_message(channel, "Priponka ni pravilen WER file")

    conversion_dict = db_get_player_translation_dictionary(db)

    pairs = []
    dci_numbers = []
    player_names = []
    # wer file persons list
    #     `.           ____....-"--"""".__
    #                 |            `    |        __  __________  ___  ____
    #       (         `._....------.._.:        /  |/  / __/ _ \/ _ \/ __/
    #        )         .()''        ``().      / /|_/ / _// , _/ // / _/
    #       '          () .=='  `===  `-.     /_/  /_/___/_/|_/____/___/
    #        . )       (  (👁     👁)   )
    #         )         )     /        J
    #        (          |.   /      . (
    #        $$         (.  (_'.   , )|`
    #        ||         |\`-....--'/  ' \
    #       /||.         \\ | | | /  /   \.
    #      //||(\         \`-===-'  '     \o.
    #     .//7' |)         `. --   / (     OObaaaad888b.
    #     (<<. / |     .a888b`.__.'d\     OO888888888888a.
    #      \  Y' |    .8888888aaaa88POOOOOO888888888888888.
    #       \  \ |   .888888888888888888888888888888888888b
    #        |   |  .d88888P88888888888888888888888b8888888.
    #        b.--d .d88888P8888888888888888a:f888888|888888b
    #        88888b 888888|8888888888888888888888888\8888888
    persons_wer_list = json_data["event"]["participation"]["person"]
    # print(persons_wer_list)
    for person in persons_wer_list:
        # get dci number and first+last name and save them for later use
        dci_numbers.append(person["@id"])
        player_names.append(person["@first"] + " " + person["@last"])

    players_dict = dict(zip(dci_numbers, player_names))

    round_list = json_data["event"]["matches"]["round"]
    try:
        if isinstance(round_list, dict):
            for player_info in round_list["match"]:
                if player_info["@win"] == "-1":
                    pairs.append((players_dict.get(player_info["@person"], ""),
                                  players_dict.get(player_info["@opponent"], "")))
        elif isinstance(round_list, list):
            for player_info in round_list[-1]["match"]:
                if player_info["@win"] == "-1":
                    pairs.append((players_dict.get(player_info["@person"], ""),
                                  players_dict.get(player_info["@opponent"], "")))
    except Exception as e:
        print(f"failed: {e}")

    # convert pairs to messages
    print(conversion_dict)
    print(pairs)
    messages = {}
    try:
        for pair in pairs:
            for player in pair:
                player = player.title()
                if player in conversion_dict:
                    opponent = [x for x in pair if x != player][0]
                    messages[conversion_dict[player]] = f"Igraš s/z: {opponent}"
    except Exception as e:
        print(e)

    print(messages)

    # send DMs
    # get all members
    all_members = client.get_all_members()

    for member in all_members:
        nick = member.name + "#" + member.discriminator
        if nick in messages:
            user = await client.get_user_info(member.id)
            print(f"Posiljam sporocilo uporabniku: {nick}")
            await client.send_message(user, messages[nick])


if __name__ == "__main__":
    # start the client
    client = Bot(command_prefix=BOT_PREFIX)
    # prepare db. note that if you have to fix anything for an existing entry,
    # you have to delete kartologi.db.
    db_name = "kartologi.db"
    db = open_db(db_name)
    print(f"Opened database file: '{db_name}'")

    for player in players.players:
        db_insert_player(db, **players_description[player])
        print(f"inserted '{player}' into DB.")

    client.run(BOT_TOKEN)
