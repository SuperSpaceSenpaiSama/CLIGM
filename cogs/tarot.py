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

MERGEDIMG = "mergedimage.png"

#the colors used for embed messages
INVISCOLOR = 0x350080
NEUTRALCOLOR = 0xBEBEFE
PLAYERCOLOR = 0x04BF22
GMCOLOR = 0xF5DA27
ERRORCOLOR = 0xBE0000

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






class Card():
    def __init__(self, name, suit, value):
        self.name = name  #The full name of the card
        self.suit = suit  #The suit.  can be  wands, pentacles, cups, swords or major
        self.value = value #The value. is 1 for Aces, 11 for Pages, 12 for Knights, 13 for Queens, 14 for Kings, and 0 for The Fool
        self.is_reversed = False #whether the card is reversed or not. doesn't really affect rules'
        self.filename = self.suit + str(self.value).zfill(2) + ".png" #The filename to the card's corresponding picture

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
            self.hands[username].append(crd) #adds the card to the user's hand
        return (msg, cnt)








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
    def get_nick(self, context):
        nickname = ""
        if context.author.nick is not None:
            nickname = context.author.nick
        elif context.author.display_name is not None:
            nickname = context.author.display_name
        else:
            nickname = context.author.name
        return nickname

    def get_decks(self, context):
        # for now, just returns the two deck attributes, This will be useful once the bot is built to handle multiple decks per channel
        return (self.player_deck, self.gm_deck)

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
        minordeck, majordeck = self.get_decks(context)
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
                title="The adventurer " + self.get_nick(context) + " tests Fate...",
                description=desc,
                color=PLAYERCOLOR,
            )
            embed.set_image(url="attachment://" + result[0].filename)

            await context.send(file=img, embed=embed)



    @commands.hybrid_command(
        name="draw_major",
        description="Draw a card from the GM deck",
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def draw_major(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context)
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
                title="The gamemaster " + self.get_nick(context)+ " draws a card...",
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
        minordeck, majordeck = self.get_decks(context)
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
                title= self.get_nick(context) + " peeks at the top of the discard pile...",
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
        minordeck, majordeck = self.get_decks(context)
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
                title= self.get_nick(context) + " peeks at the top of the discard pile...",
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
        minordeck, majordeck = self.get_decks(context)
        minordeck.shuffle()

        img = discord.File(IMGDIR + "cardbacks.png", filename="cardbacks.png")
        embed = discord.Embed(
            title= self.get_nick(context) + " shuffles the Players' deck...",
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
        minordeck, majordeck = self.get_decks(context)
        majordeck.shuffle()

        img = discord.File(IMGDIR + "cardbacks.png", filename="cardbacks.png")
        embed = discord.Embed(
            title= self.get_nick(context) + " shuffles the GM's deck...",
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
        minordeck, majordeck = self.get_decks(context)
        minordeck.shuffle()
        majordeck.shuffle()

        img = discord.File(IMGDIR + "cardbacks.png", filename="cardbacks.png")
        embed = discord.Embed(
            title= self.get_nick(context) + " shuffles both decks...",
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
        minordeck, majordeck = self.get_decks(context)

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

        embed = discord.Embed(
            title = "Debug: Decks Status",
            description = desc,
            color=NEUTRALCOLOR,
        )

        await context.send(embed=embed)



    #Here begins the commands for Challenge Phase play!

    @commands.hybrid_command(
        name="deal_player",
        description="Draw 4 cards from the Players' deck, and then hold them in your hand."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    async def deal_player(self, context: Context) -> None:
        minordeck, majordeck = self.get_decks(context)

        player = context.author.name

        output = minordeck.deal_cards(4, player) #deal hand to the player. use the player's unique username (instead of their mutable & non-unique Display Name) as the key

        await context.interaction.response.defer()

        if output[0] == "NOHAND":
            embed = discord.Embed(
                title = "All cards are in someone's hand!!!",
                description = "How did you even manage this? Please use the end-of-round command to reset the Player's deck.",
                color=ERRORCOLOR
            )

            await context.send(embed=embed)
        else:
            if output[0] == "SHUFFLED":
                embed = discord.Embed(
                    title = "The draw pile has run out with " + str(output[1]) + " card(s) left to draw!",
                    description = "Shuffling the Player's discard pile...",
                    color=PLAYERCOLOR
                )

                await context.channel.send(embed=embed)

            embed2 = discord.Embed(
                title = "The Adventurer " + self.get_nick(context) + " deals 4 cards into their hand!",
                description="What sort of strategems lie hidden between your fingers...?",
                color=PLAYERCOLOR
            )
            await context.channel.send(embed=embed2)


            desc = ""
            imagefiles = []
            for card in minordeck.hands[player]:
                desc += "The " + card.name + "\n"
                imagefiles.append(IMGDIR + card.filename)

            desc = desc[:-1] #removes the final \n character

            #sets up the embed image
            merge_images(imagefiles)
            img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)

            embed3 = discord.Embed(
                title = "You have drawn the following cards, " + self.get_nick(context) + ". Use them wisely!",
                description = desc,
                color = INVISCOLOR,
            )
            embed3.set_image(url="attachment://" + MERGEDIMG)

            await context.interaction.followup.send(embed=embed3, ephemeral = True, file=img)

    @commands.hybrid_command(
        name="deal_gm",
        description="Draw cards from the GM's deck, and then hold them in your hand."
    )
    @app_commands.guilds(discord.Object(id=1121934159988936724))
    @app_commands.describe(
        cardcount="How many cards are you drawing?"
    )
    async def deal_gm(self, context: Context, cardcount: int) -> None:
        minordeck, majordeck = self.get_decks(context)

        player = context.author.name

        output = majordeck.deal_cards(cardcount, player) #deal hand to the player. use the player's unique username (instead of their mutable & non-unique Display Name) as the key

        await context.interaction.response.defer()

        if output[0] == "NOHAND":
            embed = discord.Embed(
                title = "All cards are in someone's hand!!!",
                description = "How did you even manage this? Please use the end-of-round command to reset the Player's deck.",
                color=ERRORCOLOR
            )

            await context.send(embed=embed)
        else:
            if output[0] == "SHUFFLED":
                embed = discord.Embed(
                    title = "The draw pile has run out with " + str(output[1]) + " card(s) left to draw!",
                    description = "Shuffling the GM's discard pile...",
                    color=GMCOLOR
                )

                await context.channel.send(embed=embed)

            embed2 = discord.Embed(
                title = "The Gamemaster " + self.get_nick(context) + " deals " + str(cardcount) + " cards into their hand!",
                description="What sorts of doom does The Dungeon have in store now...?",
                color=GMCOLOR
            )
            await context.channel.send(embed=embed2)


            desc = ""
            imagefiles = []
            for card in majordeck.hands[player]:
                desc +=  card.name + "\n"
                imagefiles.append(IMGDIR + card.filename)

            desc = desc[:-1] #removes the final \n character

            #sets up the embed image
            merge_images(imagefiles)
            img = discord.File(IMGDIR + MERGEDIMG, filename=MERGEDIMG)

            embed3 = discord.Embed(
                title = "You have drawn the following cards, " + self.get_nick(context) + ". Use them wisely!",
                description = desc,
                color = INVISCOLOR,
            )
            embed3.set_image(url="attachment://" + MERGEDIMG)

            await context.interaction.followup.send(embed=embed3, ephemeral = True, file=img)




# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Tarot(bot))
