import discord
from discord.ext import commands
import json
from discord import app_commands


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


DATA_FILES = {
    "5e": {
        "spells": "json_files/5e_spells.json",
        "features": "json_files/5e_features.json",
    },
    "5e2024": {
        "spells": "json_files/5e_2024_spells.json",
        "features": "json_files/5e_2024_features.json",
    },
}

CONTENT_DATA = {
    edition: {
        content_type: load_json(path)
        for content_type, path in files.items()
    }
    for edition, files in DATA_FILES.items()
}

class Find(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="find", description="Find D&D content")
    @app_commands.describe(
        edition="Game edition (e.g., 5e , 5e2024",
        type="Type of content (e.g., spell, feture)",
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

            if edition != "5e" and edition != "5e2024":
                await interaction.response.send_message(
                    f"Edition '{edition}' not supported yet."
                )
                return

            if type != "spell" and type != "feature":
                await interaction.response.send_message(
                    f"Type '{type}' not supported yet."
                )
                return
            
            spells = CONTENT_DATA[edition]["spells"]
            features = CONTENT_DATA[edition]["features"]

            spell_names = [spell["name"].lower() for spell in spells]
            feature_names = [feature["name"].lower() for feature in features]


            match type:
                case "spell":
                    if name not in spell_names:
                        await interaction.response.send_message(
                            f"Spell '{name}' not found in 5e edition!"
                        )
                        return

                    spell = spells[spell_names.index(name)]

                    ritual = " (ritual)" if spell.get("ritual") else ""
                    concentration = "Concentration, " if spell.get("concentration") else ""

                    found = f"""Name: {spell['name']}
Level {spell['level']} {spell['school']}{ritual}
Casting Time: {spell['actionType']}
Range: {spell['range']}
Components: {', '.join(spell['components'])}
Materials: {spell.get('material', 'None')}
Duration: {concentration}{spell['duration']}

Description: {spell['description']}

Spell Lists: {', '.join(spell['classes'])}
                                """

                    await interaction.response.send_message(found)

                case "feature":
                    if name not in feature_names:
                        await interaction.response.send_message(
                            f"Feature '{name}' not found in 5e edition!"
                        )
                        return
                    feature = features[feature_names.index(name)]
                    found = f"""
Name: {feature['name']}
Description: {feature['description']}
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