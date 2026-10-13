import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):

        # Find the channel by name
        channel = discord.utils.get(member.guild.text_channels, name="🐣-introduce-yourself")

        if channel:
            await channel.send(
                f"Добредојде во Занданата, {member.mention}! 🎉\n"
                f"Претстави се во овој канал, авантуристу!"
            )

async def setup(bot):
    await bot.add_cog(Welcome(bot))