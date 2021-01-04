from keep_alive import keep_alive
import discord
from collections import defaultdict
import os
import asyncio
from classes import ResourceEncounter,AnimalEncounter, Food
import queue
import helper
import requests
import json

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

# ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

client = discord.Client()

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user: return
#  if (!message.content.startsWith("}") return; this saves runtime but we would sacrafice or meme commands like ): and :sunglasses:

  ###########################################
  #                   Help                  #
  ###########################################
  if message.content.startswith("}help"):
    helpMessage = discord.Embed(title=":hot_face: **Main Commands**:")
    helpMessage.add_field(name="}minecraft", value="Minecraft, but not really", inline=False)
    helpMessage.add_field(name="}ttt <@mention>", value="Tic-Tac-Toe, challenge a friend!", inline=False)
    helpMessage.add_field(name="}coinflip", value="coinflip, test your odds", inline=False)
    helpMessage.add_field(name="}dog", value="displays an image of a dog... sometimes", inline=False)
    helpMessage.add_field(name="}play <video>", value="search youtube for video", inline=False)
    helpMessage.add_field(name="}skip", value="skip current video", inline=False)
    helpMessage.add_field(name="}stop", value="stop current video", inline=False)
    helpMessage.add_field(name="}leave", value="make BotCato leave ):", inline=False)


    await message.channel.send(embed=helpMessage)

  ###########################################
  #               Minecraft                 #
  ###########################################
  if message.content.startswith("}minecraft") or message.content.startswith("}mc"):
    # TODO: check for edge case where user emotes manually 
    def inventoryToEmoji(inv: dict) -> str:
      """ k value must be named after discord emoji """
      result = ""
      for k,v in inv.items():
          result += ":" + k + ":" + helper.numToEmoji(v)
      return result
    # Food
    meat = Food("cut_of_meat","🥩",1)
    cookedMeat = Food("meat_on_bone","🍖",3)
    foods = [meat, cookedMeat]
    foodemojis = [i.emoji for i in foods]
    
    # Animal Encounters
    man = ResourceEncounter(":man_running:")
    pig = AnimalEncounter(":pig2:")
    cow = AnimalEncounter(":cow2:")
    rabbit = AnimalEncounter(":rabbit2:")
    goat = AnimalEncounter(":goat:")

    # Resources Encounters
    tree = ResourceEncounter(":evergreen_tree:","🪓","wood",[5,6,7,8],[1/4,1/4,1/4,1/4])
    rock = ResourceEncounter(":mountain:","⛏","mountain",[1],[1])
    cactus = ResourceEncounter(":cactus:","🪓","cactus",[1,2,3],[1/3,1/3,1/3])

    # Enviroment Encounters
    bluesquare = ResourceEncounter(":blue_square:")
    greensquare = ResourceEncounter(":green_square:")

    # All Encounters
    encounters = [bluesquare,pig,tree,rock,cow] # Forest/Plain Biome
    desertEncounters = [bluesquare,rock,cactus,rabbit]
    snowEncounters = [bluesquare,rock,tree,goat] 
    encountersprob = [0.6,0.1,0.1,0.1,0.1]

    # Initialize Playing Field
    playField = [[bluesquare for x in range(11)]] + [[helper.blockDistributer(encounters, encountersprob) for x in range(11)]] + [[greensquare for x in range(11)]]
    playField[1][10] = man

    # Initialize Player Statistics
    health = [":heart: "] + [":red_square:" for x in range(10)]
    hunger = [":meat_on_bone: "]+ [":brown_square:" for x in range(10)]
    inventory = defaultdict(int)
    steps = 0
    actions = ["⬅","🔪","🪓","⛏","🥩","🍖","🔥"]

    def moveCheck(payload):
      return str(payload.emoji) in actions and payload.message_id == grassMSG.id and payload.user_id != grassMSG.author.id
    
    def moveCheck2(payload):
      return str(payload.emoji) in ["⬅","🥩","🍖","🔥"] and payload.message_id == grassMSG.id

    # Sends PlayField as bot messages
    await message.channel.send("".join(i.name for i in playField[0]))
    playerMSG = await message.channel.send("".join(i.name for i in playField[1]))
    grassMSG = await message.channel.send("".join(i.name for i in playField[2]))
    healthMSG = await message.channel.send("".join(health))
    hungerMSG = await message.channel.send("".join(hunger))
    inventoryMSG = await message.channel.send("឵឵឵" + "".join(inventoryToEmoji(inventory)))
  
    await grassMSG.add_reaction("⬅")
    while(len(health) > 1):
      if playField[1][9] != bluesquare:
        await grassMSG.add_reaction(playField[1][9].action)
      for food in foods:
        try:
          if inventory.get(food.name) > 0 and len(hunger) < 11:
            await grassMSG.add_reaction(food.emoji)
        except:
          pass
      try:
        if inventory.get("wood") > 1 and inventory.get("mountain") > 0 and inventory.get("cut_of_meat") > 0:
          await grassMSG.add_reaction("🔥")
      except:
        pass
      if len(hunger) == 11:
            await grassMSG.clear_reaction(food.emoji)
      # Wait for User Input via Discord Reaction
      pending_tasks = [client.wait_for('raw_reaction_add',check=moveCheck), client.wait_for('raw_reaction_remove',check=moveCheck2)]
      done_tasks, pending_tasks = await asyncio.wait(pending_tasks,return_when=asyncio.FIRST_COMPLETED)
      for task in done_tasks: payload = await task
      reaction = str(payload.emoji)

      if playField[1][9] != bluesquare:
        await grassMSG.clear_reaction(playField[1][9].action)

      # Player Encounter Actions
      if reaction not in ["⬅"]:
        if reaction in foodemojis:
          chosenFood = foods[foodemojis.index(reaction)]
          try:
            if inventory.get(chosenFood.name) > 0 and len(hunger) < 11:
              for i in range(chosenFood.fill):
                hunger.append(":brown_square:")
              await hungerMSG.edit(content = "".join(hunger))
              inventory[chosenFood.name] -= 1
            if inventory.get(chosenFood.name) == 0:
              await grassMSG.clear_reaction(reaction)
              inventory.pop(chosenFood.name)
          except:
            pass
        elif reaction == "🔥":
          try:
            if inventory.get("wood") > 1 and inventory.get("mountain") > 0 and inventory.get("cut_of_meat") > 0:
              inventory["meat_on_bone"] += 1
              inventory["wood"] -= 1
              inventory["mountain"] -= 1
              inventory["cut_of_meat"] -= 1
              for i in ["wood","mountain","cut_of_meat"]:
                if inventory.get(i) == 0:
                  await grassMSG.clear_reaction("🔥")
                  if i == "cut_of_meat":
                    await grassMSG.clear_reaction("🥩")
                  inventory.pop(i)
          except:
            pass
        else:
          if len(hunger) > 1:
            hunger.pop()
            await hungerMSG.edit(content = "".join(hunger))
          drops = helper.blockDistributer(playField[1][9].dropamount,playField[1][9].droprates)
          inventory[playField[1][9].drop] += drops
          playField[1][9] = bluesquare
        await inventoryMSG.edit(content = "឵឵឵" + "".join(inventoryToEmoji(inventory)))

      # Player Move Left
      if reaction == "⬅":
        steps += 1
        for i in reversed(range(9)):
          playField[1][i+1] = playField[1][i]
        if steps % 5 == 0:
          if len(hunger) > 1:
            hunger.pop()
            await hungerMSG.edit(content = "".join(hunger))
        if len(hunger) == 1:
          if steps % 2 == 0:
            if len(health) > 1:
              health.pop()
              await healthMSG.edit(content = "".join(health))
        playField[1][0] = helper.blockDistributer(encounters, encountersprob)
      await playerMSG.edit(content = "".join(i.name for i in playField[1]))
    
    # Player Death
    death = ResourceEncounter(":headstone:")
    playerMSG = await message.channel.send("".join(i.name for i in playField[1]))
    playField[1][10] = death
      
  ###########################################
  #                  Music                  #
  ###########################################
  
  # need ytdl python documentation 
  # javascript is easier )':
  # idk wtf the methods are to even use for python ytdl

  musicQueue = queue.Queue()

  async def play(message, musicQueue):
    args = message.content.split()

    voiceChannel = message.author.voice.channel

    if (not voiceChannel):
      await message.channel.send("You need to be in a voice channel to play music!")
    
    await voiceChannel.connect()
    # permissions = voiceChannel.permissionsFor(message.client.user);
    # if (not permissions.has("CONNECT") or not permissions.has("SPEAK")):
    #   await message.channel.send(
    #     "I need the permissions to join and speak in your voice channel!"
    #   )

    #song = {"title": songInfo.videoDetails.title, "url": songInfo.videoDetails.video_url }

    if (not musicQueue):
      pass

  if (message.content.startswith("}play")):
    await play(message, musicQueue) 
    return
  elif (message.content.startswith("}skip")):
    await skip(message, musicQueue) 
    return
  elif (message.content.startswith("}stop")):
    await stop(message, musicQueue) 
    return
  elif (message.content.startswith("}leave")):
    await message.guild.voice_client.disconnect()
    return

  ###########################################
  #               Tic-Tac-Toe               #
  ###########################################
  if message.content.startswith('}ttt'):
    turn = 1
    won = False
    unchosen = ['1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣']
    chosen = []

    def movecheck1(reaction, user):
      if reaction.emoji in chosen and user == message.author:
        client.loop.create_task(channel.send("Box is already taken fuwucqing cheater."))
      return reaction.emoji in unchosen and user == message.author

    def movecheck2(reaction, user):
      if reaction.emoji in chosen and user == message.mentions[0]:
        client.loop.create_task(channel.send("Box is already taken fuwucqing cheater."))
      return reaction.emoji in unchosen and user == message.mentions[0]
    
    board = [[":white_large_square:" for x in range(3)] for x in range(3)]

    channel = message.channel
    if len(message.mentions) == 0:
      await channel.send('The command is }ttt (mention your opponent).')
      return
    
    if len(message.mentions) > 1:
      await channel.send('You can only challenge one person at a time.')
      return

    if message.mentions[0].name == message.author.name:
      await channel.send('You cannot challenge yourself!')
      return
    
    if message.mentions[0].name == "BotCato":
      await channel.send('Sorry I\'m too good for you idot')
      return

    while won == False:
      if turn == 1:
        player = message.author.mention
        boardMSG = await channel.send(helper.boardToStr(board))
        turnMSG = await channel.send(content = (player + ' pick your square!'))
        for i in range(9):
          await turnMSG.add_reaction(unchosen[i])
        sign = ":o:"
        reaction, user = await client.wait_for('reaction_add', check=movecheck1)
        await turnMSG.clear_reaction(reaction.emoji)
      elif turn % 2 != 0:
        player = message.author.mention
        await boardMSG.edit(content = helper.boardToStr(board))
        await turnMSG.edit(content = (player + ' pick your square!'))
        sign = ":o:"
        reaction, user = await client.wait_for('reaction_add', check=movecheck1)
        await turnMSG.clear_reaction(reaction.emoji)
      else:
        player = message.mentions[0].mention
        await boardMSG.edit(content = helper.boardToStr(board))
        await turnMSG.edit(content = (player + ' pick your square!'))
        sign = ":x:"
        reaction, user = await client.wait_for('reaction_add', check=movecheck2)
        await turnMSG.clear_reaction(reaction.emoji)
      unchosen.remove(reaction.emoji) 
      chosen.append(reaction.emoji)
      if reaction.emoji == '1⃣':
        board[0][0] = sign
      elif reaction.emoji == '2⃣':
        board[0][1] = sign
      elif reaction.emoji == '3⃣':
        board[0][2] = sign
      elif reaction.emoji == '4⃣':
        board[1][0] = sign
      elif reaction.emoji == '5⃣':
        board[1][1] = sign
      elif reaction.emoji == '6⃣':
        board[1][2] = sign
      elif reaction.emoji == '7⃣':
        board[2][0] = sign
      elif reaction.emoji == '8⃣':
        board[2][1] = sign
      elif reaction.emoji == '9⃣':
        board[2][2] = sign
      if ((board[0][0] == board[0][1] == board[0][2] or board[0][0] == board[1][0] == board[2][0] or board[0][0] == board[1][1] == board[2][2]) and board[0][0] != ":white_large_square:") or ((board[0][1] == board[1][1] == board[2][1] or board[1][0] == board[1][1] == board[1][2] or board[0][2] == board[1][1] == board[2][0]) and board[1][1] != ":white_large_square:") or ((board[2][0] == board[2][1] == board[2][2]) and board[2][0] != ":white_large_square:"):
        await turnMSG.clear_reactions()
        await turnMSG.edit(content = (player + ' has won!'))
        won = True
        break
      if turn == 9:
        await turnMSG.clear_reactions()
        await turnMSG.edit(content = ('It is a Thai!'))
        break
      turn+=1

  ###########################################
  #               Coinflip                  #
  ###########################################
  if message.content.startswith('}coinflip'):
    channel = message.channel
    HoTmsg = await channel.send('Heads or tails?')
    happythonk = discord.utils.get(message.guild.emojis, name='happythonk')
    thonktails = discord.utils.get(message.guild.emojis, name='thonktails')
    def Reactcheck(reaction, user):
      return (reaction.emoji == happythonk or reaction.emoji == thonktails) and user == message.author

    if happythonk and thonktails:
      await HoTmsg.add_reaction(happythonk)
      await HoTmsg.add_reaction(thonktails)
    reaction, user = await client.wait_for('reaction_add', check=Reactcheck)
    reactionlist = [reaction.emoji]
    if reaction.emoji == happythonk:
      result = 0
      reactionlist.append(thonktails)
    else:
      result = 1
      reactionlist.append(happythonk)
    if result == helper.coinflip():
      await HoTmsg.edit(content= (str(reactionlist[0]) + ' was chosen'+ '\n' + message.author.mention +' won!'))
    else: 
      await HoTmsg.edit(content= (str(reactionlist[1]) + ' was chosen'+ '\n' + message.author.mention +' lost!'))

  ###########################################
  #              Miscellaneous              #
  ###########################################
  if message.content.startswith("}say"):
    await message.channel.send(" ".join(message.content.split()[1:]))

  if "😎" in message.content and message.author.name == "dog": 
    await message.channel.send("I agree dog")
  
  if ":(" in message.content or "😔" in message.content or "😦" in message.content:
    await message.channel.send("same.")
  
  if message.content.startswith("}dog"):
    animals = ["https://dog.ceo/api/breeds/image/random","https://api.thecatapi.com/v1/images/search"]
    url = helper.blockDistributer(animals,[0.95,0.05])
    request = requests.get(url)
    try:
      dog=json.loads(request.text)["message"]
      await message.channel.send(dog)
    except:
      cat=json.loads(request.text)[0]["url"]
      await message.channel.send(cat)
  
  if message.content.startswith("}testdog"):
    animals = ["https://dog.ceo/api/breeds/image/random","https://api.thecatapi.com/v1/images/search"]
    url = helper.blockDistributer(animals,[0.95,0.05])
    request = requests.get(url)
    try:
      dog=json.loads(request.text)["message"]
      breed = dog[dog.find("breed"):dog.find("/")]
      print(dog)
      print(dog.find("breeds/").find("/"))
      await message.channel.send(embed = discord.Embed().set_image(url = dog).add_field(name = "Dog's Breed",value = "breed"))
    except:
      cat=json.loads(request.text)[0]["url"]
      await message.channel.send(cat)

keep_alive()
client.run(os.getenv('TOKEN'))