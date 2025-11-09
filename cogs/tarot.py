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
    async def testcommand(self, context: Context) -> None:
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

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Tarot(bot))
