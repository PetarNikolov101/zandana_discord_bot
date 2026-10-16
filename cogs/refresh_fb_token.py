import os, json, time, aiohttp
from pathlib import Path
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent  # cogs/ -> project folder
TOKEN_FILE = BASE_DIR / "json_files" / "ig_token.json"
REFRESH_AFTER_DAYS = 30
USERID = int(os.getenv("DISCORDUSERID"))


class RefreshToken(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ig = self.load_token()
        self.save_token()

    def load_token(self):
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, "r") as f:
                return json.load(f)
        # first run: seed from .env
        return {"token": os.getenv("IG_TOKEN"), "refreshed_at": time.time()}

    def save_token(self):
        with open(TOKEN_FILE, "w") as f:
            json.dump(self.ig, f)

    async def cog_load(self):
        self.refresh_token.start()

    async def cog_unload(self):
        self.refresh_token.cancel()

    @tasks.loop(hours=24)
    async def refresh_token(self):
        age_days = (time.time() - self.ig["refreshed_at"]) / 86400
        if age_days < REFRESH_AFTER_DAYS:
            return

        params = {"grant_type": "ig_refresh_token", "access_token": self.ig["token"]}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://graph.instagram.com/refresh_access_token", params=params
            ) as r:
                data = await r.json()

        if "access_token" in data:
            self.ig["token"] = data["access_token"]
            self.ig["refreshed_at"] = time.time()
            self.save_token()
            print("Instagram token refreshed.")
        else:
            print("Token refresh FAILED:", data)
            owner = await self.bot.fetch_user(USERID)
            await owner.send("Instagram token refresh failed. Check the bot console.")


async def setup(bot):
    await bot.add_cog(RefreshToken(bot))