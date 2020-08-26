import discord
from discord.ext import commands
import config
import json
import asyncio

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    client.loop.create_task(check_report_file())
    
@client.event
async def check_report_file() :
    c = client.get_channel(740699832204656725)
    while True :
        with open ("reportsqueue.txt", 'r') as q :
            checks = q.read()
        if len(checks) > 0 :
            with open ("reportsqueue.txt", 'w') as q :
                q.write('')
            await c.send ("tb>reports on " + checks + " filter:GV here")
        await asyncio.sleep(5)
            
        
        

        
@client.event
async def on_message(message):
    print (message.content, '##', message.author.display_name)
    if message.author.id == 386120229694078977 :
        reports = message.embeds[0].to_dict()
        reports = reports['description']
        reports = reports.split('\n')
        reportsf = []
        reportsg = []
        for item in reports :
            reportsf.append(item.split('>')[1])
        for item in reportsf :
            reportsg.append(item.split(" '")[0]+")")
        with open ("reports.json",'w') as r :
            json.dump(reportsg, r)
        




client.run(config.token)
