class Constants:
  BOARD_SIZE = 10
  PLAYER_NAME = 'player'
  BOT_NAME = 'bot'
  RANKS = '123456789SBF'
  VALID_PIECE_COUNTS = {
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

  RANK_TO_NAME = {
    'F': 'Flag',
    'B': 'Bomb',
    'S': 'Spy',
    '9': 'Scout',
    '8': 'Miner',
    '7': 'Sergeant',
    '6': 'Lieuteant',
    '5': 'Captain', 
    '4': 'Major',
    '3': 'Colonel',
    '2': 'General',
    '1': 'Marshall'
  }
  
  LAKE_COORDS = [[4,2],[4,3],[5,2],[5,3],[4,6],[4,7],[5,6],[5,7]]
