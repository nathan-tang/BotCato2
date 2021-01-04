class ResourceEncounter:
  def __init__(self, name, action="", drop="", dropamount=[],droprates=[]):
    self.name = name
    self.action = action
    self.drop = drop
    self.dropamount = dropamount
    self.droprates = droprates

class AnimalEncounter:
  def __init__(self, name, action="🔪", drop="cut_of_meat", dropamount=[1,2,3],droprates=[1/3,1/3,1/3]):
    self.name = name
    self.action = action
    self.drop = drop
    self.dropamount = dropamount
    self.droprates = droprates

class MobEncounter:
  def __init__(self, name, action="", drop="", dropamount=[],droprates=[], health=""):
    self.name = name
    self.action = action
    self.drop = drop
    self.dropamount = dropamount
    self.droprates = droprates

class Food:
  def __init__(self, name, emoji, fill):
    self.name = name
    self.emoji = emoji
    self.fill = fill