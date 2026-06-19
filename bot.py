import discord
import re
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# ----------------------------
# Conversion constants
# ----------------------------

KM_TO_MILES = 0.621371

M_TO_FT = 3.28084
M_TO_YD = 1.09361

CM_TO_INCH = 0.393701

KG_TO_LB = 2.20462
KG_TO_STONE = 0.157473

G_TO_OZ = 0.035274


# ----------------------------
# Helpers
# ----------------------------

def fmt(n):
    return f"{n:.2f}"


def cm_to_feet_inches(cm):
    inches_total = cm / 2.54
    feet = int(inches_total // 12)
    inches = round(inches_total % 12)

    if inches == 12:
        feet += 1
        inches = 0

    return feet, inches


# ----------------------------
# Bot start
# ----------------------------

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


# ----------------------------
# Message handler
# ----------------------------

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower().strip()

    # ---------------- km → miles ----------------
    km = re.match(r"^(\d+(\.\d+)?)\s*(km|kilometre|kilometer|kilometres|kilometers)\b", content)
    if km:
        value = float(km.group(1))
        miles = value * KM_TO_MILES
        await message.channel.send(f"{fmt(value)} km = {fmt(miles)} miles")
        return

    # ---------------- metres → feet + yards ----------------
    m = re.match(r"^(\d+(\.\d+)?)\s*(metre|meter|metres|meters|m)\b(?!m)", content)
    if m:
        value = float(m.group(1))
        ft = value * M_TO_FT
        yd = value * M_TO_YD
        await message.channel.send(f"{fmt(value)} m = {fmt(ft)} ft / {fmt(yd)} yd")
        return

    # ---------------- cm → feet & inches ----------------
    cm = re.match(r"^(\d+(\.\d+)?)\s*(cm|centimetre|centimeter|centimetres|centimeters)\b", content)
    if cm:
        value = float(cm.group(1))
        feet, inches = cm_to_feet_inches(value)
        await message.channel.send(f"{int(value)} cm = {feet}'{inches}\"")
        return

    # ---------------- feet → metres ----------------
    ft = re.match(r"^(\d+(\.\d+)?)\s*(ft|foot|feet)\b", content)
    if ft:
        value = float(ft.group(1))
        metres = value / M_TO_FT
        await message.channel.send(f"{fmt(value)} ft = {fmt(metres)} m")
        return

    # ---------------- yards → metres ----------------
    yd = re.match(r"^(\d+(\.\d+)?)\s*(yd|yard|yards)\b", content)
    if yd:
        value = float(yd.group(1))
        metres = value / M_TO_YD
        await message.channel.send(f"{fmt(value)} yd = {fmt(metres)} m")
        return

    # ---------------- kg → lb + stone ----------------
    kg = re.match(r"^(\d+(\.\d+)?)\s*(kg|kilogram|kilograms)\b", content)
    if kg:
        value = float(kg.group(1))
        lb = value * KG_TO_LB
        stone_total = value * KG_TO_STONE
        stones = int(stone_total)
        pounds = (stone_total - stones) * 14

        await message.channel.send(
            f"{fmt(value)} kg = {fmt(lb)} lb ({stones} st {fmt(pounds)} lb)"
        )
        return

    # ---------------- grams → ounces ----------------
    g = re.match(r"^(\d+(\.\d+)?)\s*(g|gram|grams)\b", content)
    if g:
        value = float(g.group(1))
        oz = value * G_TO_OZ
        await message.channel.send(f"{fmt(value)} g = {fmt(oz)} oz")
        return


# ----------------------------
# RUN BOT
# ----------------------------

client.run(os.getenv("DISCORD_TOKEN"))
