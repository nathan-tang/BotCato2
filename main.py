import discord
import random
from numpy.random import choice
from collections import defaultdict
import os
from classes import Encounter

client = discord.Client()

def coinflip():
  return random.randint(0,1)

def blockDistributer(listofitems):
  items = listofitems
  probabilities = [0.6,0.1,0.1,0.1,0.1]
  return choice(items,p=probabilities)


def boardtostr(board):
  return board[0][0] + board[0][1] + board[0][2] + '\n' + board[1][0] + board[1][1] + board[1][2] + '\n' + board[2][0] + board[2][1] + board[2][2] + '\n'


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user: return

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

  if message.content.startswith("}say"):
    await message.channel.send(" ".join(message.content.split()[1:]))

  if message.content.startswith("}help"):
    if coinflip() == 1:
      await message.channel.send("I need help too.");
      responses = ["are you okay", "hang in there", "???", "loser"]
      answer = await client.wait_for('message')
      if (answer.content.lower() in responses):
        await message.channel.send("):");
    else:
      await message.channel.send("""
        :hot_face: **Main Commands** :hot_face::
}coinflip - flip a coin
}ttt <@mention> - challenge another person to tic-tac-toe
}help - help me please  
      """)

      
  if message.content.startswith("😎") and message.author.name == "dog": 
    await message.channel.send("I agree dog")
  

  if message.content.startswith("}minecraft"):

    def numToEmoji(num: int) -> str:
      """ converts ints into emoji string representation """
      s = [x for x in str(num)]
      for index, letter in enumerate(s):
        if letter == "0":
          s[index] = ":zero:"
        elif letter == "1":
          s[index] = ":one:"
        elif letter == "2":
          s[index] = ":two:"
        elif letter == "3":
          s[index] = ":three:"
        elif letter == "4":
          s[index] = ":four:"
        elif letter == "5":
          s[index] = ":five:"
        elif letter == "6":
          s[index] = ":six:"
        elif letter == "7":
          s[index] = ":seven:"
        elif letter == "8":
          s[index] = ":eight:"
        elif letter == "9":
          s[index] = ":nine:"
      return "".join(s)

    def inventoryToEmoji(inv: dict) -> str:
      """ k value must be named after discord emoji """
      result = ""
      for k,v in inv.items():
          result += ":" + k + ":" + numToEmoji(v)
      return result
    
    # Animal Encounters
    man = Encounter(":man_running:")
    pig = Encounter(":pig2:","🔪","pig")
    cow = Encounter(":cow2:","🔪","cow")

    # Resources Encounters
    tree = Encounter(":evergreen_tree:","🪓","wood")
    rock = Encounter(":rock:","⛏","rock")

    # Enviroment Encounters
    blacksquare = Encounter(":black_large_square:")
    greensquare = Encounter(":green_square:")

    # All Encounters
    encounters = [blacksquare,pig,tree,rock,cow]

    # Initialize Playing Field
    playField = [[blockDistributer(encounters) for x in range(11)] for x in range(2)] + [[greensquare for x in range(11)]]
    playField[1][10] = man

    # Initialize Player Statistics
    health = [":heart: "] + [":red_square:" for x in range(10)]
    hunger = [":meat_on_bone:"]+ [":brown_square:" for x in range(10)]
    inventory = defaultdict(int)
    steps = 0
    actions = ["⬅","➡","🔪","🪓","⛏"]

    def moveCheck(reaction, user):
      return reaction.emoji in actions and reaction.message == grassMSG and user != grassMSG.author

    possibleBlocks = [":black_large_square:",":evergreen_tree:",":pig2:",":rock:"]
    blockChoice = 0
    await message.channel.send("".join(i.name for i in playField[0]))
    playerMSG = await message.channel.send("".join(i.name for i in playField[1]))
    grassMSG = await message.channel.send("".join(i.name for i in playField[2]))
    healthMSG = await message.channel.send("".join(health))
    hungerMSG = await message.channel.send("".join(hunger))
    inventoryMSG = await message.channel.send("឵឵឵" + "".join(inventoryToEmoji(inventory)))
    await grassMSG.add_reaction("⬅")
    await grassMSG.add_reaction("➡")
    while(len(health) > 1):
      if playField[1][9] != blacksquare:
        await grassMSG.add_reaction(playField[1][9].action)

      reaction, user = await client.wait_for('reaction_add', check=moveCheck)
      if playField[1][9] != blacksquare:
        await grassMSG.clear_reaction(playField[1][9].action)

      if reaction.emoji == "🔪":
        if (playField[1][9] == pig):
          inventory["pig"] += random.randint(1,3)
        elif (playField[1][9] == cow):
          inventory["cow"] += random.randint(1,3)
        await inventoryMSG.edit(content = "឵឵឵" + "".join(inventoryToEmoji(inventory)))
        playField[1][9] = blacksquare
      elif reaction.emoji == "🪓":
        inventory["wood"] += random.randint(5,8)
        await inventoryMSG.edit(content = "឵឵឵" + "".join(inventoryToEmoji(inventory)))
        playField[1][9] = blacksquare
      elif reaction.emoji == "⛏":
        inventory["rock"] += random.randint(1,3)
        await inventoryMSG.edit(content = "឵឵឵" + "".join(inventoryToEmoji(inventory)))
        playField[1][9] = blacksquare     

      if reaction.emoji == "⬅":
        steps += 1
        for i in reversed(range(9)):
          playField[1][i+1] = playField[1][i]
        if steps % 5 == 0:
          if len(hunger) > 1:
            hunger.pop()
            # try:
            #   lastHunger = len(healthHunger[1]) - 1 - healthHunger[1][::-1].index(":brown_square:")
            #   healthHunger[1][lastHunger] = ":black_large_square:"
            # except ValueError:
            #  pass
            await hungerMSG.edit(content = "".join(hunger))
        if len(hunger) == 1:
          if steps % 2 == 0:
            if len(health) > 1:
              health.pop()
              await healthMSG.edit(content = "".join(health))
        playField[1][0] = blockDistributer(encounters)
      await playerMSG.edit(content = "".join(i.name for i in playField[1]))
    death = Encounter(":headstone:")
    playField[1][10] = death
      
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




client.run(os.getenv('TOKEN'))