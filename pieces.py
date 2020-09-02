# Contains all the Piece classes
# Implements game piece combat and identities
from constants import Constants

"""
Generic Stratego game piece
"""
class Piece(object):
    # Initializes a new game Piece object
    def __init__(self, rank, team):
        self._name = Constants.RANK_TO_NAME[rank]
        self._rank = rank
        self._team = team
        self._is_visible = False
        self._moved = False
        self._known_scout = False

    def get_name(self):
        return self._name

    def get_rank(self):
        return self._rank

    def get_team(self):
        return self._team

    def set_has_moved(self):
        self._moved = True

    def is_visible(self):
      return self._is_visible

    def set_is_visible(self):
        self._is_visible = True

    def has_moved(self):
      return self._moved

    def is_known_scout(self):
      return self._known_scout
    
    def set_known_scout(self):
      self.known_scout = True

"""
All numbered pieces and the Spy.
Implements combat between pieces
"""
class MoveablePiece(Piece):
  def __init__(self, rank, team):
    super(MoveablePiece, self).__init__(rank, team)

  """
  Returns positive if the current piece wins, negative if it loses,
  0 if it's a tie
  """
  def combat(self, other):
    if (other.get_rank() == 'F' or other.get_rank() == 'S'):
      return 1
    elif (other.get_rank() == 'B'):
      return -1
    else:
      return ord(other.get_rank()) - ord(self.get_rank())

"""
Miner piece (8)
Miner beats bomb in combat
"""
class Miner(MoveablePiece):
  def __init__(self, team):
    super(Miner, self).__init__('8', team)

  def combat(self, other):
    if (other.get_rank() == 'B'):
      return 1

    return super(Miner, self).combat(other)

"""
Spy piece (S)
Spy beats Marshall if Spy attacks first
"""
class Spy(MoveablePiece):
  def __init__(self, team):
    super(Spy, self).__init__('S', team)

  def combat(self, other):
    if (other.get_rank() == '1' or other.get_rank() == 'F'):
      return 1
    if (other.get_rank() == 'S'):
      return 0
    else:
      return -1
