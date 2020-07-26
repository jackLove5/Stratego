from pieces import *
from board_configuration import *
from game import *
from constants import *

def get_piece_from_rank(rank, team):
  if (rank == 'S'):
    ret = Spy(team)
  elif (rank == '8'):
    ret = Miner(team)
  elif(rank.isdigit()):
    ret = MoveablePiece(rank, team)
  else:
    ret = Piece(rank, team)

  return ret

# coordinates of the lake; out of bounds

"""
Gameboard class. Hold pieces, validates moves, carries out moves, and
determines winner
"""
class Board:
  def __init__(self, human_pieces, bot_pieces):
    board = []
    for i in range(0, Constants.BOARD_SIZE):
      row = []
      for j in range(0, Constants.BOARD_SIZE):
        row.append(None)
      board.append(row)

    # Place bot pieces (fill rows 0-3)
    b_config = bot_pieces.get_config()
    col = 9
    for i, c in enumerate(b_config):
      board[int(3 - i // Constants.BOARD_SIZE)][col] = (
        get_piece_from_rank(c, Constants.BOT_NAME))

      col = (int(col - 1 + Constants.BOARD_SIZE)) % Constants.BOARD_SIZE

    # Place human's pieces (fill rows 6-9)
    h_config = human_pieces.get_config()
    col = 0
    for i, c in enumerate(h_config):
      board[int(6 + (i // Constants.BOARD_SIZE))][col] = (
        get_piece_from_rank(c, Constants.PLAYER_NAME))

      col = (col + 1) % Constants.BOARD_SIZE

    self._board = board

  # print the board to the screen
  def draw(self):
    board = self._board
    for i in range(len(board)):
      print(str(i) + ' ', end='')
      for j in range(len(board[i])):
        if ([i,j] in Constants.LAKE_COORDS):
          print('~', end='')
        elif(board[i][j] is None):
          print('_', end='')
        elif (board[i][j].get_team() == Constants.BOT_NAME):
          print('\033[31m' + board[i][j].get_rank() + '\033[0m', end='')
        else:
          print('\033[34m' + board[i][j].get_rank() + '\033[0m', end='')

      print()

    print('  ABCDEFGHIJ')
  
  def to_json(self, turn, message):
    json = '{"board": '
    board = self._board
    json += '['
    for i in range(len(board)):
      json +=  "["
      for j in range(len(board[i])):
        if ([i,j] in Constants.LAKE_COORDS):
          json += '{"rank": "~", "team": "None"}'
        elif(board[i][j] is None):
          json += '{"rank": "None", "team": "None"}'
        elif (board[i][j].get_team() == Constants.BOT_NAME):
          json += '{"rank": "X", "team": "Red"}'
        else:
          json += '{"rank": "' + board[i][j].get_rank() + '", "team": "Blue"}'
        
        json += (']' if j == len(board) - 1 else ',')        
      
      json += (']' if i == len(board) - 1 else ',')

    if (self.has_win()):
      message += '\\n' + self.get_winner() + ' wins!';

    json +=  ',"Turn": "' + turn + '"'
    json += ',"Message": "' + message + '"'
    json += '}'
    return json

  """
  swap two game pieces
  positions are lists: [row, col]
  """ 
  def swap_pieces(self, pos1, pos2):
    tmp = self._board[pos1[0]][pos1[1]]
    self._board[pos1[0]][pos1[1]] = self._board[pos2[0]][pos2[1]]
    self._board[pos2[0]][pos2[1]] = tmp

  """
  return true iff the position holds one of the human's pieces
  precondition: 'pos' is a valid position on the board
  """
  def has_player_piece(self, pos):
    obj = self._board[pos[0]][pos[1]]
    if (obj is None):
      return False

    return obj.get_team() == Constants.PLAYER_NAME

  """
  Validate a player's movement. Returns true iff the move is valid
  """
  def validate_move(self, src_pos, dst_pos, team_to_move):
    src_obj = self._board[src_pos[0]][src_pos[1]]
    dst_obj = self._board[dst_pos[0]][dst_pos[1]]
    # Tried to move from an empty space
    if (src_obj is None):
      return False
    
    # Tried to move the wrong team
    if (src_obj.get_team() != team_to_move):
      return False

    # Tried to move an immovable piece
    if (src_obj.get_rank() == 'B' or src_obj.get_rank() == 'F'):
      return False

    # Tried to move in the lake
    if (dst_pos in Constants.LAKE_COORDS):
      return False

    start_x = src_pos[1]
    end_x = dst_pos[1]
    start_y = src_pos[0]
    end_y = dst_pos[0]
    direction = 1 if (end_x - start_x > 0) or (end_y - start_y > 0) else -1
    dx = abs(start_x - end_x)
    dy = abs(start_y - end_y)

    # Didn't move in a straight line
    if (dx > 0 and dy > 0):
      return False

    # Moving more than one square
    if (dx > 1 or dy > 1):
      # piece is not a scout
      if (src_obj.get_rank() != '9'):
        return False
      
      # Verify the path is clear
      for i in range(dy):
        # ignore self
        if (i == 0):
          continue 
        
        path_obj = self._board[start_y + i * direction][start_x]
        # Tried to hop over pieces or lake
        if (path_obj is not None or [start_y + i * direction, start_x]
          in Constants.LAKE_COORDS):
          return False
      
      for i in range(dx):
        if (i == 0):
          continue
        
        path_obj = self._board[start_y][start_x + i * direction]
        if (not (path_obj is None) or [start_y, start_x + i * direction] in
          Constants.LAKE_COORDS):
          return False

    # true iff destination space is empty or occupied by opposite team
    return (dst_obj is None) or (dst_obj.get_team() != src_obj.get_team())

  # execute a valid move
  def do_move(self, src_pos, dst_pos):
    board = self._board
    src_y = src_pos[0]
    src_x = src_pos[1]
    dst_y = dst_pos[0]
    dst_x = dst_pos[1]
    src_obj = board[src_y][src_x]
    dst_obj = board[dst_y][dst_x]

    if (abs(src_x - dst_x) > 1 or abs(src_y - dst_y) > 1):
      src_obj.set_known_scout()

    src_obj.set_has_moved()
    board[src_y][src_x] = None
    if (dst_obj is None):
      # Moved to empty space
      board[dst_y][dst_x] = src_obj
      return ''
    else:
      # Moved to enemy space
    
      # Both pieces engaging in combat; their ranks are now known to each other
      src_obj.set_is_visible()
      dst_obj.set_is_visible()
      
      src_dead = False
      dst_dead = False
      combat_res = src_obj.combat(dst_obj)
      if (combat_res < 0):
        src_dead = True
      elif (combat_res > 0):
        board[dst_y][dst_x] = src_obj
        dst_dead = True
      else:
        board[dst_y][dst_x] = None
        src_dead = True
        dst_dead = True

      ret = ''
      if (src_dead):
        ret += (src_obj.get_team() + "'s " + src_obj.get_name() + 
          " removed by " + dst_obj.get_team() + "'s " + dst_obj.get_name())

      if (dst_dead):
        if ret != '':
          ret = ret + '\\n'
        ret = ret + dst_obj.get_team() + "\'s " + dst_obj.get_name() + ' removed by ' + \
          src_obj.get_team() + "\'s " + src_obj.get_name()
      return ret

  # checks win consition. Return true iff there's a winner
  def has_win(self):
    # return true if there's only 1 flag on the board
    # or if only one team has moveable pieces
    has_moveable_list = []
    board = self._board
    flag_count = 0
    for row in board:
      for piece in row:
        if (piece is not None):
          if (piece.get_rank() == 'F'):
            flag_count = flag_count + 1
          elif (piece.get_rank() != 'B'):
            if (piece.get_team() not in has_moveable_list):
              has_moveable_list.append(piece.get_team())

    return flag_count == 1 or len(has_moveable_list) < 2

  """
  get the winner of the game
  precondition: a team has one the game
  """
  def get_winner(self):
    board = self._board
    has_flag_list = []
    has_moveable_list = []
    for row in board:
      for piece in row:
        if (piece is not None):
          if (piece.get_rank() == 'F'):
            if (piece.get_team() not in has_flag_list):
              has_flag_list.append(piece.get_team())
          elif (piece.get_rank() != 'B'):
            if (not (piece.get_team() in has_moveable_list)):
              has_moveable_list.append(piece.get_team())

    if (len(has_flag_list) == 1):
      return has_flag_list[0]
    else:
      return has_moveable_list[0]
