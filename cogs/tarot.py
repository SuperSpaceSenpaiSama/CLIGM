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

class Card():
    def __init__(self, name, suit, value):
        self.name = name  #The full name of the card
        self.suit = suit  #The suit.  can be  wands, pentacles, cups, swords or major
        self.value = value #The value. is 1 for Aces, 11 for Pages, 12 for Knights, 13 for Queens, 14 for Kings, and 0 for The Fool

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
            elif self.suit = "swords":
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
        if len(self.drawpile) == 0:
            return "NOCARD"
        drawncard = self.drawpile.pop(random.randint(0,len(self.drawpile) - 1)) # draws a random card from the deck, removing it from drawpile
        self.discardpile.append(drawncard) # adds the card to the discard pile

        return drawncard.name  # returns just the name of the card!




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
        #random.choice(os.listdir(/tarot/minor/))
        pass

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Tarot(bot))
