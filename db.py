import sqlite3

def create_table():

    conn = sqlite3.connect("lite.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS players (uid INTEGER NOT NULL UNIQUE, firstname TEXT NOT NULL, lastname TEXT NOT NULL, country TEXT NOT NULL, PRIMARY KEY(uid))")
    cur.execute("CREATE TABLE IF NOT EXISTS tournaments (uid TEXT NOT NULL UNIQUE, date TEXT NOT NULL, format TEXT NOT NULL, rounds_total INTEGER NOT NULL, PRIMARY KEY(uid))")
    cur.execute("CREATE TABLE IF NOT EXISTS rounds (uid TEXT NOT NULL UNIQUE, time TEXT NOT NULL, number INTEGER NOT NULL, tournament_uid TEXT NOT NULL, PRIMARY KEY(uid))")
    cur.execute("CREATE TABLE IF NOT EXISTS matches (uid TEXT NOT NULL UNIQUE, round_uid TEXT NOT NULL, player_uid TEXT NOT NULL, opponent_uid TEXT, win INTEGER NOT NULL, loss INTEGER NOT NULL, draw INTEGER NOT NULL, outcome INTEGER NOT NULL, PRIMARY KEY(uid))")
    cur.execute("CREATE TABLE IF NOT EXISTS players_to_tournaments (player_uid INTEGER NOT NULL, tournament_uid TEXT NOT NULL, deck TEXT NOT NULL, PRIMARY KEY(player_uid,tournament_uid))")
    conn.commit()
    conn.close()

def db_insert_players(uid,firstname,lastname,country):
    conn = sqlite3.connect("lite.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO players VALUES (?,?,?,?)",(uid,firstname,lastname,country))
    conn.commit()
    conn.close()

def db_insert_tournament(uid,date,format,rounds_total):
    conn = sqlite3.connect("lite.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO tournaments VALUES (?,?,?,?)",(uid,date,format,rounds_total))
    conn.commit()
    conn.close()

def db_insert_rounds(uid,time,number,tournament_uid):
    conn = sqlite3.connect("lite.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO rounds VALUES (?,?,?,?)",(uid,time,number,tournament_uid))
    conn.commit()
    conn.close()

def db_insert_matches(uid,round_uid,player_uid,opponent_uid,win,loss,draw,outcome):
    conn = sqlite3.connect("lite.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO matches VALUES (?,?,?,?,?,?,?,?)",(uid,round_uid,player_uid,opponent_uid,win,loss,draw,outcome))
    conn.commit()
    conn.close()

def db_insert_players_to_tournaments(player_uid,tournament_uid,deck):
    conn = sqlite3.connect("lite.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO players_to_tournaments VALUES (?,?,?)",(player_uid,tournament_uid,deck))
    conn.commit()
    conn.close()

create_table()
