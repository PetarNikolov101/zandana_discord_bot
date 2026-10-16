import os, io, json, aiohttp, discord
from pathlib import Path
from discord.ext import commands, tasks

BASE_DIR = Path(__file__).resolve().parent.parent
LAST_SEEN_FILE = BASE_DIR / "json_files" / "ig_last_seen.json"
CHANNEL_ID = int(os.getenv("ANNOUNCEMENT_CHANNEL_ID"))
FIELDS = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,children{id,media_type,media_url,thumbnail_url}"

class FetchPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_seen = self.load_last_seen()

    # ---------- state ----------
    def load_last_seen(self):
        if LAST_SEEN_FILE.exists():
            with open(LAST_SEEN_FILE, "r") as f:
                return json.load(f).get("id")
        return None

    def save_last_seen(self, post_id):
        self.last_seen = post_id
        with open(LAST_SEEN_FILE, "w") as f:
            json.dump({"id": post_id}, f)

    async def cog_load(self):
        self.check_posts.start()

    async def cog_unload(self):
        self.check_posts.cancel()

    # ---------- instagram ----------
    async def get_posts(self):
        token = self.bot.get_cog("RefreshToken").ig["token"]  # always the latest
        params = {"fields": FIELDS, "limit": 10, "access_token": token}
        async with aiohttp.ClientSession() as session:
            async with session.get("https://graph.instagram.com/me/media", params=params) as r:
                if r.status != 200:
                    print("Instagram fetch failed:", r.status, await r.text())
                    return []
                return (await r.json()).get("data", [])

    async def download(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    return None
                return await r.read()

    # ---------- discord ----------
    async def announce(self, post):
        channel = self.bot.get_channel(CHANNEL_ID) or await self.bot.fetch_channel(CHANNEL_ID)
        caption = post.get("caption", "")
        link = post["permalink"]
        limit = channel.guild.filesize_limit
        mentions = discord.AllowedMentions(everyone=True)

        if post["media_type"] == "VIDEO":
            data = await self.download(post["media_url"]) if post.get("media_url") else None
            if data and len(data) <= limit:
                await channel.send(
                    f"@everyone\n{caption[:1700]}\n{link}",
                    file=discord.File(io.BytesIO(data), "post.mp4"),
                    allowed_mentions=mentions,
                )
                return
            # too big or download failed: cover image + link
            embed = discord.Embed(title="New Instagram video", url=link, description=caption[:4000])
            if post.get("thumbnail_url"):
                embed.set_image(url=post["thumbnail_url"])
            await channel.send("@everyone", embed=embed, allowed_mentions=mentions)
            return

        if post["media_type"] == "CAROUSEL_ALBUM":
            files, skipped, total = [], 0, 0
            for i, child in enumerate(post.get("children", {}).get("data", [])[:10]):
                url = child.get("media_url")
                data = await self.download(url) if url else None
                if not data or total + len(data) > limit:
                    skipped += 1
                    continue
                total += len(data)
                ext = "mp4" if child["media_type"] == "VIDEO" else "jpg"
                files.append(discord.File(io.BytesIO(data), f"item{i + 1}.{ext}"))

            text = f"@everyone\n{caption[:1650]}\n{link}"
            if skipped:
                text += f"\n({skipped} item(s) too large to upload, see the post)"
            await channel.send(text, files=files, allowed_mentions=mentions)
            return

        # IMAGE
        embed = discord.Embed(title="New Instagram post", url=link, description=caption[:4000])
        data = await self.download(post["media_url"]) if post.get("media_url") else None
        if data and len(data) <= limit:
            embed.set_image(url="attachment://post.jpg")
            await channel.send("@everyone", embed=embed,
                               file=discord.File(io.BytesIO(data), "post.jpg"),
                               allowed_mentions=mentions)
        else:
            await channel.send("@everyone", embed=embed, allowed_mentions=mentions)

    # ---------- loop ----------
    @tasks.loop(minutes=2)
    async def check_posts(self):
        posts = await self.get_posts()  # newest first
        if not posts:
            return

        if self.last_seen is None:  # first run: remember, don't announce old posts
            self.save_last_seen(posts[0]["id"])
            return

        ids = [p["id"] for p in posts]
        if self.last_seen in ids:
            new = posts[:ids.index(self.last_seen)]
        else:
            new = posts[:1]  # last seen post was deleted: only announce the newest

        for post in reversed(new):  # oldest first
            try:
                await self.announce(post)
            except Exception as e:
                print("Announce failed for", post["id"], e)
                break  # don't mark it as seen, retry next cycle
            self.save_last_seen(post["id"])

    @check_posts.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(FetchPost(bot))
