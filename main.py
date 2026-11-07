import json
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

        data = load_user_data()
        user_id_str = str(context.author.id)
        if user_id_str not in data:
            data[user_id_str] = {
                "name":context.author.name,
                "duels_played": 0,
                "wins": 0,
                "losses": 0,
                "totem_animal": animal['nom']
            }

        data[user_id_str]["totem"] = animal['nom']
        save_user_data(data)

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

    p1_animal = random.choice(combat_animals).copy()
    p2_animal = random.choice(combat_animals).copy()

    embed_start = discord.Embed(
        title="Tirage au sort",
        description=(
            f"{ctx.author.mention} a tiré {p1_animal['name']} \n"
            f" Attaque = {p1_animal['attack']}\n"
            f" Défense = {p1_animal['defense']}\n"
            f" Vitesse = {p1_animal['vitesse']}\n"
            f" HP = {p1_animal['hp']}\n\n"
            f"VS\n\n"
            f"{(bot.user.display_name if is_against_bot else opponent.display_name)} invoque : {p2_animal['name']} \n"
            f" Attaque = {p2_animal['attack']}\n"
            f" Défense = {p2_animal['defense']}\n"
            f" Vitesse = {p2_animal['vitesse']}\n"
            f" HP = {p2_animal['hp']}"
        ),
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed_start)
    await asyncio.sleep(2)

    await ctx.send("C'est l'heure du du-du-du-duel !")
    p1 = {"user": ctx.author, "animal": p1_animal, "hp": p1_animal["hp"]}
    p2 = {"user": (bot.user if is_against_bot else opponent), "animal": p2_animal, "hp": p2_animal["hp"]}

    if p1["animal"]["vitesse"] > p2["animal"]["vitesse"]:
        attacker, defender = p1, p2
    else:
        attacker, defender = p2, p1

    turn = 1

    while p1["hp"] > 0 and p2["hp"] > 0:
        await asyncio.sleep(2.0)

        speed_diff = attacker["animal"]["vitesse"] - defender["animal"]["vitesse"]
        dodge_chance = max(5, min(25, speed_diff * 1.5))

        defender_name = f"{defender['animal']['name']} ({defender['user'].display_name})"
        attacker_name = f"{attacker['animal']['name']} ({attacker['user'].display_name})"

        tour_header = f"\n"

        if random.randint(1, 100) <= dodge_chance:
            dodge_messages = [
                f"{tour_header}{defender_name} esquive l'attaque de {attacker_name} avec grâce et agilité",
                f"{tour_header}{defender_name} pare le coup de {attacker_name} au dernier moment",
            ]
            await ctx.send(random.choice(dodge_messages))

        else:
            raw_damage = attacker["animal"]["attack"]
            defense_val = defender["animal"]["defense"]
            final_damage = max(5, raw_damage - (defense_val // 2))

            defender["hp"] -= final_damage
            
            await ctx.send(
                f"{tour_header}"
                f"{attacker_name} inflige {final_damage} dégât à {defender_name}\n"
                f"{p1['animal']['name']} : {max(0, p1['hp'])} PV | {p2['animal']['name']} : {max(0, p2['hp'])} PV"
                f"\n"  
            )

        if defender["hp"] <= 0:
            winner = attacker
            loser = defender

            data = load_user_data()

            for p in [winner, loser]:
                if p["user"].bot:
                    continue

                uid = str(p["user"].id)
                if uid not in data:
                    data[uid] = {
                        "name": p["user"].name,
                        "duels_played": 0,
                        "wins": 0,
                        "losses": 0,
                        "totem": "Aucun"
                    }

                data[uid]["duels_played"] += 1
                if p == winner:
                    data[uid]["wins"] +=1
                else:
                    data[uid]["losses"] += 1

            save_user_data(data)


            await ctx.send(f"Le duel est gagné par {winner['user'].mention} remporte le duel grâce à son {winner['animal']['name']}")
            break

        attacker, defender = defender, attacker
        turn += 1

@bot.command(name="aide", description="Affiche la liste des commandes disponibles")
async def help_command(ctx):
    help_embed = discord.Embed(
        title="Guide et Commandes du Bot Animaux",
        description="Voici la liste de toutes le commandes disponibles:",
        color=discord.Color.blue()
    )
    help_embed.add_field(name="!ping", value="Teste le bot", inline=False)
    help_embed.add_field(name="!quiz", value="Découvre tona animal totem", inline=False)
    help_embed.add_field(name="!duel [@opponent]", value="lance un combat d'animaux", inline=False)
    help_embed.add_field(name="!liste", value="Affiche l'ensemble des naimaux du serveur", inline=False)
    help_embed.add_field(name="!aide", value="Affiche ce message d'aide", inline=False)

    help_embed.set_footer(text=f"demandé par {ctx.author.display_name}")
    await ctx.send(embed=help_embed)

@bot.command(name="liste", description="Affiche l'ensemble des animaux du serveur")
async def animal_list(ctx):
    totem_details = [f" {animal['nom']}" for animal in totem_animals]

    combat_details = [
        f" {a['name']}\n"
        f" attaque = {a['attack']}\n"
        f" defense = {a['defense']}\n"
        f" vitesse = {a['vitesse']}\n"
        f" hp = {a['hp']}\n"
        for a in combat_animals
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

DATA_FILE = "users_data.json"

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


@bot.command(name="info", description="Afficher des informations")
async def info_command(ctx, member: discord.Member = None):
    if member is None:
        member = bot.user

    data = load_user_data()
    user_id_str = str(member.id)

    if user_id_str not in data:
        data[user_id_str] = {
            "name":member.name,
            "duels_played": 0,
            "wins": 0,
            "losses": 0,
            "totem_animal": None
        }
        save_user_data(data)

    user_info = data[user_id_str]

    info_embed = discord.Embed(
        title=f"Profil de {member.display_name}",
        color=discord.Color.gold()
    )
    if member.avatar:
        info_embed.set_thumbnail(url=member.avatar.url)

    info_embed.add_field(name="Animal Totem", value=user_info.get("totem", "Inconnu"), inline=False)
    info_embed.add_field(name="Duels joués", value=str(user_info.get("duels_played", 0)), inline=True)
    info_embed.add_field(name="Defaits", value=str(user_info.get("losses", 0)), inline=True)
    info_embed.add_field(name="Victoires", value=str(user_info.get("wins", 0)), inline=True)

    info_embed.set_footer(text=f"Données de la base de donnée, demandées par {ctx.author.display_name}")
    await ctx.send(embed=info_embed)

bot.run(os.getenv("DISCORD_TOKEN"))
