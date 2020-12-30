import discord
import random
from numpy.random import choice
from collections import defaultdict
import os
import asyncio
from classes import Encounter
from helper import numToEmoji

client = discord.Client()

def coinflip():
  return random.randint(0,1)

def blockDistributer(listofitems, probabilities):
  items = listofitems
  return choice(items,p=probabilities)

def boardtostr(board):
  return board[0][0] + board[0][1] + board[0][2] + '\n' + board[1][0] + board[1][1] + board[1][2] + '\n' + board[2][0] + board[2][1] + board[2][2] + '\n'


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user: return

  ###########################################
  #                   Help                  #
  ###########################################
  if message.content.startswith("}help"):
    helpMessage = discord.Embed(title=":hot_face: **Main Commands**:")
    helpMessage.add_field(name="}minecraft", value="Minecraft, but not really", inline=False)
    helpMessage.add_field(name="}ttt <@mention>", value="Tic-Tac-Toe, challenge a friend!", inline=False)
    helpMessage.add_field(name="}coinflip", value="coinflip, test your odds", inline=False)
    await message.channel.send(embed=helpMessage)

  ###########################################
  #               Minecraft                 #
  ###########################################
  if message.content.startswith("}minecraft") or message.content.startswith("}mc"):

    def inventoryToEmoji(inv: dict) -> str:
      """ k value must be named after discord emoji """
      result = ""
      for k,v in inv.items():
          result += ":" + k + ":" + numToEmoji(v)
      return result
    
    # Animal Encounters
    man = Encounter(":man_running:")
    pig = Encounter(":pig2:","🔪","pig",[1,2,3],[1/3,1/3,1/3])
    cow = Encounter(":cow2:","🔪","cow",[1,2,3],[1/3,1/3,1/3])
    rabbit = Encounter(":rabbit2:","🔪","rabbit",[1],[1])
    goat = Encounter(":goat:","🔪","goat",[1],[1])

    # Resources Encounters
    tree = Encounter(":evergreen_tree:","🪓","wood",[5,6,7,8],[1/4,1/4,1/4,1/4])
    rock = Encounter(":mountain:","⛏","mountain",[1],[1])
    cactus = Encounter(":cactus:","🪓","cactus",[1,2,3],[1/3,1/3,1/3])

    # Enviroment Encounters
    blacksquare = Encounter(":black_large_square:")
    greensquare = Encounter(":green_square:")

    # All Encounters
    encounters = [blacksquare,pig,tree,rock,cow] # Forest/Plain Biome
    desertEncounters = [blacksquare,rock,cactus,rabbit]
    snowEncounters = [blacksquare,rock,tree,goat] 
    encountersprob = [0.6,0.1,0.1,0.1,0.1]

    # Initialize Playing Field
    playField = [[blacksquare for x in range(11)]] + [[blockDistributer(encounters, encountersprob) for x in range(11)]] + [[greensquare for x in range(11)]]
    playField[1][10] = man

    # Initialize Player Statistics
    health = [":heart: "] + [":red_square:" for x in range(10)]
    hunger = [":meat_on_bone:"]+ [":brown_square:" for x in range(10)]
    inventory = defaultdict(int)
    steps = 0
    actions = ["⬅","🔪","🪓","⛏"]

    def moveCheck(payload):
      return str(payload.emoji) in actions and payload.message_id == grassMSG.id and payload.user_id != grassMSG.author.id
    
    def moveCheck2(payload):
      return str(payload.emoji) == "⬅" and payload.message_id == grassMSG.id

    # Sends PlayField as bot messages
    await message.channel.send("".join(i.name for i in playField[0]))
    playerMSG = await message.channel.send("".join(i.name for i in playField[1]))
    grassMSG = await message.channel.send("".join(i.name for i in playField[2]))
    healthMSG = await message.channel.send("".join(health))
    hungerMSG = await message.channel.send("".join(hunger))
    inventoryMSG = await message.channel.send("឵឵឵" + "".join(inventoryToEmoji(inventory)))
  
    await grassMSG.add_reaction("⬅")
    while(len(health) > 1):
      if playField[1][9] != blacksquare:
        await grassMSG.add_reaction(playField[1][9].action)

      # Wait for User Input via Discord Reaction
      pending_tasks = [client.wait_for('raw_reaction_add',check=moveCheck), client.wait_for('raw_reaction_remove',check=moveCheck2)]
      done_tasks, pending_tasks = await asyncio.wait(pending_tasks,return_when=asyncio.FIRST_COMPLETED)
      for task in done_tasks: payload = await task
      reaction = str(payload.emoji)

      if playField[1][9] != blacksquare:
        await grassMSG.clear_reaction(playField[1][9].action)

      # Player Encounter Actions
      if reaction not in ["⬅"]:
        inventory[playField[1][9].drop] += blockDistributer(playField[1][9].dropamount,playField[1][9].droprates)
        await inventoryMSG.edit(content = "឵឵឵" + "".join(inventoryToEmoji(inventory)))
        playField[1][9] = blacksquare   

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
        playField[1][0] = blockDistributer(encounters, encountersprob)
      await playerMSG.edit(content = "".join(i.name for i in playField[1]))
    
    # Player Death
    death = Encounter(":headstone:")
    playField[1][10] = death
      
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
        boardMSG = await channel.send(boardtostr(board))
        turnMSG = await channel.send(content = (player + ' pick your square!'))
        for i in range(9):
          await turnMSG.add_reaction(unchosen[i])
        sign = ":o:"
        reaction, user = await client.wait_for('reaction_add', check=movecheck1)
        await turnMSG.clear_reaction(reaction.emoji)
      elif turn % 2 != 0:
        player = message.author.mention
        await boardMSG.edit(content = boardtostr(board))
        await turnMSG.edit(content = (player + ' pick your square!'))
        sign = ":o:"
        reaction, user = await client.wait_for('reaction_add', check=movecheck1)
        await turnMSG.clear_reaction(reaction.emoji)
      else:
        player = message.mentions[0].mention
        await boardMSG.edit(content = boardtostr(board))
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
    if result == coinflip():
      await HoTmsg.edit(content= (str(reactionlist[0]) + ' was chosen'+ '\n' + message.author.mention +' won!'))
    else: 
      await HoTmsg.edit(content= (str(reactionlist[1]) + ' was chosen'+ '\n' + message.author.mention +' lost!'))

  ###########################################
  #              Miscellaneous              #
  ###########################################
  if message.content.startswith("}say"):
    await message.channel.send(" ".join(message.content.split()[1:]))

  if message.content.startswith("😎") and message.author.name == "dog": 
    await message.channel.send("I agree dog")


client.run(os.getenv('TOKEN'))