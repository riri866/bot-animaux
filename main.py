import os
import random
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from liste_quiz import questions_quiz as quiz_questions, animaux_totems as totem_animals, combat_animals as combat_animals

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

@bot.command(name="duel", description="Combat entre animaux")
async def duel(ctx, opponent: discord.Member = None):

    is_against_bot = opponent is None or opponent == bot.user

    if is_against_bot:
        await ctx.send(f"{ctx.author.mention} lance un duel contre le bot")
    else:
        if opponent == ctx.author:
            await ctx.send(f"{ctx.author.mention}, tu ne pas te battre contre toi-même")
            return
        await ctx.send(f"{ctx.author.mention} veut affronter {opponent.mention} en duel")

    P1_animal = random.choice(combat_animals).copy()

    P2_animal = random.choice(combat_animals).copy()

    embed_start = discord.Embed(
        title="Tirage au sort",
        description=f"{ctx.author.mention} a tiré {P1_animal['name']} \n"
                    f"({P1_animal['attack']} {P1_animal['defense']} {P1_animal['vitesse']} {P1_animal['hp']})\n\n"
                    f"VS\n\n"
                    f"{(bot.user.display_name if is_against_bot else opponent.display_name)} invoque : {P2_animal['name']} \n"
                    f"({P2_animal['attack']} {P2_animal['defense']} {P2_animal['vitesse']} {P2_animal['hp']})\n\n",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed_start)
    await asyncio.sleep(2)

    await ctx.send("C'est l'heure du du-du-du-duel !")
    p1 = {"user": ctx.author, "animal": P1_animal, "hp": P1_animal["hp"]}
    p2 = {"user": (bot.user if is_against_bot else opponent), "animal": P2_animal, "hp": P2_animal["hp"]}

    if P1["animal"]["vitesse"] > P2["animal"]["vitesse"]:
        attacker, defender = p1, p2
    else:
        attacker, defender = p2, p1

    turn = 1
    while P1["hp"] > 0 and P2["hp"] > 0:
        await asyncio.sleep(2)

        speed_diff = attacker["animal"]["vitesse"] - defender["animal"]["vitesse"]
        dodge_chance = max(5, min(30, speed_diff * 2))

        if random.randint(1, 100) <= dodge_chance:
            await ctx.send(f"{defender['animal']['name']} ({defender['user'].display_name}) esquive l'attaque avec grâce et agilité")
        else:
            raw_damage = attacker["animal"]["attack"]
            defense_val = defender["animal"]["defense"]
            final_damage = max(5, raw_damage - (defense_val // 2))

            defender["hp"] -= final_damage
        if defender["hp"] <= 0:

            await ctx.send(f"{attacker['animal']['name']} inflige {final_damage} dégâts à {defender['animal']['name']})"
                           f" PV restant : {P1['animal']['name']} ({P1['hp']}) {P2['animal']['name']} ({P2['hp']})")

        if defender["hp"] <= 0:
            winner = attacker
            await ctx.send(f"Le duel est gagné par {winner['user'].mention} remporte le duel grâce à son {winner['animal']['name']}")
            break

        attacker, defender = defender, attacker
        turn += 1    

bot.run(os.getenv("DISCORD_TOKEN"))
