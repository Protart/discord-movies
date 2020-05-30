import discord
import requests as r
import os
import srt
import pause
import datetime
from math import *
import asyncio


token = os.environ['DISCORDMOVIES']

f_dir = "movie_subtitles"


def save(request, filename):
    if not os.path.isdir(f_dir):
        os.mkdir(f_dir)

    with open(os.path.join(f_dir, filename), "wb") as f:
        f.write(request.content)

def get_all_movies():
    return [
        {
            "movie": x["movie"],
            "subs": f"https://movies-get.herokuapp.com/api/get-subtitles/?s={x['id']}",
        }
        for x in r.post(
            "https://movies-get.herokuapp.com/api/get-all/", json={}
        ).json()["movies"]
    ]

the_movies = get_all_movies()

def search(s):
    return r.post('https://movies-get.herokuapp.com/api/data/search/',data={'q':s}).json()


def get_subs(movie):
    path = os.path.join(f_dir, movie)
    x = open(path, 'r').read()
    subs = list(srt.parse(x))

    return subs

client = discord.Client()

@client.event
async def on_ready():
    print(f'we have logged in as {client.user}')

play = False
@client.event
async def on_message(message):
    global play
    print(f'{message.channel}:{message.author}:{message.author.name}:{message.content}')
    commands = message.content.split()
    if message.content=='ping!':
        await message.channel.send('pong!')

    if commands[0] == 'search!':
        movies = search(' '.join(commands[1:]))
        print(movies)
        if movies == {'no-res': True}:
            await message.channel.send("I couldn't find any movies :(")

        else:
            for i in movies['movies'][:5]:
                embed = discord.Embed(title= i['movie'], colour=discord.Colour.teal())
                embed.set_thumbnail(url= i['thumb'])
                await message.channel.send(embed=embed)
        
    if commands[0] == 'play!':
        print(' '.join(commands[1:]))
        for i in the_movies:
            if i['movie'] == ' '.join(commands[1:]):
                save(r.get(i['subs']),i['movie'])

        
        await message.channel.send(f"NOW PLAYING: {' '.join(commands[1:])}")

        subs = get_subs(' '.join(commands[1:]))
        start_ = datetime.datetime.now()
        play = True
        for i in range(len(subs)):
            if play:
                await message.channel.send(subs[i].content)
                asyncio.sleep((subs[i + 1].start - subs[i].start).total_seconds()+ 0.5)
            else:
                break

    if commands[0] == 'stop!':
        play = False
        await message.channel.send('stopped')

client.run(token)