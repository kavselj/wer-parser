na vrhu fajla main.py imaš nastavitve (nč pipat prosm)

        # settings
        BOT_PREFIX = ("|", "!")
        BOT_TOKEN = "*****"

pred definicijo komande !pairings imaš:
        
        # start the client
        client = Bot(command_prefix=BOT_PREFIX)

v main.py imaš naslednjo kodo, ki se požene:

    if __name__ == "__main__":
        # prepare db. note that if you have to fix anything for an existing entry,
        # you have to delete kartologi.db. improved implementation will follow
        db_name = "kartologi.db"
        db = open_db(db_name)
        print(f"Opened database file: '{db_name}'")
    
        for player in players.players:
            # file players.py contains entries for all players, edit at
            # your discretion
            db_insert_player(db, **players_description[player])
            print(f"inserted '{player}' into DB.")
        
        client.run(BOT_TOKEN)


fajli:
    
    .gitignore = gitignore, predvidevam da veš kaj dela, dodal sem standarden python template poleg že obstoječih zadev
    
    __init__.py = predvidevam da veš kaj to dela, stvar sem spisal "kot se šika", če/ko se bo stvar razvijala dalje
    
    main.py = logika je spisana tukaj
    
    players.py = file, ki vsebuje dict za opis igralcev
    
    
kako poženeš bota:

    python main.py

kako poženeš pairings:

    pošlješ "!pairings" + attachas .WER file v channel, ki ga bot posluša. najbolje, da bota po končanem delu ugasneš.
    
