import json
import os
import random
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from liste_quiz import questions_quiz as quiz_questions, animaux_totems as totem, combat_animals as animals_fight

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "settings.json"
DODGE_MIN, DODGE_MAX = 5, 23
MIN_DAMAGE = 5
TURN_DELAY = 1

def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return{}
    return {}

def save_user_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user(data, member):
    uid = str(member.id)
    if uid not in data:
        data[uid] = {"name": member.name, "duels_played": 0,
                     "wins": 0, "losses":0, "totem": "Aucun"}
    return data[uid]


@bot.event
async def on_ready():
    print (f"Connecte en tant que {bot.user}")
    await bot.tree.sync()


@bot.command()
async def ping(context):
    await context.send("Pong !")


@bot.tree.command(name="salut", description="Le bot te dit bonjour")
async def say_hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Salut {interaction.user.mention} !")


@bot.command(name="animal")
async def animals_details(ctx, *, name: str = None):
    if name is None:
        await ctx.send("Utilise : !animal nom")
        return
    
    search = name.lower().strip()
    combat_animal = next((a for a in animals_fight if a["name"].lower() == search), None)
    totem_animal = next((a for a in totem if a["nom"].lower() == search), None)

    if combat_animal is None and totem_animal is None:
        await ctx.send("Aniaml introuvable, fait liste pour voir les animaux")
        return

    title = totem_animal["nom"] if totem_animal else combat_animal["name"]
    embed = discord.Embed(title=title, color=discord.Color.orange())

    if totem_animal:
        embed.description = totem_animal["description"]
        embed.set_image(url=totem_animal["img"])
    if combat_animal:
        embed.add_field(name="Stats de combat", value=format_stats(combat_animal), inline=False)

    await ctx.send(embed=embed)

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

            try:
                message = await bot.wait_for("message", check=check_message, timeout=60)
            except asyncio.TimeoutError:
                await context.send("Temps écoulé, relance !quiz")
                return
            
            cleaned_response = message.content.lower().strip()
            user_responses.append(message.content)

            if cleaned_response not in valid_choices[question_index]:
                trap_detected = True

        await context.send("le bot analyse tes réponses  ...")

        if trap_detected:
            prank_embed = discord.Embed(
                title="JE T'AI EU !",
                description="",
                color=discord.Color.red()
            )
            prank_embed.set_image(url="https://media.tenor.com/6MY0yMmbs3IAAAAM/doakes-im-watching-you.gif")
            prank_embed.set_footer(text=f"Bien piégé {context.author.display_name}")

            await context.send(embed=prank_embed)
            await asyncio.sleep(TURN_DELAY)
            continue

        total_characters = sum(len(response) for response in user_responses)
        animal_index = total_characters % len(totem)
        animal = totem[animal_index]

        result_embed = discord.Embed(
            title=f"Ton animal totem est : {animal['nom']}",
            description=f"{animal['description']}\n\n Tes réponses : " + ", ".join(user_responses),
            color=discord.Color.green()
        )
        result_embed.set_image(url=animal['img'])
        result_embed.set_footer(text=f"quiz fait pour {context.author.display_name}")

        data = load_user_data()
        get_user(data, context.author)["totem"] = animal["nom"]
        save_user_data(data)

        await context.send(embed=result_embed)
        break


def format_stats(animal):
    return(f"Attaque = {animal['attack']}\n"
           f"Défense = {animal['defense']}\n"
           f"Vitesse = {animal['vitesse']}\n"
           f"HP = {animal['hp']}")

def record_result(winner, loser):
    data = load_user_data()
    for p, won in ((winner, True), (loser, False)):
        user = get_user(data, p["user"])
        user["duels_played"] += 1
        user["wins" if won else "losses"] += 1
    save_user_data(data)


