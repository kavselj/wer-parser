from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import json
import xmltodict
import os
from discord_webhook import DiscordWebhook, DiscordEmbed

window = Tk()

#This is where we lauch the file manager bar.
def OpenFile():
    name = askopenfilename(initialdir="c:/",
                           filetypes =(("WER file", "*.wer"),("All Files","*.*")),
                           title = "Choose a file."
                           )
    print(name)
    #Using try in case user types in unknown file or closes without choosing a file.

    def wertojson(name):
        with open(name, encoding="utf-8") as werdata:
            global json_data
            json_data = json.loads(json.dumps(xmltodict.parse(werdata.read()), indent=1))

    def players():
        global plist
        plist = []
        dci = []
        names = []

        person_list = json_data["event"]["participation"]["person"]
        for person in person_list:
            dci.append(person["@id"])
            names.append(person["@first"]+" "+person["@last"])
        players = dict(zip(dci, names))

        round_list = json_data["event"]["matches"]["round"]

        try:
            if round_list["@number"] == "1":
                for match in round_list["match"]:
                    if match["@win"] == "-1":
                        plist.append("**"+players.get(match["@person"], "")+"** // **"+players.get(match["@opponent"], "")+"**")
                        plist.append("**"+players.get(match["@opponent"], "")+"** // **"+players.get(match["@person"], "")+"**")

        # I'm sure there's a more elegant solution than forcing the TypeError
        # but due to the structure of the .wer file, I can't think of a
        # better way right now.

        except:
            for round in round_list:
                match = round["match"]
                for f in match:
                    if f["@win"] == "-1":
                        plist.append("**"+players.get(f["@person"], "")+"** // **"+players.get(f["@opponent"], "")+"**")
                        plist.append("**"+players.get(f["@opponent"], "")+"** // **"+players.get(f["@person"], "")+"**")

        # TODO: Add players discord handle to ping them directly

        # with open("pairings.txt", 'w', encoding="utf-8") as f:
        #     f.write('\n'.join(sorted(plist)))
        print("Pairings successfully posted!")

    def post_pairings():

        pairs = "**Player 1** // **Player 2**\n\n"+str("\n".join(str(x) for x in sorted(plist)))
        # players1 = str("\n".join(str(x) for x in p1))
        # opponents = str("\n".join(str(x) for x in p2))

        webhook = DiscordWebhook(url='ENTER WEBHOOK URL', content=pairs)

        # embed = DiscordEmbed(color=0x006400)
        # embed.add_embed_field(name='Player 1 // Player 2', value=pairs)
        # embed.add_embed_field(name='Player 2', value=opponents, inline=True)

        # webhook.add_embed(embed)
        webhook.execute()

    try:
        wertojson(name)
        players()
        post_pairings()
    except:
        print("No file exists")

Title = window.title( "WER Parser 0.1")

openparse=Button(window,text="Open & Parse",command=OpenFile,height=5,width=20)
openparse.grid(row=0,column=0)

# postpairs=Button(window,text="Post to Discord",command=post_pairings,height=5,width=20)
# postpairs.grid(row=0,column=1)

close=Button(window,text="Exit",command=lambda:exit(),height=5,width=20)
close.grid(row=0,column=1)

#Menu Bar

menu = Menu(window)
window.config(menu=menu)

file = Menu(menu)

file.add_command(label = 'Exit', command = lambda:exit())

menu.add_cascade(label = 'File', menu = file)

window.mainloop()
