import discord
from discord.ext import commands
import json
from discord import app_commands

with open("json_files/5e_spells.json", "r") as f:
    spells_data = json.load(f)


class Find(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="find", description="Find D&D content")
    @app_commands.describe(
        edition="Game edition (e.g., 5e)",
        type="Type of content (e.g., spell)",
        name="Name of the content to find"
    )
    async def find(
        self,
        interaction: discord.Interaction,
        edition: str,
        type: str,
        name: str
    ):

        try:
            edition = edition.lower()
            type = type.lower()
            name = name.lower()

            if edition != "5e":
                await interaction.response.send_message(
                    f"Edition '{edition}' not supported yet."
                )
                return

            if type != "spell":
                await interaction.response.send_message(
                    f"Type '{type}' not supported yet."
                )
                return

            spell_names = [spell["name"].lower() for spell in spells_data]

            if name not in spell_names:
                await interaction.response.send_message(
                    f"Spell '{name}' not found in 5e edition!"
                )
                return

            spell = spells_data[spell_names.index(name)]

            ritual = " (ritual)" if spell.get("ritual") else ""
            concentration = "Concentration, " if spell.get("concentration") else ""

            found = f"""
Name: {spell['name']}
Level {spell['level']} {spell['school']}{ritual}
Casting Time: {spell['actionType']}
Range: {spell['range']}
Components: {', '.join(spell['components'])}
Materials: {spell.get('material', 'None')}
Duration: {concentration}{spell['duration']}

Description: 
{spell['description']}

Spell Lists: {', '.join(spell['classes'])}
"""

            await interaction.response.send_message(found)

        except Exception as e:
            print("ERROR:", e)
            await interaction.response.send_message(
                "Something went wrong.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Find(bot))