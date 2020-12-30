class Encounter:
  def __init__(self, name, action="", drop="", dropamount=[],droprates=[]):
    self.name = name
    self.action = action
    self.drop = drop
    self.dropamount = dropamount
    self.droprates = droprates