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
    "The Fool",
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

class Card():
    def __init__(self, name, suit, value):
        self.name = name  #The full name of the card
        self.suit = suit  #The suit.  can be  wands, pentacles, cups, swords or major
        self.value = value #The value. is 1 for Aces, 11 for Pages, 12 for Knights, 13 for Queens, 14 for Kings, and 0 for The Fool
        self.filename = self.suit + str(self.value).zfill(2) + ".png" #The filename to the card's corresponding picture
        self.filepath = IMGDIR + self.filename

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


class Deck():
    def __init__(self, major):
        self.drawpile = []
        self.discardpile = []
        self.hands = []

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

            # write code for  shuffling HANDS here!!!


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

        return (drawncard, msg)  # returns the card that was drawn, and a status message!

    def show_discard(self):
        #shows the top card of the discard pile
        if len(self.discardpile) != 0:
            return self.discardpile[-1]
        else:
            return "NOCARD"







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
        self.gm_deck = Deck(major=True)
        self.player_deck = Deck(major=False)

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.


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
            color=0xBEBEFE,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="draw_minor",
        description="Draw a card from the player deck",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def draw_minor(self, context: Context) -> None:
        result = self.player_deck.draw()

        if result[1] == "NOCARD":
            embed = discord.Embed(
                title = "The draw pile is empty, adventurer! You need to shuffle this deck!",
                color=0xBE0000,
            )
            await context.send(embed=embed)
        else:
            img = discord.File(result[0].filepath, filename=result[0].filename)
            desc = "You have drawn the *" + result[0].name + "*!"
            if result[1] == "LASTCARD":
                desc = desc + "\nThis was the last card in the draw pile!"
            elif result[1] == "FOOL":
                desc = desc + "\nThe Fool demands that you shuffle your decks!"

            embed = discord.Embed(
                title="The adventurer " + context.author.nick + " tests Fate...",
                description=desc,
                color=0xBEBEFE,
            )
            embed.set_image(url="attachment://" + result[0].filename)

            await context.send(file=img, embed=embed)



    @commands.hybrid_command(
        name="draw_major",
        description="Draw a card from the GM deck",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def draw_major(self, context: Context) -> None:
        result = self.gm_deck.draw()

        if result[1] == "NOCARD":
            embed = discord.Embed(
                title = "The draw pile is empty, gamemaster! You need to shuffle this deck!",
                color=0xBE0000,
            )
            await context.send(embed=embed)
        else:
            img = discord.File(result[0].filepath, filename=result[0].filename)
            desc = "You have drawn the *" + result[0].name + "*!"
            if result[1] == "LASTCARD":
                desc = desc + "\nThis was the last card in the draw pile!"

            embed = discord.Embed(
                title="The gamemaster " + context.author.nick + " draws a card...",
                description=desc,
                color=0xBEBEFE,
            )
            embed.set_image(url="attachment://" + result[0].filename)

            await context.send(file=img, embed=embed)


    @commands.hybrid_command(
        name="debug",
        description="Show the status of all decks for debug purposes",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def debug(self, context: Context) -> None:
        desc = "**PLAYER DRAWPILE:**"

        for card in self.player_deck.drawpile:
            desc += "\n" + card.name + ", " + card.suit + ", " + str(card.value)

        desc += "\n\n**PLAYER DISCARD PILE:**"

        for card in self.player_deck.discardpile:
            desc += "\n" + card.name + ", " + card.suit + ", " + str(card.value)

        desc += "\n\n**GM DRAWPILE:**"

        for card in self.gm_deck.drawpile:
            desc += "\n" + card.name + ", " + card.suit + ", " + str(card.value)

        desc += "\n\n**GM DISCARD PILE:**"

        for card in self.gm_deck.discardpile:
            desc += "\n" + card.name + ", " + card.suit + ", " + str(card.value)

        embed = discord.Embed(
            title = "Debug: Decks Status",
            description = desc,
            color=0xFFFFFF,
        )

        await context.send(embed=embed)



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Tarot(bot))
