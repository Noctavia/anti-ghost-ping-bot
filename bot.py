import discord
from discord.ext import commands
import json

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='n?', intents=intents)

# Base de données simple
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"enabled": True, "whitelist": [], "redirect_channel": None}

# Sauvegarder la configuration
def save_config():
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

# --- ANTI-GHOST PING ---
@bot.event
async def on_ready():
    print(f'✅ Connecté en tant que {bot.user}')

@bot.event
async def on_message_delete(message):
    if not config["enabled"] or message.author.bot:
        return

    if message.mentions and message.author.id not in config["whitelist"]:
        mentions = ", ".join(user.mention for user in message.mentions)
        embed = discord.Embed(
            title="🚨 Anti-Ghost Ping 🚨",
            description=f"**Auteur :** {message.author.mention}\n"
                        f"**Mentions :** {mentions}\n"
                        f"**Message supprimé :** {message.content or '*Aucun contenu*'}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Détecté par l'anti-ghost ping")

        channel = message.guild.get_channel(config["redirect_channel"]) if config["redirect_channel"] else message.channel
        await channel.send(embed=embed)

# --- COMMANDES ---

# 1️⃣ Commande INFO
@bot.command()
async def info(ctx):
    status = "✅ **Activé**" if config["enabled"] else "❌ **Désactivé**"
    redirect = f"<#{config['redirect_channel']}>" if config["redirect_channel"] else "Pas défini"

    embed = discord.Embed(
        title="ℹ️ Informations sur l'Anti-Ghost Ping",
        color=discord.Color.blue()
    )
    embed.add_field(name="Statut", value=status, inline=False)
    embed.add_field(name="Canal de redirection", value=redirect, inline=False)
    embed.add_field(name="Utilisateurs whitelistés", value=str(len(config["whitelist"])), inline=False)
    embed.set_footer(text="Utilisez ?help pour voir toutes les commandes.")

    await ctx.send(embed=embed)

# 2️⃣ Commande MENTIONS REDIRECT
@bot.command()
@commands.has_permissions(administrator=True)
async def mentions_redirect(ctx, channel: discord.TextChannel):
    config["redirect_channel"] = channel.id
    save_config()

    embed = discord.Embed(
        title="✅ Redirection des mentions mise à jour",
        description=f"Les alertes seront désormais envoyées dans {channel.mention}.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# 3️⃣ Commande WHITELIST ADD
@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist_add(ctx, user: discord.User):
    if user.id in config["whitelist"]:
        embed = discord.Embed(
            title="⚠️ Déjà whitelisté",
            description=f"{user.mention} est déjà dans la whitelist.",
            color=discord.Color.orange()
        )
    else:
        config["whitelist"].append(user.id)
        save_config()
        embed = discord.Embed(
            title="✅ Ajouté à la whitelist",
            description=f"{user.mention} a été ajouté à la whitelist.",
            color=discord.Color.green()
        )
    await ctx.send(embed=embed)

# 4️⃣ Commande WHITELIST REMOVE
@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist_remove(ctx, user: discord.User):
    if user.id not in config["whitelist"]:
        embed = discord.Embed(
            title="❌ Non whitelisté",
            description=f"{user.mention} n'est pas dans la whitelist.",
            color=discord.Color.red()
        )
    else:
        config["whitelist"].remove(user.id)
        save_config()
        embed = discord.Embed(
            title="✅ Retiré de la whitelist",
            description=f"{user.mention} a été retiré de la whitelist.",
            color=discord.Color.green()
        )
    await ctx.send(embed=embed)

# 5️⃣ Commande WHITELIST LIST
@bot.command()
async def whitelist_list(ctx):
    if not config["whitelist"]:
        embed = discord.Embed(
            title="📋 Whitelist",
            description="Aucun utilisateur n'est whitelisté.",
            color=discord.Color.dark_gray()
        )
    else:
        whitelist_mentions = [f"<@{user_id}>" for user_id in config["whitelist"]]
        embed = discord.Embed(
            title="📋 Liste des utilisateurs whitelistés",
            description="\n".join(whitelist_mentions),
            color=discord.Color.blue()
        )
    await ctx.send(embed=embed)

# 6️⃣ Commande ETOGGLE
@bot.command()
@commands.has_permissions(administrator=True)
async def etoggle(ctx):
    config["enabled"] = not config["enabled"]
    save_config()

    status = "✅ **Activé**" if config["enabled"] else "❌ **Désactivé**"
    embed = discord.Embed(
        title="⚙️ Statut de l'Anti-Ghost Ping mis à jour",
        description=f"L'anti-ghost ping est maintenant : {status}",
        color=discord.Color.green() if config["enabled"] else discord.Color.red()
    )
    await ctx.send(embed=embed)

# 7️⃣ Commande HELP
@bot.command()
async def aide(ctx):
    embed = discord.Embed(
        title="📖 Aide - Commandes disponibles",
        description="Voici la liste des commandes disponibles :",
        color=discord.Color.purple()
    )
    embed.add_field(name="`n?info`", value="Affiche les informations sur l'anti-ghost ping.", inline=False)
    embed.add_field(name="`n?mentions_redirect #canal`", value="Redirige les alertes de ghost ping vers un canal spécifique.", inline=False)
    embed.add_field(name="`n?whitelist add @utilisateur`", value="Ajoute un utilisateur à la whitelist.", inline=False)
    embed.add_field(name="`n?whitelist remove @utilisateur`", value="Supprime un utilisateur de la whitelist.", inline=False)
    embed.add_field(name="`n?whitelist list`", value="Affiche la liste des utilisateurs whitelistés.", inline=False)
    embed.add_field(name="`n?etoggle`", value="Active ou désactive l'anti-ghost ping.", inline=False)
    embed.set_footer(text="Détecté par l'anti-ghost ping | Créé par ton bot préféré 🤖")

    await ctx.send(embed=embed)

# Gestion des erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="🚫 Permission refusée",
            description="Vous n'avez pas la permission d'utiliser cette commande.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="⚠️ Argument manquant",
            description="Veuillez fournir tous les arguments nécessaires.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore les commandes inconnues
    else:
        raise error

bot.run('VOTRE_TOKEN')
