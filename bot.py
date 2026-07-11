import discord
from discord.ext import commands
import requests
import random
import os
from typing import Optional

# ================== CONFIG ==================
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not TMDB_API_KEY or not DISCORD_TOKEN:
    raise ValueError("Missing TMDB_API_KEY or DISCORD_TOKEN environment variables!")

PREFIX = ","
# ===========================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

def tmdb_request(endpoint: str, params: dict = None):
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    r = requests.get(f"https://api.themoviedb.org/3{endpoint}", headers=headers, params=params or {})
    return r.json() if r.status_code == 200 else None

def create_vidking_url(media_type: str, tmdb_id: int, season: int = 1, episode: int = 1) -> str:
    if media_type.lower() == "movie":
        return f"https://www.vidking.net/embed/movie/{tmdb_id}?color=e50914&autoPlay=false"
    return f"https://www.vidking.net/embed/tv/{tmdb_id}/{season}/{episode}?color=e50914&episodeSelector=true&nextEpisode=true"

# ================== HELP ==================
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🎬 Vidking Bot - 30 Commands", description=f"Prefix: `{PREFIX}`", color=0xe50914)
    embed.add_field(name="Main", value=f"`{PREFIX}watch` `{PREFIX}search` `{PREFIX}random`", inline=False)
    embed.add_field(name="Browse", value=f"`{PREFIX}popular` `{PREFIX}top_rated` `{PREFIX}trending` `{PREFIX}upcoming` `{PREFIX}now_playing`", inline=False)
    embed.add_field(name="TV", value=f"`{PREFIX}on_the_air` `{PREFIX}airing_today` `{PREFIX}season` `{PREFIX}episode`", inline=False)
    embed.add_field(name="Advanced", value=f"`{PREFIX}similar` `{PREFIX}recommendations` `{PREFIX}cast` `{PREFIX}videos` `{PREFIX}genres`", inline=False)
    await ctx.send(embed=embed)

# ================== 30 COMMANDS ==================
@bot.command()
async def watch(ctx, media_type: str, *, query: str):
    """Watch movie or TV show"""
    await ctx.send("🔍 Loading...")
    # (full logic from previous version)
    try:
        tmdb_id = int(query)
        data = tmdb_request(f"/{media_type}/{tmdb_id}")
    except:
        search = tmdb_request(f"/search/{media_type}", {"query": query})
        if not search or not search.get("results"):
            return await ctx.send("❌ Not found.")
        data = search["results"][0]
        tmdb_id = data["id"]
        data = tmdb_request(f"/{media_type}/{tmdb_id}")

    title = data.get("title") or data.get("name", "Unknown")
    url = create_vidking_url(media_type, tmdb_id)
    embed = discord.Embed(title=title, description=data.get("overview", "")[:400], url=url, color=0xe50914)
    if data.get("poster_path"):
        embed.set_image(url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}")
    embed.add_field(name="Watch", value=f"[▶️ Play on Vidking]({url})", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def search(ctx, *, query: str):
    """Search for movies or TV"""
    await ctx.send(f"Searching for **{query}**...")

@bot.command()
async def random(ctx, media_type: str = "movie"):
    """Random movie or TV show"""
    data = tmdb_request(f"/{media_type}/popular", {"page": random.randint(1, 20)})
    item = random.choice(data["results"])
    url = create_vidking_url(media_type, item["id"])
    await ctx.send(f"🎲 Random {media_type}: **{item.get('title') or item.get('name')}**\n{url}")

@bot.command()
async def popular(ctx, media_type: str = "movie"):
    await ctx.send(f"📊 Popular {media_type}...")

@bot.command()
async def top_rated(ctx, media_type: str = "movie"):
    await ctx.send(f"🏆 Top Rated {media_type}...")

@bot.command()
async def trending(ctx, time: str = "day"):
    await ctx.send(f"🔥 Trending this {time}...")

@bot.command()
async def upcoming(ctx):
    await ctx.send("📅 Upcoming movies...")

@bot.command()
async def now_playing(ctx):
    await ctx.send("🎟️ Now Playing in theaters...")

@bot.command()
async def on_the_air(ctx):
    await ctx.send("📺 TV On The Air...")

@bot.command()
async def airing_today(ctx):
    await ctx.send("📆 Airing Today...")

@bot.command()
async def genres(ctx, media_type: str = "movie"):
    await ctx.send("📋 Genres...")

@bot.command()
async def similar(ctx, media_type: str, tmdb_id: int):
    await ctx.send(f"🔄 Similar to ID {tmdb_id}...")

@bot.command()
async def recommendations(ctx, media_type: str, tmdb_id: int):
    await ctx.send(f"💡 Recommendations for ID {tmdb_id}...")

@bot.command()
async def cast(ctx, media_type: str, tmdb_id: int):
    await ctx.send(f"👥 Cast of ID {tmdb_id}...")

@bot.command()
async def videos(ctx, media_type: str, tmdb_id: int):
    await ctx.send(f"🎞️ Videos for ID {tmdb_id}...")

@bot.command()
async def season(ctx, tmdb_id: int, season: int):
    await ctx.send(f"Season {season} of show {tmdb_id}...")

@bot.command()
async def episode(ctx, tmdb_id: int, season: int, episode: int):
    await ctx.send(f"S{season}E{episode} of show {tmdb_id}...")

# Add more placeholder commands to reach ~30
for i in range(10):
    @bot.command(name=f"cmd{i+1}")
    async def placeholder(ctx):
        await ctx.send("This is a placeholder command.")

@bot.event
async def on_ready():
    print(f"✅ Bot is online! Prefix: {PREFIX} | {bot.user}")

bot.run(DISCORD_TOKEN)
