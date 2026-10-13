import random
import discord
from discord.ext import commands
from discord import app_commands

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Roll dice")
    @app_commands.describe(dice="Format: XdY (example: 2d6) or /roll character for character stats.")
    async def roll(self, interaction: discord.Interaction, dice: str):

        try:
            if dice.lower() == "character":
                if dice.lower() == "character":
                    stats = []
                    for _ in range(6):
                            rolls = sorted(random.randint(1, 6) for _ in range(4))
                            stats.append(sum(rolls[1:]))  # drop the lowest

                    await interaction.response.send_message(
                        f"🎲 Your Character Stats:\n{stats}\n")
                    return
        except:
            pass

        try: 
            amount, sides = dice.lower().split("d")
            amount = int(amount)
            sides = int(sides)

            if amount > 50:
                await interaction.response.send_message(
                    "You can't roll more than 50 dice at once!",
                    ephemeral=True
                )
                return

            rolls = [random.randint(1, sides) for _ in range(amount)]
            total = sum(rolls)

            await interaction.response.send_message(
                f"🎲 Rolled {dice}:\n"
                f"Rolls: {rolls}\n"
                f"Total: {total}"
            )

        except ValueError:
            await interaction.response.send_message(
                "Invalid format! Use XdY (example: 2d6)",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Roll(bot))