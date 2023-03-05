import discord
import socket
from discord.ext import commands
from config import secrets
import json
import asyncio

intent = discord.Intents.default()
intent.message_content = True
client = discord.Client(intents=intent)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    client.loop.create_task(sock_server())
  
@client.event
async def sock_server () :
    server = await asyncio.start_server(connection_handler, "127.0.0.1", 54296)
    async with server :
        await server.serve_forever()
    
        
        
async def connection_handler (r: asyncio.StreamReader, w: asyncio.StreamWriter) :
    req = (await r.read(255)).decode('utf8')
    guilty_only = True
    if (req[0] == '*') :
        req = req[1:]
        guilty_only = False
    c = client.get_channel(740699832204656725)
    while True :
        await c.send ("tb>reports on " + req + (" filter:GV here" if guilty_only else " here"))
        message = await client.wait_for("message", timeout=15)
        if message.author.id == 386120229694078977 :
            reports = message.embeds[0].to_dict()
            reports = reports['description']
            reports = reports.split('\n')
            reportsf = []
            reportsg = []
            for item in reports :
                print (item)
                if "Error fetching user reports" in item or 'There are no reports to display' in item:
                    continue
                reportsf.append(item.split('>')[1])
            for item in reportsf :
                reportsg.append(item.split(" '")[0]+")")
            w.write(json.dumps(reportsg).encode())
            w.write(b"\26")
            return


client.run(secrets.token)
