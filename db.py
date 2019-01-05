import sqlite3

def create_table():

    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS players (uid INTEGER NOT NULL UNIQUE, firstname TEXT NOT NULL, lastname TEXT NOT NULL, country TEXT NOT NULL, PRIMARY KEY(uid))")
    cur.execute("CREATE TABLE IF NOT EXISTS tournaments (uid TEXT NOT NULL UNIQUE, date TEXT NOT NULL, format TEXT NOT NULL, rounds_total INTEGER NOT NULL, PRIMARY KEY(uid))")
    cur.execute("CREATE TABLE IF NOT EXISTS rounds (uid TEXT NOT NULL UNIQUE, time TEXT NOT NULL, number INTEGER NOT NULL, tournament_uid TEXT NOT NULL, PRIMARY KEY(uid))")
    cur.execute("CREATE TABLE IF NOT EXISTS matches (uid TEXT NOT NULL UNIQUE, round_uid TEXT NOT NULL, player_uid TEXT NOT NULL, opponent_uid TEXT, win INTEGER NOT NULL, loss INTEGER NOT NULL, draw INTEGER NOT NULL, outcome INTEGER NOT NULL, PRIMARY KEY(uid))")
    cur.execute("CREATE TABLE IF NOT EXISTS players_to_tournaments (player_uid INTEGER NOT NULL, tournament_uid TEXT NOT NULL, deck_uid TEXT NOT NULL, PRIMARY KEY(player_uid,tournament_uid,deck_uid))")
    cur.execute("CREATE TABLE IF NOT EXISTS decks (uid TEXT NOT NULL UNIQUE, deckname TEXT NOT NULL UNIQUE, PRIMARY KEY(uid))")
    conn.commit()
    conn.close()

def db_insert_players(uid,firstname,lastname,country):
    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO players VALUES (?,?,?,?)",(uid,firstname,lastname,country))
    conn.commit()
    conn.close()

def db_insert_tournament(uid,date,format,rounds_total):
    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO tournaments VALUES (?,?,?,?)",(uid,date,format,rounds_total))
    conn.commit()
    conn.close()

def db_insert_rounds(uid,time,number,tournament_uid):
    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO rounds VALUES (?,?,?,?)",(uid,time,number,tournament_uid))
    conn.commit()
    conn.close()

def db_insert_matches(uid,round_uid,player_uid,opponent_uid,win,loss,draw,outcome):
    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO matches VALUES (?,?,?,?,?,?,?,?)",(uid,round_uid,player_uid,opponent_uid,win,loss,draw,outcome))
    conn.commit()
    conn.close()

def db_insert_players_to_tournaments(player_uid,tournament_uid,deck_uid):
    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO players_to_tournaments VALUES (?,?,?)",(player_uid,tournament_uid,deck_uid))
    conn.commit()
    conn.close()

def db_duplicate_check(tournament_uid):
    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("SELECT uid FROM tournaments WHERE uid=?",(tournament_uid,))
    t_uid=cur.fetchone()
    conn.close()
    return t_uid

def db_insert_decks(uid,deckname):
    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO decks VALUES (?,?)",(uid,deckname))
    conn.commit()
    conn.close()

def db_deck_check(deckname):
    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("SELECT uid FROM decks WHERE deckname=?",(deckname,))
    deck_uid=cur.fetchone()
    conn.close()
    return deck_uid

def db_check_date(date):
    conn = sqlite3.connect("kartologi.db")
    cur = conn.cursor()
    cur.execute("SELECT uid FROM tournaments WHERE date=?",(date,))
    t_uid=cur.fetchone()
    conn.close()
    return t_uid

create_table()