@bot.command(name="duel", description="Combat entre animaux")
async def duel(ctx, opponent: discord.Member = None):
    if opponent == ctx.author:
        await ctx.send(f"{ctx.author.mention}, tu ne peux pas te battre contre toi-même")
        return

    is_against_bot = opponent is None or opponent == bot.user
    opponent_user = bot.user if is_against_bot else opponent
    await ctx.send(f"{ctx.author.mention} affronte {opponent_user.mention} en duel")


    p1_animal = random.choice(animals_fight)
    p2_animal = random.choice(animals_fight)

    embed_start = discord.Embed(
        title="Tirage au sort",
        description=(
            f"{ctx.author.mention} a tiré {p1_animal['name']}\n{format_stats(p1_animal)}\n\n"
            f"{opponent_user.display_name} invoque : {p2_animal['name']}\n{format_stats(p2_animal)}"             
        ),
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed_start)
    await asyncio.sleep(TURN_DELAY)

    await ctx.send("C'est l'heure du du-du-du-duel !")
    p1 = {"user": ctx.author, "animal": p1_animal, "hp": p1_animal["hp"]}
    p2 = {"user": opponent_user, "animal": p2_animal, "hp": p2_animal["hp"]}

    if p1["animal"]["vitesse"] > p2["animal"]["vitesse"]:
        attacker, defender = p1, p2
    else:
        attacker, defender = p2, p1

    while p1["hp"] > 0 and p2["hp"] > 0:
        await asyncio.sleep(TURN_DELAY)

        speed_diff = defender["animal"]["vitesse"] - attacker["animal"]["vitesse"]
        dodge_chance = max(DODGE_MIN, min(DODGE_MAX, speed_diff * 1.5))
        defender_name = defender["animal"]["name"]
        attacker_name = attacker["animal"]["name"]

        if random.randint(1, 100) <= dodge_chance:
            await ctx.send(random.choice([
                f"{defender_name} esquive l'attaque de {attacker_name} avec grâce et agilité",
                f"{defender_name} pare le coup de {attacker_name} au dernier moment",
                f"----------------------\n"
            ]))

        else:
            damage = max(MIN_DAMAGE, attacker["animal"]["attack"] - defender["animal"]["defense"] //2)
            defender["hp"] -= damage
            await ctx.send(
                f"{attacker_name} inflige {damage} dégâts à {defender_name}\n"
                f"{p1['animal']['name']} : {max(0, p1['hp'])} PV | "
                f"{p2['animal']['name']} : {max(0, p2['hp'])} PV\n"
                f"{'-' * 60}"
            )

        if defender["hp"] <= 0:
            record_result(attacker, defender)
            await ctx.send(f"{attacker['user'].mention} remporte le duel grâce à son {attacker_name}")
            return

        attacker, defender = defender, attacker

@bot.command(name="aide", description="Affiche la liste des commandes disponibles")
async def help_command(ctx):
    help_embed = discord.Embed(
        title="Guide et Commandes du Bot Animaux",
        description="Voici la liste de toutes les commandes disponibles:",
        color=discord.Color.blue()
    )
    help_embed.add_field(name="!ping", value="Teste le bot", inline=False)
    help_embed.add_field(name="!quiz", value="Découvre ton animal totem", inline=False)
    help_embed.add_field(name="!duel [@opponent]", value="lance un combat d'animaux", inline=False)
    help_embed.add_field(name="!liste", value="Affiche l'ensemble des animaux du serveur", inline=False)
    help_embed.add_field(name="!info [@someone]", value="Affiche les informations du joueur", inline=False)
    help_embed.add_field(name="!aide", value="Affiche ce message d'aide", inline=False)
    help_embed.add_field(name="!animal nom", value="affiche les informations de l'animal", inline=False)

    help_embed.set_footer(text=f"demandé par {ctx.author.display_name}")
    await ctx.send(embed=help_embed)

@bot.command(name="liste", description="Affiche l'ensemble des animaux du serveur")
async def animal_list(ctx):
    totem_details = [f" {animal['nom']}" for animal in totem]

    combat_details = [
        f" {a['name']}\n"
        f" attaque = {a['attack']}\n"
        f" defense = {a['defense']}\n"
        f" vitesse = {a['vitesse']}\n"
        f" hp = {a['hp']}\n"
        for a in animals_fight
    ]

    list_embed = discord.Embed(
        title="Catalogue des Animaux",
        description="Voici les animaux du serveur :",
        color=discord.Color.purple()
    )

    list_embed.add_field(
        name="Animaux du Quiz",
        value="\n".join(totem_details),
        inline=False
    )

    list_embed.add_field(
        name="Animaux de Combat",
        value="\n".join(combat_details),
        inline=False
    )

    list_embed.set_footer(text=f"Demandé par {ctx.author.display_name}")
    await ctx.send(embed=list_embed)




@bot.command(name="info", description="Afficher des informations")
async def info_command(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    data = load_user_data()
    user_info = get_user(data, member)
    save_user_data(data)

    info_embed = discord.Embed(
        title=f"Profil de {member.display_name}",
        color=discord.Color.gold()
    )
    if member.avatar:
        info_embed.set_thumbnail(url=member.avatar.url)

    info_embed.add_field(name="Animal Totem", value=user_info.get("totem", "Inconnu"), inline=False)
    info_embed.add_field(name="Duels joués", value=str(user_info.get("duels_played", 0)), inline=True)
    info_embed.add_field(name="Défaites", value=str(user_info.get("losses", 0)), inline=True)
    info_embed.add_field(name="Victoires", value=str(user_info.get("wins", 0)), inline=True)

    info_embed.set_footer(text=f"Données de la base de donnée, demandées par {ctx.author.display_name}")
    await ctx.send(embed=info_embed)

bot.run(os.getenv("DISCORD_TOKEN"))
