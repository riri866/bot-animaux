import os
import random
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from liste_quiz import questions_quiz as quiz_questions, animaux_totems as totem_animals

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
async def ping(context):
    await context.send("Pong !")


# Commande slash : /salut
@bot.tree.command(name="salut", description="Le bot te dit bonjour")
async def say_hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Salut {interaction.user.mention} !")

# Commande quiz pour connaitre ton animal spirituel (!quiz)
@bot.command(name="quiz", description="Découvre ton animal totem")
async def animal_quiz(context):

    valid_choices = [
        ["montagne", "plage", "foret", "ville"],
        ["calme", "loyal", "curieux", "puissant"],
        ["matin", "apres-midi", "nuit"],
        ["fuite", "attaque", "strategie", "camouflage"],
        ["viande", "poisson", "fruits", "tout"]
    ]

    while True :
        await context.send(f"Bienvenue au quiz des animaux totem {context.author.mention} \n")

        def check_message(received_message):
            return received_message.author == context.author and received_message.channel == context.channel

        user_responses = []
        trap_detected = False

        for question_index, current_question in enumerate(quiz_questions):
            await context.send(f"{current_question}")

            message = await bot.wait_for("message", check=check_message)
            cleaned_response = message.content.lower().strip()
            user_responses.append(message.content)

            if cleaned_response not in valid_choices[question_index]:
                trap_detected = True

        await context.send("le bot analyse t'es réponse  ...")

        if trap_detected:
            prank_embed = discord.Embed(
                title="JE T'AI EU !",
                description="",
                color=discord.Color.red()
            )
            prank_embed.set_image(url="https://media.tenor.com/6MY0yMmbs3IAAAAM/doakes-im-watching-you.gif")
            prank_embed.set_footer(text=f"Bien piégé {context.author.display_name}")

            await context.send(embed=prank_embed)
            await asyncio.sleep(3)
            continue

        total_characters = sum(len(response) for response in user_responses)
        animal_index = total_characters % len(totem_animals)
        animal = totem_animals[animal_index]

        result_embed = discord.Embed(
            title=f"Ton animal totem est : {animal['nom']}",
            description=f"{animal['description']}\n\n Tes réponses : " + ", ".join(user_responses),
            color=discord.Color.green()
        )
        result_embed.set_image(url=animal['img'])
        result_embed.set_footer(text=f"quiz fait pour {context.author.display_name}")

        await context.send(embed=result_embed)
        break

bot.run(os.getenv("DISCORD_TOKEN"))
