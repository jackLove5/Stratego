from constants import *

"""
A class that represents an initial stratego setup.
Pieces are placed on the board starting from the player's top left corner
"""
class BoardConfiguration:
  def __init__(self, str):
    self._str = str
    if (self._validate(self._str) is False):
      raise ValueError('Invalid board configuration')

  """
  Validate the contents of a boardconfiguration
  Must be 40 characters long and include the correct number of each rank
  """
  def _validate(self, str):
    valid_piece_counts = dict(Constants.VALID_PIECE_COUNTS)

    for c in str:
      if (c in valid_piece_counts):
        valid_piece_counts[c] -= 1
      else:
        return False

    return (len(str) == 40 and
      all(x == 0 for x in list(valid_piece_counts.values())))

  def get_config(self):
    return self._str
