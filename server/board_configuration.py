"""
A class that represents an initial stratego setup
pieces are placed on the board starting from the player's top left corner
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
    valid_piece_counts = {
      'B': 6,
      '1': 1,
      '2': 1,
      '3': 2,
      '4': 3,
      '5': 4,
      '6': 4,
      '7': 4,
      '8': 5,
      '9': 8,
      'S': 1,
      'F': 1
    }

    for c in str:
      if (c in valid_piece_counts):
        valid_piece_counts[c] -= 1
      else:
        return False

    return (len(str) == 40 and
      all(x == 0 for x in list(valid_piece_counts.values())))

  def get_config(self):
    return self._str
