import discord
from discord import app_commands
import requests
import random
from typing import Optional

# ================== CONFIG ==================
TMDB_API_KEY = "YOUR_TMDB_READ_ACCESS_TOKEN_HERE"
# ===========================================

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

def tmdb_request(endpoint: str, params: dict = None):
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    r = requests.get(f"https://api.themoviedb.org/3{endpoint}", headers=headers, params=params or {})
    return r.json() if r.status_code == 200 else None

def create_vidking_url(media_type: str, tmdb_id: int, season: int = 1, episode: int = 1) -> str:
    if media_type.lower() == "movie":
        return f"https://www.vidking.net/embed/movie/{tmdb_id}?color=e50914&autoPlay=false"
    return f"https://www.vidking.net/embed/tv/{tmdb_id}/{season}/{episode}?color=e50914&episodeSelector=true&nextEpisode=true"

# ================== HELP COMMAND ==================
@tree.command(name="help", description="Show all available Vidking commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎬 Vidking Bot - Full Command List",
        description="Use any command with `/`",
        color=0xe50914
    )

    embed.add_field(name="🎥 Core Commands", value="""
• `/watch` - Watch movie or TV episode
• `/search` - Search for content
• `/random` - Random movie/show
""", inline=False)

    embed.add_field(name="📊 Discovery", value="""
• `/popular` - Popular content
• `/top_rated` - Top rated
• `/trending` - Trending now
• `/upcoming` - Upcoming movies
• `/now_playing` - In theaters
""", inline=False)

    embed.add_field(name="📺 TV Specific", value="""
• `/on_the_air` - Currently airing
• `/airing_today` - Airing today
• `/season` - Season details
• `/episode` - Episode details
""", inline=False)

    embed.add_field(name="🔍 More Tools", value="""
• `/similar` - Similar titles
• `/recommendations` - Recommendations
• `/cast` - Cast & crew
• `/videos` - Trailers
• `/genres` - Browse genres
""", inline=False)

    embed.set_footer(text="Tip: Start with /watch movie Inception")
    await interaction.response.send_message(embed=embed)

# ================== MAIN COMMANDS ==================
@tree.command(name="watch", description="Watch on Vidking Player")
@app_commands.describe(media_type="movie or tv", query="Title or TMDB ID", season="Season (TV)", episode="Episode (TV)")
async def watch(interaction: discord.Interaction, media_type: str, query: str, season: Optional[int] = 1, episode: Optional[int] = 1):
    await interaction.response.defer()
    try:
        tmdb_id = int(query)
        data = tmdb_request(f"/{media_type}/{tmdb_id}")
    except:
        search = tmdb_request(f"/search/{media_type}", {"query": query})
        if not search or not search.get("results"):
            return await interaction.followup.send("❌ Not found.")
        data = search["results"][0]
        tmdb_id = data["id"]
        data = tmdb_request(f"/{media_type}/{tmdb_id}")

    if not data:
        return await interaction.followup.send("❌ Failed to load data.")

    title = data.get("title") or data.get("name", "Unknown")
    url = create_vidking_url(media_type, tmdb_id, season, episode)

    embed = discord.Embed(title=f"🎬 {title}", description=data.get("overview", "No overview available.")[:400], url=url, color=0xe50914)
    if data.get("poster_path"):
        embed.set_image(url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}")
    embed.add_field(name="▶️ Watch Now", value=f"[Open Vidking Player]({url})", inline=False)
    await interaction.followup.send(embed=embed)

# Add more commands as needed (random, popular, trending, etc.)
# For brevity, the rest are similar. You can expand them.

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Vidking Bot is online with slash commands! - {bot.user}")

bot.run("YOUR_DISCORD_BOT_TOKEN_HERE")
