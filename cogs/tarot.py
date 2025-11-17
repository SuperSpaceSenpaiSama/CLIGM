"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.4.0
"""
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import os, random
import math
from PIL import Image
from typing import List
import time

SHORTMAJOR = [
    "0-Fool",
    "I-Magi",
    "II-HP",
    "III-Emps",
    "IV-Emp",
    "V-Hiero",
    "VI-Love",
    "VII-Char",
    "VIII-Str",
    "IX-Herm",
    "X-Wheel",
    "XI-Justc",
    "XII-Hang",
    "XIII-Dth",
    "XIV-Temp",
    "XV-Devil",
    "XVI-Towr",
    "XVII-Star",
    "XVIII-Moon",
    "XIX-Sun",
    "XX-Judge",
    "XXI-World"
]

MAJORNAME = [
    "Fool",
    "I - The Magician",
    "II - The High Priestess",
    "III - The Empress",
    "IV - The Emperor",
    "V - The Hierophant",
    "VI - The Lovers",
    "VII - The Chariot",
    "VIII - Strength",
    "IX - The Hermit",
    "X - The Wheel of Fortune",
    "XI - Justice",
    "XII - The Hanged Man",
    "XIII - Death",
    "XIV - Temperance",
    "XIV - The Devil",
    "XVI - The Tower",
    "XVII - The Stars",
    "XVIII - The Moon",
    "XIX - The Sun",
    "XX - Judgement",
    "XXI - The World"
]

VALUENAME = [
    "",
    "Ace of ",
    "Two of ",
    "Three of ",
    "Four of ",
    "Five of ",
    "Six of ",
    "Seven of ",
    "Eight of ",
    "Nine of ",
    "Ten of ",
    "Page of ",
    "Knight of ",
    "Queen of ",
    "King of ",
]

IMGDIR = "tarot/"
IMGDIR_FLIPPED = "tarot_flipped/"

MERGEDIMG = "mergedimage.png"

#the colors used for embed messages
INVISCOLOR = 0x350080
NEUTRALCOLOR = 0xBEBEFE
PLAYERCOLOR = 0x04BF22
GMCOLOR = 0xF5DA27
ERRORCOLOR = 0xBE0000
BATTLECOLOR = 0xFE7777

def merge_images(filelist):
    maxcol = 6 #maximum number of cards per row
    gap_percent = 0.05 # how much space between each card, based off its width

    imagelist = []
    for f in filelist:
        imagelist.append(Image.open(f))

    #we are assuming that all card pics are of the same dimensions
    (card_w, card_h) = imagelist[0].size
    cardcount = len(imagelist)
    gap = round(card_w * gap_percent)

    final_w = 0
    final_h = 0
    if cardcount < maxcol:
        final_w = (card_w * cardcount) + (gap * (cardcount - 1))
        final_h = card_h
    else:
        rowcnt = math.ceil(cardcount/maxcol)
        final_w = (card_w * maxcol) + (gap * (maxcol - 1))
        final_h = (card_h * rowcnt) + (gap * (rowcnt - 1))

    result = Image.new('RGBA', (final_w, final_h))

    x=0
    y=0
    xmul = card_w + gap
    ymul = card_h + gap
    for img in imagelist:
        result.paste(im=img, box=(x*xmul, y*ymul))

        x += 1
        if x == maxcol:
            x = 0
            y += 1

    result.save(IMGDIR + MERGEDIMG, "PNG")

def merge_sideways(imagefile):
    #this command always merges one upright card with the sidewaysback.png card.
    gap_percent= 0.05


    image1 = Image.open(imagefile)
    image2 = Image.open("tarot/sidewaysbacks.png")

    (w1, h1) = image1.size
    (w2, h2) = image2.size
    gap = round(gap_percent * w1)

    final_w = w1 + gap + w2
    final_h = h1

    result = Image.new('RGBA', (final_w, final_h))

    result.paste(im=image1, box=(0,0))
    result.paste(im=image2, box=(w1 + gap, final_h - h2))

    result.save(IMGDIR + MERGEDIMG, "PNG")




class Card():
    def __init__(self, name, suit, value):
        self.name = name  #The full name of the card
        self.suit = suit  #The suit.  can be  wands, pentacles, cups, swords or major
        self.value = value #The value. is 1 for Aces, 11 for Pages, 12 for Knights, 13 for Queens, 14 for Kings, and 0 for The Fool
        self.is_reversed = False #whether the card is reversed or not. doesn't really affect rules'
        self.filename = self.suit + str(self.value).zfill(2) + ".png" #The filename to the card's corresponding picture

        self.is_main = True #whether the card was played as a main action or not. ONLY matters for facedown cards.

        self.is_up = False #whether the card has been flipped and thus visible. ONLY matters for initiative cards.

    def short_print(self): #prints the card in a shorthand manner
        if self.suit == "major":
            return SHORTMAJOR[self.value]
        else:
            shortval = ""
            if 1 < self.value <= 10:
                shortval = string(self.value)
            elif self.value == 1:
                shortval = "A"
            elif self.value == 11:
                shortval = "P"
            elif self.value == 12:
                shortval = "Kn"
            elif self.value == 13:
                shortval = "Q"
            elif self.value == 14:
                shortval = "K"

            shortsuit = ""
            if self.suit == "wands":
                shortsuit = "W"
            elif self.suit == "pentacles":
                shortsuit = "P"
            elif self.suit == "cups":
                shortsuit = "C"
            elif self.suit == "swords":
                shortsuit = "S"

            return shortval + shortsuit

    def get_filepath(self): #gets the filepath for the card, depending on if it is flipped or not
        if self.is_reversed:
            return IMGDIR_FLIPPED + self.filename
        else:
            return IMGDIR + self.filename


class Deck():
    def __init__(self, major):
        self.drawpile = []
        self.discardpile = []
        self.hands = {}
        self.facedowns = {} # a dict for the facedown cards of monsters/adventurers
        self.initiatives = {} # a dict for the initiative cards of monsters/adventurers

        if major: # major is true,  this is the GM's deck. All Major arcana save for fool
            for i in range(1,22):
                self.drawpile.append(Card(MAJORNAME[i], "major", i))

        else: #major is false, this is the Players' deck. All Minor arcana plus fool
            self.drawpile.append(Card(MAJORNAME[0], "major", 0))
            for i in range(1,15):
                self.drawpile.append(Card(VALUENAME[i] + "Wands", "wands", i))
                self.drawpile.append(Card(VALUENAME[i] + "Pentacles", "pentacles", i))
                self.drawpile.append(Card(VALUENAME[i] + "Cups", "cups", i))
                self.drawpile.append(Card(VALUENAME[i] + "Swords", "swords", i))

    def shuffle(self):
            #just needs to pop all elements of discardpile and return them to the drawpile.
            while len(self.discardpile) > 0:
                crd = self.discardpile.pop()
                self.drawpile.append(crd)

            #hands should  probably not be shuffled in by default
            #
            #for player in self.hands:
            #    while len(hands[player]) > 0:
            #        crd = hands[player].pop()
            #        self.drawpile.append(crd)


    def draw(self):
        msg = ""
        if len(self.drawpile) == 0:
            return (None, "NOCARD")
        elif len(self.drawpile) == 1:
            msg = "LASTCARD"
        else:
            msg = "OK"
        drawncard = self.drawpile.pop(random.randint(0,len(self.drawpile) - 1)) # draws a random card from the deck, removing it from drawpile
        if drawncard.suit == "major" and drawncard.value == 0:
            #if the card is The Fool, report that instead
            msg = "FOOL"
        self.discardpile.append(drawncard) # adds the card to the discard pile

        drawncard.is_reversed = bool(random.getrandbits(1)) #coinflip on whether card is reversed or not upon drawing


        return (drawncard, msg)  # returns the card that was drawn, and a status message!

    def show_discard(self):
        #shows the top card of the discard pile
        if len(self.discardpile) != 0:
            return (self.discardpile[-1], "")
        else:
            return ("", "NOCARD")

    def deal_cards(self, cardcount, username):
        #first, check if the player has a hand list already. if not, create it
        if username not in self.hands:
            self.hands[username] = []

        msg = ""
        cnt = 0
        for i in range(cardcount):
            if len(self.drawpile) == 0:
               #lets the command know that the deck had to be shuffled to get the last i cards
               msg = "SHUFFLED"
               cnt = i
               self.shuffle()
               if len(self.drawpile) == 0:
                   #if the drawpile is STILL empty right after shuffling, that means all cards are in someone's hands. this should never happen, return an error code anyways
                    msg = "NOCARD"
                    break
            crd = self.drawpile.pop(random.randint(0,len(self.drawpile) - 1)) #draws a random card from the deck, as many times as needed
            crd.is_reversed = bool(random.getrandbits(1)) #coinflip on if card is reversed. No mechanical diff, just flavoring

            self.hands[username].append(crd) #adds the card to the user's hand

        return (msg, cnt)

    def seek(self, username, value, suit):
        #tries to find a specific card in the discard pile and draw it into username's hand
        if username not in self.hands:
            self.hands[username] = []

        for i in range(len(self.discardpile)):
            if self.discardpile[i].value == value and self.discardpile[i].suit == suit:
                card = self.discardpile.pop(i)
                self.hands[username].append(card)

                return (card, "")
        # if the card wasn't in the discard pile...
        return ("", "NOCARD")


    def debug_seek(self, username, value, suit, destination):
        #tries to find a specific card in the discard pile and draw it into username's hand
        if username not in self.hands and destination == "hand":
            self.hands[username] = []

        #search the discard pile first
        card = None
        found_in = ""
        for i in range(len(self.discardpile)):
            if self.discardpile[i].value == value and self.discardpile[i].suit == suit:
                card = self.discardpile.pop(i)
                found_in = "the discardpile"
                break

        #search drawpile next
        if card is None:
            for i in range(len(self.drawpile)):
                if self.drawpile[i].value == value and self.drawpile[i].suit == suit:
                    card = self.drawpile.pop(i)
                    found_in = "the drawpile"
                    break

        #last, search hands
        found = False
        if card is None:
            for p in self.hands:
                hand = self.hands[p]
                for i in range(len(hand)):
                    if hand[i].value == value and hand[i].suit == suit:
                        card = hand.pop(i)
                        found_in = p + "'s hand"
                        break
                if card is not None:
                    break


        if card is not None:
            if destination == "draw":
                self.drawpile.append(card)
            elif destination == "discard":
                self.discardpile.append(card)
            else:
                self.hands[username].append(card)

            return (card, found_in)


        # if the card wasn't in the discard pile...
        return ("", "NOCARD")


    def play_card(self, val, suit, username):

        if not self.has_hand(username):
            return ("","HANDEMPTY")

        hand = self.hands[username]
        #first, we need to check if the card is in this player's hand
        cardindex = -1

        found = False
        for i in range(len(hand)):
            if hand[i].value == val and hand[i].suit == suit:
                found = True
                cardindex = i
                break

        if not found:
            return ("","NOCARD")

        #now that we know the card is in the player's hand, return it to the discard pile and then return it!
        played = hand.pop(cardindex)
        self.discardpile.append(played)

        self.cleanup_hand(username)

        return (played, "")

    def has_fool(self, username):
        #checks if a player has The Fool. used to check for the /play_fool command without causing any irreversible changes first.
        if not self.has_hand(username):
            return "HANDEMPTY"

        msg = "NO"
        for i in range(len(hand)):
            if hand[i].value == 0: #just need to check this, THe Fool is the only card in the Minor deck with a value of 0
                msg = "YES"
                break
        return msg

    def has_hand(self, username):
        #checks if the player has a hand or not.
        if username not in self.hands:
            return False
        elif len(self.hands[username]) == 0:
            return False
        else:
            return True

    def flush(self, username):
        #flushes every card in a player's hand into the discard pile.
        discardlist = []
        if username in self.hands:
            hand = self.hands[username]
            while len(hand) != 0:
                card = hand.pop()
                discardlist.append(card)
                self.discardpile.append(card)

        self.cleanup_hand(username)
        return discardlist

    def cleanup_hand(self, username):
        #get rid of empty hands  to save on space
        if username in self.hands:
            if len(self.hands[username]) == 0:
                del self.hands[username]


    #here start the methods for facedown cards!
    #facedown cards are keyed by the username for adventurers, and by the inputed monster name for GM monsters
    #username is used for the GM, primarily
    def play_facedown(self, username, charname, val: int, suit: str, main: bool):
        #first, check if they already have a facedown card.
        if charname in self.facedowns:
            return ("", "HASFACEDOWN")

        #then, check if they actually have the card they want to play facedown
        if not self.has_hand(username):
            return ("","HANDEMPTY")

        hand = self.hands[username]
        cardindex = -1

        found = False
        for i in range(len(hand)):
            if hand[i].value == val and hand[i].suit == suit:
                found = True
                cardindex = i
                break

        if not found:
            return ("","NOCARD")

        #if both of these are true, we can play the card facedown. Remove it from the hand and set it as the adventurer's/monster's facedown. Change its main status if needed
        card = hand.pop(cardindex)
        card.is_main = main
        self.facedowns[charname] = card

        #since we got rid of a card, check for hand cleanup
        self.cleanup_hand(username)

        return (card, "")

    def discard_facedown (self, charname):
        if charname not in self.facedowns:
            return ("", "NOCARD")
        else:
            card = self.facedowns.pop(charname)
            self.discardpile.append(card)
            return (card, "")


    #here start the methods for initiative cards!  Kind of similar to Facedown cards, in most respects
    def set_initiative(self, username, charname, val: int, suit: str):
        #first, check if they already have an initiative card.
        if charname in self.initiatives:
            return ("", "HASFACEDOWN")

        #then, check if they actually have the card they want to play as initiative
        if not self.has_hand(username):
            return ("","HANDEMPTY")

        hand = self.hands[username]
        cardindex = -1

        found = False
        for i in range(len(hand)):
            if hand[i].value == val and hand[i].suit == suit:
                found = True
                cardindex = i
                break

        if not found:
            return ("","NOCARD")

        #if both of these are true, we can play the card as initiative. Remove it from the hand and set it as the adventurer's/monster's initiative. Change set is_up to False
        card = hand.pop(cardindex)
        card.is_up = False #initiative cards always begin unrevealed
        self.initiatives[charname] = card

        #since we got rid of a card, check for hand cleanup
        self.cleanup_hand(username)

        return (card, "")


    #does NOT pop the card, simply changes its is_up value
    def flip_initiative(self, charname):
        if charname not in self.initiatives:
            return("", "NOCARD")
        else:
            card = self.initiatives[charname]
            card.is_up = True
            return (card, "")

    def discard_initiative (self, charname):
        if charname not in self.initiatives:
            return("", "NOCARD")
        else:
            card= self.initiatives.pop(charname)
            self.discardpile.append(card)
            return (card, "")




# Here we name the cog and create a new class for the cog.
# class Template(commands.Cog, name="tarot"):
#     def __init__(self, bot) -> None:
#         self.bot = bot

#     # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

#     @commands.hybrid_command(
#         name="draw minor",
#         description="Draw a card from the player deck",
#     )
#     async def testcommand(self, context: Context) -> None:
#         random.choice(os.listdir(/tarot/minor/))

class Tarot(commands.Cog, name="tarot"):
    def __init__(self, bot) -> None:
        self.bot = bot

        #for now, we're just doing one deck across the entire bot for testing purposes.
        #Will do per-channel instances later.
        #self.gm_deck = Deck(major=True)
        #self.player_deck = Deck(major=False)

        self.gm_decks = {}
        self.player_decks = {}

        self.initiative = {} # a dict with channel ids as the keys

        self.gamemasters = {} # a dict with channel ids as the keys and User objects as the values

        self.userids = {} #a dict with usernames as the keys and userids as the values. Submitted via /initiative, cleared at /end_of_round
        self.usernicks = {}

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    def get_nick(self, user):
        nickname = ""
        if user.nick is not None:
            nickname = user.nick
        elif user.display_name is not None:
            nickname = user.display_name
        else:
            nickname = user.name
        return nickname

    def get_decks(self, channel):
        # for now, just returns the two deck attributes, This will be useful once the bot is built to handle multiple decks per channel
        #return (self.player_deck, self.gm_deck)


        if channel.id not in self.player_decks:
            self.player_decks[channel.id] = Deck(major=False)
        if channel.id not in self.gm_decks:
            self.gm_decks[channel.id] = Deck(major=True)

        return (self.player_decks[channel.id], self.gm_decks[channel.id])


    def get_initiative(self, channel):
        return self.initiative

    def get_gm(self, channel):
        if channel.id not in self.gamemasters:
            return None  # there is no gamemaster assigned to this channel
        return self.gamemasters[channel.id]

    async def show_hand(self, interaction: discord.Interaction, deck: Deck, player: str, prefix: str):
        desc = ""
        imagefiles = []
        rev = ""
        carddir = ""
        for card in deck.hands[player]:
            if card.is_reversed:
                rev = " **(R)**"
                carddir = IMGDIR_FLIPPED
            else:
                rev = ""
                carddir = IMGDIR
            desc += prefix + card.name + rev + "\n"
            imagefiles.append(carddir + card.filename)

        desc = desc[:-1] #removes the final \n character

        #sets up the embed image
        merge_images(imagefiles)
        img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)

        embed3 = discord.Embed(
            title = "You have drawn the following cards, " + self.get_nick(interaction.user) + ". Use them wisely!",
            description = desc,
            color = INVISCOLOR,
        )
        embed3.set_image(url="attachment://" + MERGEDIMG)

        await interaction.followup.send(embed=embed3, ephemeral = True, file=img)

    @commands.hybrid_command(
        name="clihello",
        description="Test bots response",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def clihello(self, context: Context) -> None:
        """
        Check if the bot is alive.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="Hiya!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=NEUTRALCOLOR,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="draw_minor",
        description="Draw a card from the player deck",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def draw_minor(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context.channel)
        result = minordeck.draw()

        if result[1] == "NOCARD":
            embed = discord.Embed(
                title = "The draw pile is empty, adventurer! You need to shuffle this deck!",
                color=ERRORCOLOR,
            )
            await context.send(embed=embed)
        else:

            desc = "You have drawn the "
            if result[0].is_reversed:
                desc += "**Reversed** *" + result[0].name + "*!"
            else:
                desc += "*" + result[0].name + "*!"

            if result[1] == "LASTCARD":
                desc = desc + "\nThis was the last card in the draw pile!"
            elif result[1] == "FOOL":
                desc = desc + "\nThe Fool demands that you shuffle your decks!"

            img = discord.File(result[0].get_filepath(), filename=result[0].filename)
            embed = discord.Embed(
                title="The adventurer " + self.get_nick(context.author) + " tests Fate...",
                description=desc,
                color=PLAYERCOLOR,
            )
            embed.set_image(url="attachment://" + result[0].filename)

            await context.send(file=img, embed=embed)


    @app_commands.command(
        name="draw_hidden_minor",
        description="Draw a card from the player deck without showing it to anyone else.",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def draw_hidden_minor(self, interaction: discord.Interaction) -> None:
        minordeck, majordeck = self.get_decks(interaction.channel)
        result = minordeck.draw()

        if result[1] == "NOCARD":
            embed = discord.Embed(
                title = "The draw pile is empty, gamemaster! You need to shuffle this deck!",
                color=ERRORCOLOR,
            )
            await interaction.respond.send_message(embed=embed)
        else:
            embed2 = discord.Embed(
                title = "The gamemaster " + self.get_nick(interaction.user) + " quietly draws a card without showing it to anyone...",
                description="Who knows what it means?...",
                color=GMCOLOR
            )
            await interaction.channel.send(embed=embed2)


            desc = "You have drawn the "
            if result[0].is_reversed:
                desc += "**Reversed** *" + result[0].name + "*!"
            else:
                desc += "*" + result[0].name + "*!"

            if result[1] == "LASTCARD":
                desc = desc + "\nThis was the last card in the draw pile!"
            elif result[1] == "FOOL":
                desc = desc + "\nThe Fool demands that you shuffle your decks!"

            img = discord.File(result[0].get_filepath(), filename=result[0].filename)
            embed = discord.Embed(
                title="You surreptitiously draw a card without showing it...",
                description=desc,
                color=GMCOLOR,
            )
            embed.set_image(url="attachment://" + result[0].filename)

            await interaction.response.send_message(file=img, embed=embed, ephemeral=True)


    @commands.hybrid_command(
        name="draw_major",
        description="Draw a card from the GM deck",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def draw_major(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context.channel)
        result = majordeck.draw()

        if result[1] == "NOCARD":
            embed = discord.Embed(
                title = "The draw pile is empty, gamemaster! You need to shuffle this deck!",
                color=ERRORCOLOR,
            )
            await context.send(embed=embed)
        else:

            desc = "You have drawn the "
            if result[0].is_reversed:
                desc += "**Reversed** *" + result[0].name + "*!"
            else:
                desc += "*" + result[0].name + "*!"

            if result[1] == "LASTCARD":
                desc = desc + "\nThis was the last card in the draw pile!"

            img = discord.File(result[0].get_filepath(), filename=result[0].filename)
            embed = discord.Embed(
                title="The gamemaster " + self.get_nick(context.author)+ " draws a card...",
                description=desc,
                color=GMCOLOR,
            )
            embed.set_image(url="attachment://" + result[0].filename)

            await context.send(file=img, embed=embed)



    @commands.hybrid_command(
        name="show_discard",
        description="Show the top card on the Players' discard pile",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def show_discard(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context.channel)
        topcard = minordeck.show_discard()

        if topcard[1] == "NOCARD":
            embed = discord.Embed(
                title = "The discard pile is empty! You need to draw some cards!",
                color=ERRORCOLOR,
            )
            await context.send(embed=embed)
        else:
            desc = "The top card in the players' discard pile is the "
            if topcard[0].is_reversed:
                desc += "**Reversed** *" + topcard[0].name + "*!"
            else:
                desc += "*" + topcard[0].name + "*!"

            img = discord.File(topcard[0].get_filepath(), filename=topcard[0].filename)
            embed = discord.Embed(
                title= self.get_nick(context.author) + " peeks at the top of the discard pile...",
                description=desc,
                color=NEUTRALCOLOR,
            )
            embed.set_image(url="attachment://" + topcard[0].filename)

            await context.send(file=img, embed=embed)



    @commands.hybrid_command(
        name="show_discard_major",
        description="Show the top card on the GM's discard pile",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def show_discard_major(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context.channel)
        topcard = majordeck.show_discard()

        if topcard[1] == "NOCARD":
            embed = discord.Embed(
                title = "The discard pile is empty! You need to draw some cards!",
                color=ERRORCOLOR,
            )
            await context.send(embed=embed)
        else:
            desc = "The top card in the GM's discard pile is the "
            if topcard[0].is_reversed:
                desc += "**Reversed** *" + topcard[0].name + "*!"
            else:
                desc += "*" + topcard[0].name + "*!"

            img = discord.File(topcard[0].get_filepath(), filename=topcard[0].filename)
            embed = discord.Embed(
                title= self.get_nick(context.author) + " peeks at the top of the discard pile...",
                description=desc,
                color=NEUTRALCOLOR,
            )
            embed.set_image(url="attachment://" + topcard[0].filename)

            await context.send(file=img, embed=embed)




    @commands.hybrid_command(
        name="shuffle_minor",
        description="shuffles the Players' discard pile back into the draw pile."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def shuffle_minor(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context.channel)
        minordeck.shuffle()

        img = discord.File(IMGDIR + "cardbacks.png", filename="cardbacks.png")
        embed = discord.Embed(
            title= self.get_nick(context.author) + " shuffles the Players' deck...",
            description = "Now you can draw again, and test your fate...",
            color=PLAYERCOLOR,
        )
        embed.set_image(url="attachment://cardbacks.png")

        await context.send(file=img, embed=embed)



    @commands.hybrid_command(
        name="shuffle_major",
        description="shuffles the GM's discard pile back into the draw pile."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def shuffle_major(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context.channel)
        majordeck.shuffle()

        img = discord.File(IMGDIR + "cardbacks.png", filename="cardbacks.png")
        embed = discord.Embed(
            title= self.get_nick(context.author) + " shuffles the GM's deck...",
            description = "Now you can draw again, and herald disaster...",
            color=GMCOLOR,
        )
        embed.set_image(url="attachment://cardbacks.png")

        await context.send(file=img, embed=embed)



    @commands.hybrid_command(
        name="shuffle_both",
        description="shuffles both discard piles back into their respective draw piles."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def shuffle_both(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context.channel)
        minordeck.shuffle()
        majordeck.shuffle()

        img = discord.File(IMGDIR + "cardbacks.png", filename="cardbacks.png")
        embed = discord.Embed(
            title= self.get_nick(context.author) + " shuffles both decks...",
            description = "Now you can draw again, and weave our tale...",
            color=NEUTRALCOLOR,
        )
        embed.set_image(url="attachment://cardbacks.png")

        await context.send(file=img, embed=embed)




    @commands.hybrid_command(
        name="debug",
        description="Show the status of all decks for debug purposes",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def debug(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context.channel)

        gamemaster = self.get_gm(context.channel)
        if gamemaster is None or context.author.name != gamemaster.name:
            embed = discord.Embed(
                title = "Only the Gamemaster can use this command!",
                description = "Please ask your GM about it.",
                color = ERRORCOLOR
            )
            await context.send(embed=embed)
            return None

        desc = "**PLAYER DRAWPILE:**"

        for card in minordeck.drawpile:
            desc += "\n" + card.name + ", " + card.suit + ", " + str(card.value)

        desc += "\n\n**PLAYER DISCARD PILE:**"

        for card in minordeck.discardpile:
            desc += "\n" + card.name + ", " + card.suit + ", " + str(card.value)

        desc += "\n\n**PLAYER HANDS**"

        for player in minordeck.hands:
            desc += "\n**Hand of " + player +":**"

            for card in minordeck.hands[player]:
                desc += "\n  - " + card.name

        desc += "\n\n**GM DRAWPILE:**"

        for card in majordeck.drawpile:
            desc += "\n" + card.name + ", " + card.suit + ", " + str(card.value)

        desc += "\n\n**GM DISCARD PILE:**"

        for card in majordeck.discardpile:
            desc += "\n" + card.name + ", " + card.suit + ", " + str(card.value)

        desc += "\n\n**GM HANDS**"

        for player in majordeck.hands:
            desc += "\n**Hand of " + player +":**"

            for card in majordeck.hands[player]:
                desc += "\n  - " + card.name

        desc += "\n\n**FACEDOWN CARDS:**"

        for char in minordeck.facedowns:
            desc += "\n" + char + ": " + minordeck.facedowns[char].name + ", is_main: " + str(minordeck.facedowns[char].is_main)

        for char in majordeck.facedowns:
            desc += "\n" + char + ": " + majordeck.facedowns[char].name + ", is_main: " + str(majordeck.facedowns[char].is_main)


        desc += "\n\n**INITIATIVE CARDS:**"

        for char in minordeck.initiatives:
            desc += "\n" + char + ": " + minordeck.initiatives[char].name + ", is_up: " + str(minordeck.initiatives[char].is_up)
        for char in majordeck.initiatives:
            desc += "\n" + char + ": " + majordeck.initiatives[char].name + ", is_up: " + str(majordeck.initiatives[char].is_up)

        embed = discord.Embed(
            title = "Debug: Decks Status",
            description = desc,
            color=NEUTRALCOLOR,
        )

        await context.send(embed=embed)



    #Here begins the commands for Challenge Phase play!

    @app_commands.command(
        name="deal_minor",
        description="Draw 4 cards from the Players' deck, and then hold them in your hand."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def deal_minor(self, interaction: discord.Interaction) -> None:
        minordeck, majordeck = self.get_decks(interaction.channel)

        player = interaction.user.name

        if majordeck.has_hand(player):
            #if this user already has a Major Arcana hand, they shouldn't be dealing minoor arcana to themselves!!'
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + ", you already have Major Arcana cards in your hand! Don't mix and match!",
                description = "If you're the GM, use /draw_major instead! If you're a player, please flush your Major Arcana cards.",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return None

        output = minordeck.deal_cards(4, player) #deal hand to the player. use the player's unique username (instead of their mutable & non-unique Display Name) as the key

        await interaction.response.defer(ephemeral=True)

        if output[0] == "NOHAND":
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " tried to draw, but all Player cards are in someone's hand!!!",
                description = "How did you even manage this? Please use the end-of-round command to reset the Player's deck.",
                color=ERRORCOLOR
            )

            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            if output[0] == "SHUFFLED":
                embed = discord.Embed(
                    title = "The draw pile has run out with " + str(output[1]) + " card(s) left to draw!",
                    description = "Shuffling the Player's discard pile...",
                    color=PLAYERCOLOR
                )

                await interaction.channel.send(embed=embed)

            embed2 = discord.Embed(
                title = "The adventurer " + self.get_nick(interaction.user) + " deals 4 cards into their hand!",
                description="What sort of strategems lie hidden between your fingers...?",
                color=PLAYERCOLOR
            )
            await interaction.channel.send(embed=embed2)


            await self.show_hand(interaction, minordeck, player, "The ")

    @app_commands.command(
        name="deal_major",
        description="Draw cards from the GM's deck, and then hold them in your hand."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.describe(
        cardcount="How many cards are you drawing?"
    )
    async def deal_major(self, interaction: discord.Interaction, cardcount: int) -> None:
        minordeck, majordeck = self.get_decks(interaction.channel)

        gamemaster = self.get_gm(interaction.channel)
        if gamemaster is None or interaction.user.name != gamemaster.name:
            embed = discord.Embed(
                title = "Only the Gamemaster can use this command!",
                description = "Please ask your GM about it.",
                color = ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
            return None

        player = interaction.user.name

        if minordeck.has_hand(player):
            #if this user already has a Minor Arcana hand, they shouldn't be dealing major arcana to themselves!!'
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + ", you already have Minor Arcana cards in your hand! Don't mix and match!",
                description = "If you're a player, use /draw_minor instead! If you're the GM, please flush your Minor Arcana cards.",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return None

        output = majordeck.deal_cards(cardcount, player) #deal hand to the player. use the player's unique username (instead of their mutable & non-unique Display Name) as the key

        await interaction.response.defer(ephemeral=True)

        if output[0] == "NOHAND":
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " tried to draw, but all GM cards are in someone's hand!!!",
                description = "How did you even manage this? Please use the end-of-round command to reset the GM's deck.",
                color=ERRORCOLOR
            )

            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            if output[0] == "SHUFFLED":
                embed = discord.Embed(
                    title = "The draw pile has run out with " + str(output[1]) + " card(s) left to draw!",
                    description = "Shuffling the GM's discard pile...",
                    color=GMCOLOR
                )

                await interaction.channel.send(embed=embed)

            embed2 = discord.Embed(
                title = "The gamemaster " + self.get_nick(interaction.user) + " deals " + str(cardcount) + " cards into their hand!",
                description="What sorts of doom does The Dungeon have in store now...?",
                color=GMCOLOR
            )
            await interaction.channel.send(embed=embed2)

            await self.show_hand(interaction, majordeck, player, "")

    @app_commands.command(
            name="specific_deal",
            description="get a specific card back in your hand. use ONLY to undo mistakes!"
    )
    @app_commands.describe(
        value="What is the number value of the card? Ace = 1, Page = 11, Knight = 12, Queen = 13, King = 14"
    )
    @app_commands.choices(suit=[
        app_commands.Choice(name="Wands",value="wands"),
        app_commands.Choice(name="Pentacles",value="pentacles"),
        app_commands.Choice(name="Cups",value="cups"),
        app_commands.Choice(name="Swords",value="swords"),
        app_commands.Choice(name="Major Arcana",value="major"),
    ])
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def specific_deal(self, interaction: discord.Interaction, value: int, suit: app_commands.Choice[str]):
        minordeck, majordeck = self.get_decks(interaction.channel)
        player = interaction.user.name

        #first, which deck is the card being drawn from?
        is_major = False
        if suit.value == "major" and value <= 21 and value >= 1:
            is_major = True
        elif suit.value == "major" and value == 0:
            #the Fool counts as a minor card for this game
            is_major = False
        elif suit.value != "major" and value <= 14 and value >= 1:
            is_major = False
        else:
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " searched the discard piles for a card that does not exist!",
                description = "Please check your input, friend :P",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
            return None

        #now we know for a fact the player is drawing a valid card. Check to see if they're trying to mix decks
        if is_major and minordeck.has_hand(player):
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + ", you already have Minor Arcana cards in your hand! Don't mix and match!",
                description = "If you're the GM, please flush your Minor Arcana cards.",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
            return None
        if not is_major and majordeck.has_hand(player):
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + ", you already have Major Arcana cards in your hand! Don't mix and match!",
                description = "If you're a player, please flush your Major Arcana cards.",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
            return None

        #the player is trying to draw a real card, and it does not conflict with their hand state. let's try to see if the card is in a discard pile!
        result = ""
        if is_major:
            result = majordeck.seek(player, value, suit.value)
        else:
            result = minordeck.seek(player, value, suit.value)

        #check if a card was found or not
        if result[1] == "NOCARD":
            t = self.get_nick(interaction.user) + " searched the discard pile for *"
            if suit.value == "major":
                if value == 0:
                    t += "The "
                t += MAJORNAME[value]
            else:
                t += "The " + VALUENAME[value] + suit.name
            t+= "*, but it was not there!"

            embed = discord.Embed(
                title = t,
                description = "Wherever it is, you probably shouldn't be taking that card...",
                color=ERRORCOLOR
            )

            await interaction.response.send_message(embed=embed)
            return None
        else:
            # the card was found!
            colr = 0
            if is_major:
                colr = GMCOLOR
                prefix = ""
            else:
                colr = PLAYERCOLOR
                prefix = "The "

            img = discord.File(result[0].get_filepath(), filename=result[0].filename)
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " searches the discard pile for *" + prefix + result[0].name +"*...",
                description = "... and puts it in their hand! It's okay, we all make mistakes.",
                color = colr,
            )
            embed.set_image(url="attachment://" + result[0].filename)

            await interaction.response.send_message(file=img, embed=embed)




    @app_commands.command(
        name="peek",
        description="Peek at your current hand!"
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def peek(self, interaction: discord.Interaction):
        minordeck, majordeck = self.get_decks(interaction.channel)
        player = interaction.user.name

        has_min = minordeck.has_hand(player)
        has_maj = majordeck.has_hand(player)

        await interaction.response.defer(ephemeral=True)


        if has_min and has_maj:
            embed3 = discord.Embed(
                title = "You have cards from both the Minor and Major decks in your hand!",
                description = "This should not happen! Please let the GM know.",
                color = ERRORCOLOR,
            )

            await interaction.followup.send(embed=embed3, ephemeral = False)
        elif has_min:
            await self.show_hand(interaction, minordeck, player, "The ")
        elif has_maj:
            await self.show_hand(interaction, majordeck, player, "")
        else:
            embed = discord.Embed(
                title = "Your hand is empty, friend!",
                description = "Draw some cards to peek at them.",
                color=ERRORCOLOR
            )

            await interaction.followup.send(embed=embed)



    @app_commands.command(
        name="play_minor",
        description="Play a Minor Arcana card in your hand, showing it to everyone and then discarding it."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.describe(
        value="What is the number value of the card? Ace = 1, Page = 11, Knight = 12, Queen = 13, King = 14"
    )
    @app_commands.choices(suit=[
        app_commands.Choice(name="Wands",value="wands"),
        app_commands.Choice(name="Pentacles",value="pentacles"),
        app_commands.Choice(name="Cups",value="cups"),
        app_commands.Choice(name="Swords",value="swords")
    ])
    async def play_minor(self, interaction: discord.Interaction, value: int, suit: app_commands.Choice[str]):
        minordeck, majordeck = self.get_decks(interaction.channel)

        if value < 1 or value > 14:
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " tried to play a card that does not exist!",
                description = "Please check your input, adventurer :P",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
        else:
            result = minordeck.play_card(value, suit.value, interaction.user.name) # run the play method

            #check if hand is empty or the card was not empty.
            if result[1] == "HANDEMPTY":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play a card, but their hand is empty!",
                    description = "Please be more careful, adventurer.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play a card that they do not have!",
                    description = "Please /peek at your hand to see what cards you *can* play, adventurer.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            else:
                #the player was able to play a card!

                desc = "You have played the "
                if result[0].is_reversed:
                    desc += "**Reversed** *" + result[0].name + "*!"
                else:
                    desc += "*" + result[0].name + "*!"

                img = discord.File(result[0].get_filepath(), filename=result[0].filename)
                embed = discord.Embed(
                    title="The adventurer " + self.get_nick(interaction.user) + " plays a card!",
                    description=desc,
                    color=PLAYERCOLOR,
                )
                embed.set_image(url="attachment://" + result[0].filename)

                await interaction.response.send_message(file=img, embed=embed)



    @app_commands.command(
        name="play_fool",
        description="Play The Fool + another Minor Arcana card in your hand, showing and then discarding them."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.describe(
        value="What is the number value of the card? Ace = 1, Page = 11, Knight = 12, Queen = 13, King = 14"
    )
    @app_commands.choices(suit=[
        app_commands.Choice(name="Wands",value="wands"),
        app_commands.Choice(name="Pentacles",value="pentacles"),
        app_commands.Choice(name="Cups",value="cups"),
        app_commands.Choice(name="Swords",value="swords")
    ])
    async def play_fool(self, interaction: discord.Interaction, value: int, suit: app_commands.Choice[str]):
        minordeck, majordeck = self.get_decks(interaction.channel)

        if value < 1 or value > 14:
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " tried to play a card that does not exist!",
                description = "Please check your input, adventurer :P",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
        else:
            #first, check if the player has the fool
            hasfool = minordeck.has_fool(interaction.user.name)
            if hasfool == "HANDEMPTY":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play a card, but their hand is empty!",
                    description = "Please be more careful, adventurer.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif hasfool == "NO":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play the fool, but does not have it!",
                    description = "Please /peek at your hand to see what cards you *can* play, adventurer.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            else:
                #attempt playing the other card first. if it is not there, we should not draw the fool
                result = minordeck.play_card(value, suit.value, interaction.user.name) # run the play method

                #check if card was not there
                if result[1] == "NOCARD":
                    embed = discord.Embed(
                        title = self.get_nick(interaction.user) + " tried to play a card that they do not have!",
                        description = "Please /peek at your hand to see what cards you *can* play, adventurer.",
                        color=ERRORCOLOR
                    )

                    await interaction.response.send_message(embed=embed)
                else:
                    #the player was able to play the other card, AND they have the fool! play the fool now
                    fool = minordeck.play_card(0, "major", interaction.user.name)

                    #show output s normal
                    desc = "You have played ***The Fool***, plus the "
                    if result[0].is_reversed:
                        desc += "**Reversed** *" + result[0].name + "*!"
                    else:
                        desc += "*" + result[0].name + "*!"


                    #sets up the embed image
                    merge_images([fool[0].get_filepath(), result[0].get_filepath()])
                    img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)

                    #img = discord.File(result[0].get_filepath(), filename=result[0].filename)
                    embed = discord.Embed(
                        title="The adventurer " + self.get_nick(interaction.user) + " plays The Fool!",
                        description=desc,
                        color=PLAYERCOLOR,
                    )
                    embed.set_image(url="attachment://" + MERGEDIMG)

                    await interaction.response.send_message(file=img, embed=embed)


    @app_commands.command(
        name="play_major",
        description="Play a Major Arcana card in your hand, showing it to everyone and then discarding it."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.describe(
        value="What is the number value of the card?"
    )
    async def play_major(self, interaction: discord.Interaction, value: int):
        minordeck, majordeck = self.get_decks(interaction.channel)

        if value < 1 or value > 21:
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " tried to play a card that does not exist!",
                description = "Please check your input, gamemaster!",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
        else :
            result = majordeck.play_card(value, "major", interaction.user.name) # run the play method

            #check if hand is empty or the card was not empty.
            if result[1] == "HANDEMPTY":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play a card, but their hand is empty!",
                    description = "Please be more careful, gamemaster.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play a card that they do not have!",
                    description = "Please /peek at your hand to see what cards you *can* play, gamemaster.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            else:
                #the player was able to play a card!

                desc = "You have played the "
                if result[0].is_reversed:
                    desc += "**Reversed** *" + result[0].name + "*!"
                else:
                    desc += "*" + result[0].name + "*!"

                img = discord.File(result[0].get_filepath(), filename=result[0].filename)
                embed = discord.Embed(
                    title="The gamemaster " + self.get_nick(interaction.user) + " plays a card!",
                    description=desc,
                    color=PLAYERCOLOR,
                )
                embed.set_image(url="attachment://" + result[0].filename)

                await interaction.response.send_message(file=img, embed=embed)

    @commands.hybrid_command(
        name = "flush",
        description = "Flush all the cards in your hand into the discard pile. Useful for fixing erroneous hands."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def flush(self, context: Context):
        minordeck, majordeck = self.get_decks(context.channel)
        player = context.author.name

        discards1 = minordeck.flush(player)
        discards2 = majordeck.flush(player)
        discardlist = discards1 + discards2

        imagelist=[]
        for card in discardlist:
            imagelist.append(card.get_filepath())

        #sets up the embed image
        merge_images(imagelist)
        img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)

        embed = discord.Embed(
                title = self.get_nick(context.author) + " flushes their hand into the discard pile!",
                color=NEUTRALCOLOR,
            )
        embed.set_image(url="attachment://" + MERGEDIMG)

        await context.send(embed=embed, file=img)


    #here begin the facedown card commands

    @app_commands.command(
        name="facedown_minor",
        description="Play a card facedown for your adventurer, to spring later!",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.describe(
        value="What is the number value of the card? Ace = 1, Page = 11, Knight = 12, Queen = 13, King = 14",
        action_type="Are you playing this as a Main action during your turn, or a Minor action outside of your turn?",
    )
    @app_commands.choices(
        suit=[
            app_commands.Choice(name="Wands",value="wands"),
            app_commands.Choice(name="Pentacles",value="pentacles"),
            app_commands.Choice(name="Cups",value="cups"),
            app_commands.Choice(name="Swords",value="swords")
        ],
        action_type=[
            app_commands.Choice(name="Main",value=1),
            app_commands.Choice(name="Minor",value=0)
        ]
    )
    async def facedown_minor(self, interaction: discord.Interaction, value: int, suit: app_commands.Choice[str], action_type: app_commands.Choice[int]):
        minordeck, majordeck = self.get_decks(interaction.channel)
        player = interaction.user.name

        if value < 1 or value > 14:
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " tried to play a card that does not exist!",
                description = "If you tried, remember that you can't play The Fool facedown.",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
        else:
            result = minordeck.play_facedown(player, player, value, suit.value, action_type.value)

            #check if hand is empty or the card was not empty.
            if result[1] == "HANDEMPTY":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play a card, but their hand is empty!",
                    description = "Please be more careful, adventurer.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play a card that they do not have!",
                    description = "Please /peek at your hand to see what cards you *can* play, adventurer.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "HASFACEDOWN":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to place a card facedown, but they already have another facedown card!",
                    description = "Please /discard_facedown your previous card if you want to make a new facedown action, adventurer.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            else:
                #the player was able to place the facedown card!

                imagename = ""
                if action_type.value: # if it is a main action, use the upright cardbacks
                    imagename = "cardbacks.png"
                else:
                    #if it is a minor action, use sideways cardbacks
                    imagename = "sidewaysbacks.png"

                img = discord.File(IMGDIR + imagename,  filename=imagename)
                embed = discord.Embed(
                    title="The adventurer " + self.get_nick(interaction.user) + " places a card facedown as a *" + action_type.name + "* Action!",
                    description="Who knows how powerful it is...?",
                    color=PLAYERCOLOR,
                )
                embed.set_image(url="attachment://" + imagename)

                await interaction.response.send_message(file=img, embed=embed)



    @app_commands.command(
        name="facedown_major",
        description="Play a GM card facedown for a monster, to spring later!",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.describe(
        value="What is the number value of the card? Ace = 1, Page = 11, Knight = 12, Queen = 13, King = 14",
        action_type="Are you playing this as a Main action during your turn, or a Minor action outside of your turn?",
        monster="The name of the monster playing this card. Please give each monster a unique name!"
    )
    @app_commands.choices(
        action_type=[
            app_commands.Choice(name="Main",value=1),
            app_commands.Choice(name="Minor",value=0)
        ]
    )
    async def facedown_major(self, interaction: discord.Interaction, monster: str, value: int, action_type: app_commands.Choice[int]):
        minordeck, majordeck = self.get_decks(interaction.channel)
        player = interaction.user.name

        if value < 1 or value > 21:
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " tried to play a card that does not exist!",
                description = "Please be more careul, gamemaster!",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
        else:
            result = majordeck.play_facedown(player, monster, value, "major", action_type.value)

            #check if hand is empty or the card was not empty.
            if result[1] == "HANDEMPTY":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play a card, but their hand is empty!",
                    description = "Please be more careful, gamemaster.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to play a card that they do not have!",
                    description = "Please /peek at your hand to see what cards you *can* play, gamemaster.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "HASFACEDOWN":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to place a card facedown for " + monster + ", but it already has another facedown card!",
                    description = "Please /discard_facedown your monster's previous card if you want it to make a new facedown action, gamemaster.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            else:
                #the player was able to place the facedown card!

                imagename = ""
                if action_type.value: # if it is a main action, use the upright cardbacks
                    imagename = "cardbacks.png"
                else:
                    #if it is a minor action, use sideways cardbacks
                    imagename = "sidewaysbacks.png"

                img = discord.File(IMGDIR + imagename,  filename=imagename)
                embed = discord.Embed(
                    title="The gamemaster " + self.get_nick(interaction.user) + " places a card facedown for " + monster + " as a *" + action_type.name + "* Action!",
                    description="Who knows how powerful it is...?",
                    color=GMCOLOR,
                )
                embed.set_image(url="attachment://" + imagename)

                await interaction.response.send_message(file=img, embed=embed)

    @app_commands.command(
        name = "discard_facedown",
        description = "Discards current facedown card, if you cannot or don't want to activate it."
    )
    @app_commands.describe(
        monster = "If you are the GM, name which monster's facedown card you want to discard!"
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def discard_facedown(self, interaction: discord.Interaction, monster: str=None):
        minordeck, majordeck = self.get_decks(interaction.channel)
        if monster is None:
            #the user running this command is a player
            result = minordeck.discard_facedown(interaction.user.name)

            if result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to discard their facedown card, but they do not have one!",
                    color=ERRORCOLOR
                )
                await interaction.response.send_message(embed=embed)
            else:
                #the discard was successful! show the card to everyone

                desc = "It was a "
                if result[0].is_reversed:
                    desc += "**Reversed** *" + result[0].name + "*!"
                else:
                    desc += "*" + result[0].name + "*!"

                img = discord.File(result[0].get_filepath(), filename=result[0].filename)
                embed = discord.Embed(
                    title="The adventurer " + self.get_nick(interaction.user) + " quietly discards their facedown card...",
                    description=desc,
                    color=PLAYERCOLOR,
                )
                embed.set_image(url="attachment://" + result[0].filename)

                await interaction.response.send_message(file=img, embed=embed)
        else:
            #the usr running this command is the GM

            #verify it really is GM
            gamemaster = self.get_gm(interaction.channel)
            if gamemaster is None or interaction.user.name != gamemaster.name:
                embed = discord.Embed(
                    title = "Only the Gamemaster can use this command for monsters!",
                    description = "Please ask your GM about it.",
                    color = ERRORCOLOR
                )
                await interaction.response.send_message(embed=embed)
                return None

            result = majordeck.discard_facedown(monster)

            if result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to discard the facedown card of " + monster + ", but it does not have one!",
                    color=ERRORCOLOR
                )
                await interaction.response.send_message(embed=embed)
            else:
                #the discard was successful! show the card to everyone

                desc = "It was a "
                if result[0].is_reversed:
                    desc += "**Reversed** *" + result[0].name + "*!"
                else:
                    desc += "*" + result[0].name + "*!"

                img = discord.File(result[0].get_filepath(), filename=result[0].filename)
                embed = discord.Embed(
                    title="The gamemaster " + self.get_nick(interaction.user) + " quietly discards the facedown card of " + monster + "...",
                    description=desc,
                    color=GMCOLOR,
                )
                embed.set_image(url="attachment://" + result[0].filename)

                await interaction.response.send_message(file=img, embed=embed)


    #reveal_facedown is kind of the same as discard_facdown, just with different flavor text...
    @app_commands.command(
        name = "reveal_facedown",
        description = "Reveals and discards your facedown card, once it has been triggered!"
    )
    @app_commands.describe(
        monster = "If you are the GM, name which monster's facedown card you want to reveal!"
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def reveal_facedown(self, interaction: discord.Interaction, monster: str=None):
        minordeck, majordeck = self.get_decks(interaction.channel)
        if monster is None:
            #the user running this command is a player
            result = minordeck.discard_facedown(interaction.user.name)

            if result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to reveal their facedown card, but they do not have one!",
                    color=ERRORCOLOR
                )
                await interaction.response.send_message(embed=embed)
            else:
                #the discard was successful! show the card to everyone

                desc = "It was a "
                if result[0].is_reversed:
                    desc += "**Reversed** *" + result[0].name + "*!"
                else:
                    desc += "*" + result[0].name + "*!"

                img = discord.File(result[0].get_filepath(), filename=result[0].filename)
                embed = discord.Embed(
                    title="The adventurer " + self.get_nick(interaction.user) + " reveals their facedown card and springs into action!",
                    description=desc,
                    color=PLAYERCOLOR,
                )
                embed.set_image(url="attachment://" + result[0].filename)

                await interaction.response.send_message(file=img, embed=embed)
        else:
            #the usr running this command is the GM
            result = majordeck.discard_facedown(monster)

            #verify it's really the GM'
            gamemaster = self.get_gm(interaction.channel)
            if gamemaster is None or interaction.user.name != gamemaster.name:
                embed = discord.Embed(
                    title = "Only the Gamemaster can use this command for monsters!",
                    description = "Please ask your GM about it.",
                    color = ERRORCOLOR
                )
                await interaction.response.send_message(embed=embed)
                return None

            if result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to reveal the facedown card of " + monster + ", but it does not have one!",
                    color=ERRORCOLOR
                )
                await interaction.response.send_message(embed=embed)
            else:
                #the discard was successful! show the card to everyone

                desc = "It was a "
                if result[0].is_reversed:
                    desc += "**Reversed** *" + result[0].name + "*!"
                else:
                    desc += "*" + result[0].name + "*!"

                img = discord.File(result[0].get_filepath(), filename=result[0].filename)
                embed = discord.Embed(
                    title="The gamemaster " + self.get_nick(interaction.user) + " reveals the facedown card of " + monster + "!",
                    description=desc,
                    color=GMCOLOR,
                )
                embed.set_image(url="attachment://" + result[0].filename)

                await interaction.response.send_message(file=img, embed=embed)


    #Initiative-related commands begin here!

    @app_commands.command(
        name="initiative",
        description="Place a card facedown to serve as your initiative for this round!",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.describe(
        value="What is the number value of the card? Ace = 1, Page = 11, Knight = 12, Queen = 13, King = 14",
    )
    @app_commands.choices(
        suit=[
            app_commands.Choice(name="Wands",value="wands"),
            app_commands.Choice(name="Pentacles",value="pentacles"),
            app_commands.Choice(name="Cups",value="cups"),
            app_commands.Choice(name="Swords",value="swords")
        ]
    )
    async def initiative(self, interaction: discord.Interaction, value: int, suit: app_commands.Choice[str]):
        minordeck, majordeck = self.get_decks(interaction.channel)
        player = interaction.user.name

        if value < 1 or value > 14:
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " tried to set a card that does not exist for their initiative!",
                description = "If you tried, remember that you can't use The Fool as your initiative. Why would you even want to?",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
        else:
            result = minordeck.set_initiative(player, player, value, suit.value)

            #check if hand is empty or the card was not empty.
            if result[1] == "HANDEMPTY":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to set down their initiative, but their hand is empty!",
                    description = "Please be more careful, adventurer.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to set initiative with a card that they do not have!",
                    description = "Please /peek at your hand to see what cards you *can* use, adventurer.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "HASFACEDOWN":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to set their initiative, but they have already done so this round!",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            else:
                #the player was able to set their initiative
                self.userids[interaction.user.name] = interaction.user.id
                self.usernicks[interaction.user.name] = self.get_nick(interaction.user)


                imagename = "cardbacks.png"

                img = discord.File(IMGDIR + imagename,  filename=imagename)
                embed = discord.Embed(
                    title="The adventurer " + self.get_nick(interaction.user) + " sets down a card as their initiative!",
                    description="Fast or slow? Reckless or cautious?",
                    color=PLAYERCOLOR,
                )
                embed.set_image(url="attachment://" + imagename)

                await interaction.response.send_message(file=img, embed=embed)




    @app_commands.command(
        name="monster_initiative",
        description="Set the initiative for a specific monster!",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.describe(
        value="What is the number value of the card? Ace = 1, Page = 11, Knight = 12, Queen = 13, King = 14",
        monster="The name of the monster playing this card. Please give each monster a unique name!"
    )
    async def monster_initiative(self, interaction: discord.Interaction, monster: str, value: int):
        minordeck, majordeck = self.get_decks(interaction.channel)
        player = interaction.user.name

        if value < 1 or value > 21:
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " tried to set initiative with a card that does not exist!",
                description = "Please be more careul, gamemaster!",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
        else:
            result = majordeck.set_initiative(player, monster, value, "major")

            #check if hand is empty or the card was not empty.
            if result[1] == "HANDEMPTY":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to set initiative, but their hand is empty!",
                    description = "Please be more careful, gamemaster.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to set initiative with a card that they do not have!",
                    description = "Please /peek at your hand to see what cards you *can* set down, gamemaster.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            elif result[1] == "HASFACEDOWN":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to set the initiative of " + monster + ", but it already has an initiative card!",
                    description = "Please wait until end of round.",
                    color=ERRORCOLOR
                )

                await interaction.response.send_message(embed=embed)
            else:
                #the player was able to place the facedown card!

                imagename = "cardbacks.png"

                img = discord.File(IMGDIR + imagename,  filename=imagename)
                embed = discord.Embed(
                    title="The gamemaster " + self.get_nick(interaction.user) + " sets down an initiative card for " + monster + "!",
                    description="Fast or slow? Reckless or cautious?",
                    color=GMCOLOR,
                )
                embed.set_image(url="attachment://" + imagename)

                await interaction.response.send_message(file=img, embed=embed)

    #does not discard the card, just makes it visible to everyone
    @app_commands.command(
        name = "flip_initiative",
        description = "Manually flip over your facedown initiative card, in case you are being targeted by an enemy!"
    )
    @app_commands.describe(
        monster = "If you are the GM, name which monster's initiative card you want to reveal!"
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def reveal_facedown(self, interaction: discord.Interaction, monster: str=None):
        minordeck, majordeck = self.get_decks(interaction.channel)
        if monster is None:
            #the user running this command is a player
            result = minordeck.flip_initiative(interaction.user.name)

            if result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to reveal their initiative card, but they do not have one!",
                    color=ERRORCOLOR
                )
                await interaction.response.send_message(embed=embed)
            else:
                #the discard was successful! show the card to everyone

                desc = "It is The "
                if result[0].is_reversed:
                    desc += "**Reversed** *" + result[0].name + "*!"
                else:
                    desc += "*" + result[0].name + "*!"

                img = discord.File(result[0].get_filepath(), filename=result[0].filename)
                embed = discord.Embed(
                    title="The adventurer " + self.get_nick(interaction.user) + " reveals their initiative card in response to enemy assault!",
                    description=desc,
                    color=PLAYERCOLOR,
                )
                embed.set_image(url="attachment://" + result[0].filename)

                await interaction.response.send_message(file=img, embed=embed)
        else:
            #the usr running this command is the GM
            result = majordeck.flip_initiative(monster)

            #check if it's really the GM'
            gamemaster = self.get_gm(interaction.channel)
            if gamemaster is None or interaction.user.name != gamemaster.name:
                embed = discord.Embed(
                    title = "Only the Gamemaster can use this command for monsters!",
                    description = "Please ask your GM about it.",
                    color = ERRORCOLOR
                )
                await interaction.response.send_message(embed=embed)
                return None

            if result[1] == "NOCARD":
                embed = discord.Embed(
                    title = self.get_nick(interaction.user) + " tried to reveal the initiative card of " + monster + ", but it does not have one!",
                    color=ERRORCOLOR
                )
                await interaction.response.send_message(embed=embed)
            else:
                #the discard was successful! show the card to everyone

                desc = "It is the "
                if result[0].is_reversed:
                    desc += "**Reversed** *" + result[0].name + "*!"
                else:
                    desc += "*" + result[0].name + "*!"

                img = discord.File(result[0].get_filepath(), filename=result[0].filename)
                embed = discord.Embed(
                    title="The gamemaster " + self.get_nick(interaction.user) + " reveals the initiative card of " + monster + "!",
                    description=desc,
                    color=GMCOLOR,
                )
                embed.set_image(url="attachment://" + result[0].filename)

                await interaction.response.send_message(file=img, embed=embed)

    @commands.hybrid_command(
        name = "declare_gm",
        description = "Declare yourself as the GM for this channel!"
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def declare_gm(self, context: Context):
        self.gamemasters[context.channel.id] = context.author
        await context.send(content="You have been declared as the Gamemaster for this channel!")



    @commands.hybrid_command(
        name =  "next_turn",
        description = "Counts up to the next character whose turn it is!"
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def next_turn(self, context: Context):
        minordeck, majordeck = self.get_decks(context.channel)
        gamemaster = self.get_gm(context.channel)

        initid = context.channel.id

        if initid not in self.initiative:
            self.initiative[initid] = 1

        # we need to build a dict of every char's initiative score, irregardless of card.
        init_pool = {}
        for char in minordeck.initiatives:
            init_pool[char] = minordeck.initiatives[char].value

        for monster in majordeck.initiatives:
            init_pool[":" + monster] = majordeck.initiatives[monster].value #monsters identifiably have a : in their name, to avoid name conflicts in the keys of init_pool

        #check if init pool is empty
        if not init_pool:
            embed = discord.Embed(
                title = "No one has any initiative cards down!",
                description = "Please place down some initiative cards before playing.",
                color = ERRORCOLOR
            )
            await context.send(embed=embed)
            return None

        max_initiative = max(init_pool.values())

        embed = discord.Embed(
            title = "The Dungeon counts up towards a bloody battle!",
            description = "Current Initiative: " + str(self.initiative[initid]) + "\nLower initiatives go sooner, but are more vulnerable!",
            color = BATTLECOLOR
        )
        await context.send(embed = embed)


        #main countdown loop!!!
        turn_goers = []
        while self.initiative[initid] <= max_initiative:
            if self.initiative[initid] in init_pool.values():
                #it's someone's turn on this number! possibly many people!
                for char in init_pool:
                    if init_pool[char] == self.initiative[initid]:
                        #this adventurer/monster's initiative matches! add them to turn_goers
                        turn_goers.append(char)
                await context.channel.send("***" + str(self.initiative[initid]) + "!***")
                self.initiative[initid] += 1
                break

            else:
                #it is not anyone's turn this number
                await context.channel.send(str(self.initiative[initid]) + "...")
                time.sleep(1)
                self.initiative[initid] += 1

        #check if this was the final turn
        is_final = False
        if self.initiative[initid] >= max_initiative:
            is_final = True

        #now, we check if we are announcing a turn!
        if len(turn_goers) != 0:
            #we have turns to announce!!
            if len(turn_goers) == 1:
                char = turn_goers[0]
                #only one person is going! be detailed!
                #first we get a ping for an adventurer, and the normal monster name for a monster
                name=""
                ping=""
                card = 0
                if char[0] == ":":
                    card = majordeck.initiatives[(char[1:])]
                    name = char[1:]

                    if gamemaster is not None:
                        ping = "<@" + str(gamemaster.id) + ">'s " + char[1:]
                else:
                    card = minordeck.initiatives[char]
                    name = char
                    if name in self.userids:
                        ping = "<@" + str(self.userids[name]) + ">" #this should ping the user
                    if name in self.usernicks:
                        name = self.usernicks[name]

                #set the flipped initiative card!
                desc = "Their Initiative Card is "

                if not card.is_up:
                    desc += "revealed to be "
                    card.is_up = True

                if card.suit != "major":
                    desc += "the "

                if card.is_reversed:
                    desc += "**Reversed** *" + card.name + "*!"
                else:
                    desc += "*" + card.name + "*!"

                if is_final:
                    desc += "\n\n This is the final turn of the round! Run /end_of_round afterwards!"

                img = discord.File(card.get_filepath(), filename=card.filename)
                embed = discord.Embed(
                    title = "The spotlight shines on " + name + "!",
                    description = desc,
                    color = BATTLECOLOR
                )
                embed.set_image(url="attachment://" + card.filename)

                await context.send(embed=embed, file=img)

                if ping != "":
                    await context.channel.send(content = "Go, " + ping + ", Dance!")

            else:
                #first, make sure we flip everyone's initiative cards face-up, and get their names and cards!
                cardlist = [] #just filepaths for images
                namelist = []
                has_monster = False # see if we need to ping GM!
                pinglist = "" #first we just add players to the pinglist
                for char in turn_goers:
                    if char[0] == ":":  #if it is a monster, we need to ignore the colon
                        majordeck.initiatives[(char[1:])].is_up = True
                        namelist.append(char[1:])
                        cardlist.append(majordeck.initiatives[(char[1:])].get_filepath())
                        has_monster = True
                    else:
                        minordeck.initiatives[char].is_up = True

                        name = char
                        if name in self.userids:
                            pinglist += "<@" + str(self.userids[name]) + ">" #this should ping the user
                        if name in self.usernicks:
                            name = self.usernicks[name]
                        namelist.append(name)
                        cardlist.append(minordeck.initiatives[char].get_filepath())

                ttl = ""
                if has_monster:
                    ttl = "Many combatants are raring to go! The gamemaster decides who goes first!"
                    #also add GM to pinglist
                    if gamemaster is not None:
                        pinglist += "<@" + str(gamemaster.id) + ">"

                else:
                    ttl = "Many adventurers act together! Decide among yourselves who goes first!"

                desc = "The following characters are ready to risk it all:"
                for name in namelist:
                    desc += "\n" + name + "!"

                if is_final:
                    desc += "\n\n This is the final turn of the round! Run /end_of_round after everyone has gone!"

                #sets up the embed image
                merge_images(cardlist)
                img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)

                embed = discord.Embed(
                        title = ttl,
                        description = desc,
                        color=BATTLECOLOR,
                    )
                embed.set_image(url="attachment://" + MERGEDIMG)

                await context.send(embed=embed, file=img)
        else:
            #There are no turn-goers. let ppl know
            embed = discord.Embed(
                title = "There is no one left to go!",
                description = "Run /end_of_round if you haven't yet.",
                color = NEUTRALCOLOR
            )
            await context.send(embed=embed)

            await context.channel.send(content = pinglist)

    @commands.hybrid_command(
        name = "end_of_round",
        description = "Resets initiative, initiative cards, and flushes everyone's hand.'"
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def end_of_round(self, context:Context):
        minordeck, majordeck = self.get_decks(context.channel)

        #check that the GM is doing this
        gamemaster = self.get_gm(context.channel)
        if gamemaster is None or context.author.name != gamemaster.name:
            embed = discord.Embed(
                title = "Only the Gamemaster can use this command!",
                description = "Please ask your GM about it.",
                color = ERRORCOLOR
            )
            await context.send(embed=embed)
            return None


        initid = context.channel.id

        if initid not in self.initiative:
            await context.send(content="The round hasn't started yet! What are yout trying to reset it for?")
        else:
            #reset the initiative
            self.initiative.pop(initid)

            cardlist = []

            #do initiative cards
            adventurers = []
            for adventurer in minordeck.initiatives:
                adventurers.append(adventurer)

            for a in adventurers:
                initcard = minordeck.discard_initiative(adventurer)
                if initcard[1] == "NOCARD":
                    await context.send(content="Error! Tried to discard an initiative card that doesn't exist! This should not happen!'")
                    return None
                cardlist.append(initcard[0].get_filepath())
                #cleaning up our dictionaries
                self.userids.pop(adventurer)
                self.usernicks.pop(adventurer)

            for monster in majordeck.initiatives:
                initcard = majordeck.discard_initiative(monster)
                if initcard[1] == "NOCARD":
                    await context.send(content="Error! Tried to discard an initiative card that doesn't exist! This should not happen!'")
                    return None
                cardlist.append(initcard[0].get_filepath())
                #same thing, but without dictionaries to clean

            #do everyone's hands'
            discardlist = []
            minorhands = []
            for hand in minordeck.hands:
                minorhands.append(hand)

            for hand in minorhands:
                discardlist += minordeck.flush(hand)

            majorhands = []
            for hand in majordeck.hands:
                majorhands.append(hand)

            for hand in majorhands:
                discardlist += majordeck.flush(hand)


            for card in discardlist:
                cardlist.append(card.get_filepath())


            #sets up the embed image
            merge_images(cardlist)
            img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)

            embed = discord.Embed(
                    title = self.get_nick(context.author) + " ends the round!",
                    description = "Initiative has been reset to 1. Hands and initiative cards have been discarded, though facedown cards remain!\n If *The Fool* was played this round, shuffle both decks now!",
                    color=NEUTRALCOLOR,
                )
            embed.set_image(url="attachment://" + MERGEDIMG)

            await context.send(embed=embed, file=img)

    @commands.hybrid_command(
        name = "check_table",
        description = "Take a peek at everything on the table in your DMs"
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def check_table(self, context : Context):
        minordeck, majordeck = self.get_decks(context.channel)

        gamemaster = self.get_gm(context.channel)
        gm_hand = None
        if gamemaster is not None and gamemaster.name in majordeck.hands:
            gm_hand = majordeck.hands[gamemaster.name]

        #first, show all the players stuff
        playertable = {} # a dict  with usern.name as a dict,
        """
        [0] = the hand
        [1] = the initiative
        [2] = the facedown
        """

        # gather all the info, hands first!
        for player in minordeck.hands:
            playertable[player] = [minordeck.hands[player]]

        # next, all the initiativve cards. may need to add a new entry for handsless players
        for player in minordeck.initiatives:
            if player not in playertable:
                playertable[player] = [[], minordeck.initiatives[player]]
            else:
                playertable[player].append(minordeck.initiatives[player])

        #same for facedowns
        for player in minordeck.facedowns:
            if player not in playertable:
                playertable[player] = [[], None, minordeck.facedowns[player]]
            else:
                playertable[player].append(minordeck.facedowns[player])

        for player in playertable:
            if len(playertable[player]) == 1:
                playertable[player].append(None)
                playertable[player].append(None)
            elif len(playertable[player]) == 2:
                playertable[player].append(None)

        #now we have a full deck of player stuff! collect info on GM next

        monstertable = {}
        """
        [0] = the initiative
        [1] = the facedown
        """

        for monster in majordeck.initiatives:
            monstertable[monster] = [majordeck.initiatives[monster]]

        for monster in majordeck.facedowns:
            if monster not  in monstertable:
                monstertable[monster] = [None, majordeck.facedowns[monster]]
            else:
                monstertable[monster].append(majordeck.facedowns[monster])

        for monster in monstertable:
            if len(monstertable[monster]) == 1:
                monstertable[monster].append(None)

        #now that we have everything, we can start embedding!

        embed2 = discord.Embed(
            title = self.get_nick(context.author) + " checks the state of the table...",
            color = NEUTRALCOLOR
        )

        await context.send(embed=embed2)


        #make a DM channel first
        channel = await context.author.create_dm()

        await channel.send(content = "**On the Players' Side...**")

        for p in playertable:
            if context.author.name == p:
                #if displaying your own cards...
                handcount = len(playertable[p][0])
                initcard = playertable[p][1]
                facedown = playertable[p][2]

                initimgname = "cardbacks.png"
                initimgpath = IMGDIR + "cardbacks.png"
                initblurb = ""

                if initcard is not None: #show the init card either way
                    initimgname = initcard.filename
                    initimgpath = initcard.get_filepath()
                    initblurb =  "of **" + str(initcard.value) + "**"


                blurb = "1 card"
                if handcount != 1:
                    blurb = str(handcount) + " cards"
                ttl =  "**Your** are holding " + blurb + " in your hand!"

                if initcard is None and facedown is None:
                    #just give hand info

                    embed = discord.Embed(
                        title = ttl,
                        description = "You have no cards down on the table.",
                        color = PLAYERCOLOR
                    )

                    await channel.send(embed=embed)

                elif initcard is None:
                    #there is a facedown card

                    img = discord.File(facedown.get_filepath(), filename= facedown.filename)
                    act = ""
                    if facedown.is_main:
                        act = "main-action"
                    else:
                        act = "minor-action"

                    embed = discord.Embed(
                        title = ttl,
                        description = "You have the *" + facedown.name + "* as a " + act + " facedown card!",
                        color = PLAYERCOLOR
                    )
                    embed.set_image(url="attachment://" + imgname)

                    await channel.send(embed=embed, file=img)

                elif facedown is None:
                    #there is only a initiative card

                    img = discord.File(initimgpath, filename= initimgname)

                    embed = discord.Embed(
                        title = ttl,
                        description = "You have an Initiative " + initblurb + "!",
                        color = PLAYERCOLOR
                    )
                    embed.set_image(url="attachment://" + initimgname)

                    await channel.send(embed=embed, file=img)

                else:
                    #There is both an initiative and a facedown!
                    act = ""
                    imglist = [initimgpath, facedown.get_filepath()]
                    merge_images(imglist)
                    if facedown.is_main:
                        act = "main-action"
                    else:
                        act = "minor-action"

                    img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)
                    embed = discord.Embed(
                        title = ttl,
                        description = "They have an Initiative " + initblurb + " and the *" + facedown.name + "* as a " + act + " facedown card!",
                        color = PLAYERCOLOR
                    )
                    embed.set_image(url="attachment://" +MERGEDIMG)

                    await channel.send(embed=embed, file=img)


            else:
                handcount = len(playertable[p][0])
                initcard = playertable[p][1]
                facedown = playertable[p][2]

                initimgname = "cardbacks.png"
                initimgpath = IMGDIR + "cardbacks.png"
                initblurb = "card face-down"

                if initcard is not None:
                    if initcard.is_up:
                        initimgname = initcard.filename
                        initimgpath = initcard.get_filepath()
                        initblurb = "of **" + str(initcard.value) + "**"


                blurb = "1 card"
                if handcount != 1:
                    blurb = str(handcount) + " cards"
                ttl =  self.usernicks[p] + " is holding " + blurb + " in their hand!"


                if initcard is None and facedown is None:
                    #just give hand info

                    embed = discord.Embed(
                        title = ttl,
                        description = "They have no cards down on the table.",
                        color = PLAYERCOLOR
                    )

                    await channel.send(embed=embed)

                elif initcard is None:
                    #there is a facedown card

                    img = ""
                    act = ""
                    imgname = ""
                    if facedown.is_main:
                        img = discord.File(IMGDIR + "cardbacks.png", filename="cardbacks.png")
                        act = "main-action"
                        imgname = "cardbacks.png"
                    else:
                        img = discord.File(IMGDIR + "sidwaysbacks.png", filename="sidewaysbacks.png")
                        act = "minor-action"
                        imgname = 'sidewaysbacks.png'

                    embed = discord.Embed(
                        title = ttl,
                        description = "They have a " + act + " card facedown!",
                        color = PLAYERCOLOR
                    )
                    embed.set_image(url="attachment://" + imgname)

                    await channel.send(embed=embed, file=img)

                elif facedown is None:
                    #there is only a initiative card

                    img = discord.File(initimgpath, filename= initimgname)

                    embed = discord.Embed(
                        title = ttl,
                        description = "They have an Initiative " + initblurb + "!",
                        color = PLAYERCOLOR
                    )
                    embed.set_image(url="attachment://" + initimgname)

                    await channel.send(embed=embed, file=img)

                else:
                    #There is both an initiative and a facedown!
                    act = ""
                    if facedown.is_main:
                        imglist = [initimgpath, IMGDIR + "cardbacks.png"]
                        merge_images(imglist)
                        act = "main-action"
                    else:
                        merge_sideways(initimgpath)
                        act = "minor-action"

                    img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)
                    embed = discord.Embed(
                        title = ttl,
                        description = "They have an Initiative " + initblurb + " and a " + act + " facedown card!",
                        color = PLAYERCOLOR
                    )
                    embed.set_image(url="attachment://" +MERGEDIMG)

                    await channel.send(embed=embed, file=img)

        #check if the person sending this is gm
        sender_is_gm = False
        if gamemaster is not None and context.author.name == gamemaster.name:
            sender_is_gm = True

        await channel.send(content="**On the GM's side...**")

        if gamemaster is not None:
            if gm_hand is not None:
                if len(gm_hand) == 1:
                    await channel.send(content= "**The Gamemaster " + self.get_nick(gamemaster) + " is holding 1 card!**")
                else:
                    await channel.send(content= "**The Gamemaster " + self.get_nick(gamemaster) + " is holding " + str(len(gm_hand)) + " cards!**")
            else:
                await channel.send(content= "**The Gamemaster " + self.get_nick(gamemaster) + " is holding 0 cards!**")

        for m in monstertable:
            #we need to do the same for a monster, but monsters do not have hands
            initcard = monstertable[m][0]
            facedown = monstertable[m][1]

            initimgname = "cardbacks.png"
            initimgpath = IMGDIR + "cardbacks.png"
            initblurb = "card face-down"

            if initcard is not None:
                if initcard.is_up or sender_is_gm:
                    initimgname = initcard.filename
                    initimgpath = initcard.get_filepath()
                    initblurb = "of **" + str(initcard.value) + "**"

            ttl =  m + " sits menacingly at the table!"


            if initcard is None and facedown is None:
                #just give hand info

                embed = discord.Embed(
                    title = ttl,
                    description = "They have no cards down on the table.",
                    color = GMCOLOR
                )

                await channel.send(embed=embed)

            elif initcard is None:
                #there is a facedown card

                img = ""
                desc = ""
                imgname = ""

                if sender_is_gm:
                    img = discord.File(facedown.get_filepath(), filename= facedown.filename)
                    imgname = facedown.filename
                    act = ""
                    if facedown.is_main:
                        act = "main-action"
                    else:
                        act = "minor-action"
                    desc = "They have the *" + facedown.name + "* as a " + act + " facedown card!"
                elif facedown.is_main:
                    img = discord.File(IMGDIR + "cardbacks.png", filename="cardbacks.png")
                    desc = "They have a main-action card facedown!"
                    imgname = "cardbacks.png"
                else:
                    img = discord.File(IMGDIR + "sidwaysbacks.png", filename="sidewaysbacks.png")
                    desc = "They have a minor-action card facedown!"
                    imgname = 'sidewaysbacks.png'

                embed = discord.Embed(
                    title = ttl,
                    description = desc,
                    color = PLAYERCOLOR
                )
                embed.set_image(url="attachment://" + imgname)

                await channel.send(embed=embed, file=img)

            elif facedown is None:
                #there is only a initiative card

                img = discord.File(initimgpath, filename= initimgname)

                embed = discord.Embed(
                    title = ttl,
                    description = "They have an Initiative " + initblurb + "!",
                    color = PLAYERCOLOR
                )
                embed.set_image(url="attachment://" + initimgname)

                await channel.send(embed=embed, file=img)

            else:
                #There is both an initiative and a facedown!
                desc = ""
                if sender_is_gm:
                    imglist = [initimgpath, facedown.get_filepath()]
                    merge_images(imglist)
                    act = ""
                    if facedown.is_main:
                        act = "main-action"
                    else:
                        act = "minor-action"
                    desc = "They have an Initiative " + initblurb + " and the *" + facedown.name + "* as a " + act + " facedown card!"
                elif facedown.is_main:
                    imglist = [initimgpath, IMGDIR + "cardbacks.png"]
                    merge_images(imglist)
                    desc = "They have an Initiative " + initblurb + " and a main-action facedown card!"
                else:
                    merge_sideways(initimgpath)
                    desc = "They have an Initiative " + initblurb + " and a minor-action facedown card!"

                img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)
                embed = discord.Embed(
                    title = ttl,
                    description = desc,
                    color = PLAYERCOLOR
                )
                embed.set_image(url="attachment://" +MERGEDIMG)

                await channel.send(embed=embed, file=img)


    @app_commands.command(
        name="move_card",
        description="debug-only command for moving a card from anywhere to your hand or either pile"
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.choices(suit=[
        app_commands.Choice(name="Wands",value="wands"),
        app_commands.Choice(name="Pentacles",value="pentacles"),
        app_commands.Choice(name="Cups",value="cups"),
        app_commands.Choice(name="Swords",value="swords"),
        app_commands.Choice(name="Major Arcana",value="major"),
    ],
    destination=[
        app_commands.Choice(name="Draw Pile",value="draw"),
        app_commands.Choice(name="Discard Pile", value="discard"),
        app_commands.Choice(name="My Hand",value="hand")
    ])
    async def move_card(self, interaction: discord.Interaction, value: int, suit: app_commands.Choice[str], destination: app_commands.Choice[str]):
        minordeck, majordeck = self.get_decks(interaction.channel)
        player = interaction.user.name

        #check if it's really the GM'
        gamemaster = self.get_gm(interaction.channel)
        if gamemaster is None or player != gamemaster.name:
            embed = discord.Embed(
                title = "Only the Gamemaster can use this command!",
                description = "Please ask your GM about it.",
                color = ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
            return None

        #first, which deck is the card being drawn from?
        is_major = False
        if suit.value == "major" and value <= 21 and value >= 1:
            is_major = True
        elif suit.value == "major" and value == 0:
            #the Fool counts as a minor card for this game
            is_major = False
        elif suit.value != "major" and value <= 14 and value >= 1:
            is_major = False
        else:
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " searched the discard piles for a card that does not exist!",
                description = "Please check your input, gamemaster!",
                color=ERRORCOLOR
            )
            await interaction.response.send_message(embed=embed)
            return None


        #now we know we're seeking a valid card, try to obtain it and send it to destination!
        result = ""
        if is_major:
            result = majordeck.debug_seek(player, value, suit.value, destination.value)
        else:
            result = minordeck.debug_seek(player, value, suit.value, destination.value)

        #check if a card was found or not
        if result[1] == "NOCARD":
            t = self.get_nick(interaction.user) + " DEBUG-searched all piles for *"
            if suit.value == "major":
                if value == 0:
                    t += "The "
                t += MAJORNAME[value]
            else:
                t += "The " + VALUENAME[value] + suit.name
            t+= "*, but it was not anywhere!"

            embed = discord.Embed(
                title = t,
                description = "This **really** shouldn't happen! Please contact a developer.",
                color=ERRORCOLOR
            )

            await interaction.response.send_message(embed=embed)
            return None
        else:
            # the card was found!
            colr = 0
            if is_major:
                colr = GMCOLOR
                prefix = ""
            else:
                colr = PLAYERCOLOR
                prefix = "The "

            des = ""
            if destination.value == "draw":
                des = "the draw pile"
            elif destination.value == "discard":
                des = "the discard pile"
            elif destination.value == "hand":
                des = "their hand"

            img = discord.File(result[0].get_filepath(), filename=result[0].filename)
            embed = discord.Embed(
                title = self.get_nick(interaction.user) + " fetches *" + prefix + result[0].name +"* from " + result[1] + "...",
                description = "... and puts it in " + des + "! Please check out for card-type mixing.",
                color = colr,
            )
            embed.set_image(url="attachment://" + result[0].filename)

            await interaction.response.send_message(file=img, embed=embed)





# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Tarot(bot))
