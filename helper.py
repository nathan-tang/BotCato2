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