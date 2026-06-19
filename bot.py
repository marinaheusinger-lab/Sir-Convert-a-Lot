import discord
import re
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# ----------------------------
# Helpers
# ----------------------------

def fmt(n):
    return f"{n:.2f}"


# ----------------------------
# UNIT DEFINITIONS
# ----------------------------

UNIT_PATTERNS = {
    "mm": ["mm", "millimetre", "millimeter", "millimetres", "millimeters"],
    "cm": ["cm", "centimetre", "centimeter", "centimetres", "centimeters"],
    "m": ["m", "metre", "meter", "metres", "meters"],
    "km": ["km", "kilometre", "kilometer", "kilometres", "kilometers"],

    "ug": ["µg", "ug", "microgram", "micrograms"],
    "mg": ["mg", "milligram", "milligrams"],
    "g": ["g", "gram", "grams"],
    "kg": ["kg", "kilogram", "kilograms"],
    "t": ["t", "tonne", "tonnes"],

    "ml": ["ml", "millilitre", "milliliter", "millilitres", "milliliters"],
    "l": ["l", "litre", "liter", "litres", "liters"]
}


# ----------------------------
# FIND UNIT
# ----------------------------

def find_unit(text):
    for key, variants in UNIT_PATTERNS.items():
        for v in variants:
            pattern = rf"(\d+(\.\d+)?)\s*{re.escape(v)}\b"
            match = re.search(pattern, text)
            if match:
                return key, float(match.group(1))
    return None, None


# ----------------------------
# LENGTH (UK ONLY)
# ----------------------------

def convert_length(unit, value):
    meters = value * {
        "mm": 0.001,
        "cm": 0.01,
        "m": 1,
        "km": 1000
    }[unit]

    feet_total = meters * 3.28084
    yards = meters / 0.9144

    feet = int(feet_total)
    inches = round((feet_total - feet) * 12)

    if inches == 12:
        feet += 1
        inches = 0

    if unit == "km":
        miles = meters / 1609.344
        return f"{fmt(value)} km = {fmt(miles)} miles"

    return f"{fmt(value)} {unit} = {feet} ft {inches} in / {fmt(yards)} yd"


# ----------------------------
# MASS (UK ONLY)
# ----------------------------

def convert_mass(unit, value):
    grams = value * {
        "ug": 0.000001,
        "mg": 0.001,
        "g": 1,
        "kg": 1000,
        "t": 1_000_000
    }[unit]

    kg = grams / 1000
    pounds_total = kg * 2.20462

    stone = int(pounds_total // 14)
    pounds = round(pounds_total % 14, 1)

    return f"{fmt(value)} {unit} = {stone} st {fmt(pounds)} lb"


# ----------------------------
# VOLUME (UK ONLY)
# ----------------------------

def convert_volume(unit, value):
    liters = value * {
        "ml": 0.001,
        "l": 1
    }[unit]

    uk_gallons = liters / 4.54609

    return f"{fmt(value)} {unit} = {fmt(uk_gallons)} UK gal"


# ----------------------------
# BOT
# ----------------------------

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower()

    unit, value = find_unit(content)
    if not unit:
        return  # 🚨 SILENT if nothing to convert

    # LENGTH
    if unit in ["mm", "cm", "m", "km"]:
        await message.channel.send(convert_length(unit, value))
        return

    # MASS
    if unit in ["ug", "mg", "g", "kg", "t"]:
        await message.channel.send(convert_mass(unit, value))
        return

    # VOLUME
    if unit in ["ml", "l"]:
        await message.channel.send(convert_volume(unit, value))
        return


client.run(os.getenv("DISCORD_TOKEN"))
