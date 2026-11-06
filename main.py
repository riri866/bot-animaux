import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print (f"Connecte en tant que {bot.user}")
    await bot.tree.sync()
    


# Commande prefixee : !ping
@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")


# Commande slash : /salut
@bot.tree.command(name="salut", description="Le bot te dit bonjour")
async def salut(interaction: discord.Interaction):
    await interaction.response.send_message(f"Salut {interaction.user.mention} !")


# Commande prefixee : !est tu chinois ?
@bot.command(name="chinois", description="Le bot te dit si tu es chinois et peux demander a un menbre aussi")
async def est_tu_chinois(ctx, membre: discord.Member = None):

    if membre is None:
        membre = ctx.author

    await ctx.send(f"{membre.mention}, est tu chinois ? Réponds par **oui** ou **non**.")

    def check(message):
        return message.author == membre and message.channel == ctx.channel

    reponse = await bot.wait_for("message", check=check)
    contenu = reponse.content.lower().strip()

    if contenu == "oui":
        await ctx.send(f"Va manger des chiens {ctx.author.mention} !")
    elif contenu == "non":
        await ctx.send (f"Va manger du poulet {ctx.author.mention} !")
    else:
        await ctx.send(f"Repond bien neuille {ctx.author.mention}")


bot.run(os.getenv("DISCORD_TOKEN"))
