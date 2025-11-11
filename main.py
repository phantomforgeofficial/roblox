from discord.ext import commands
import discord, requests, random, threading, asyncio
import os

# Haal de bot token op uit een omgevingsvariabele
TOKEN = os.getenv('DISCORD_TOKEN')

# Controleer of de token is ingesteld
if TOKEN is None:
    print("Fout: DISCORD_TOKEN omgevingsvariabele is niet ingesteld. Zorg ervoor dat deze op Render.com is geconfigureerd.")
    exit(1)

# Lees cookies uit het bestand
try:
    with open('cookies.txt', 'r') as cookies_file:
        cookies1 = cookies_file.read().splitlines()
    if not cookies1:
        print("Waarschuwing: 'cookies.txt' is leeg. Sommige functies werken mogelijk niet.")
except FileNotFoundError:
    print("Fout: 'cookies.txt' niet gevonden. Zorg ervoor dat het bestand in de root van je repository staat.")
    cookies1 = []
except Exception as e:
    print(f"Fout bij het lezen van 'cookies.txt': {e}")
    cookies1 = []

bot = commands.Bot(command_prefix='.?')

@bot.event
async def on_ready():
    print(f'Bot is online als {bot.user.name}!')

def follow_user(cookie, prox, userid):
    with requests.session() as session:
        try:
            proxy = {'http': prox, 'https': prox}
            session.cookies['.ROBLOSECURITY'] = cookie
            response = session.get('https://www.roblox.com/home', proxies=proxy, timeout=10)
            response.raise_for_status()
            csrf_token = response.content.decode('utf8').split("Roblox.XsrfToken.setToken('")[1].split("');")[0]
            session.headers['x-csrf-token'] = csrf_token
            follow_response = session.post(f'https://friends.roblox.com/v1/users/{userid}/follow', proxies=proxy, timeout=10)
            follow_response.raise_for_status()
            print(f"Volgactie succesvol voor cookie: {cookie[:10]}... en gebruiker {userid}")
        except requests.exceptions.RequestException as e:
            print(f"Fout bij follow_user voor cookie {cookie[:10]}...: {e}")
        except IndexError:
            print(f"IndexError: CSRF-token niet gevonden voor cookie {cookie[:10]}...")
        except Exception as e:
            print(f"Onverwachte fout in follow_user voor cookie {cookie[:10]}...: {e}")

def add_user(cookie, userid):
    with requests.session() as session:
        try:
            session.cookies['.ROBLOSECURITY'] = cookie
            response = session.get('https://www.roblox.com/home', timeout=10)
            response.raise_for_status()
            csrf_token = response.content.decode('utf8').split("Roblox.XsrfToken.setToken('")[1].split("');")[0]
            session.headers['x-csrf-token'] = csrf_token
            add_response = session.post(f'https://friends.roblox.com/v1/users/{userid}/request-friendship', timeout=10)
            add_response.raise_for_status()
            print(f"Vriendschapsverzoek succesvol voor cookie: {cookie[:10]}... en gebruiker {userid}")
        except requests.exceptions.RequestException as e:
            print(f"Fout bij add_user voor cookie {cookie[:10]}...: {e}")
        except IndexError:
            print(f"IndexError: CSRF-token niet gevonden voor cookie {cookie[:10]}...")
        except Exception as e:
            print(f"Onverwachte fout in add_user voor cookie {cookie[:10]}...: {e}")

@bot.command()
async def follow(ctx, userId: int):
    await ctx.send(f'<@{ctx.author.id}>, we hebben de follow bot gestart!')
    prox = ""
    try:
        response = requests.get('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=150000&country=all&ssl=all&anonymity=all', stream=True, timeout=15)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=10000):
            if chunk:
                prox += chunk.decode()
        proxies = prox.splitlines()
        if not proxies:
            await ctx.send("Geen proxies gevonden. Kan de follow-actie niet uitvoeren.")
            return
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Fout bij het ophalen van proxies: {e}")
        return
    if not cookies1:
        await ctx.send("Geen cookies geladen. Kan de follow-actie niet uitvoeren.")
        return
    for cookie in cookies1:
        threading.Thread(target=follow_user, args=(cookie, random.choice(proxies), userId)).start()
        await asyncio.sleep(0.01)

@bot.command()
async def friends(ctx, userId: int):
    await ctx.send(f'<@{ctx.author.id}>, we hebben de friend bot gestart!')
    if not cookies1:
        await ctx.send("Geen cookies geladen. Kan de friend-actie niet uitvoeren.")
        return
    for cookie in cookies1:
        threading.Thread(target=add_user, args=(cookie, userId)).start()
        await asyncio.sleep(0.01)

@bot.command()
async def cookies(ctx):
    await ctx.send(f'Er zijn momenteel **{len(cookies1)}** cookies in onze server!')

bot.run(TOKEN)
