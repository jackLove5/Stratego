from pieces import *
from board_configuration import BoardConfiguration
from constants import Constants

"""
Construct a piece object given its rank and team
"""
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

"""
Gameboard class. Holds pieces, validates moves, carries out moves, and
determines winner
"""
class Board:
  def __init__(self, p1_pieces, p2_pieces):
    self._board = [[None for x in range(Constants.BOARD_SIZE)] for y in range(Constants.BOARD_SIZE)]
    self._place_pieces(p1_pieces, False)
    self._place_pieces(p2_pieces, True)

  """
  Place a given player's pieces on the board
  """
  def _place_pieces(self, pieces, is_player2):
    if is_player2:
      self._flip()
    
    # Fill rows 6-9
    p_config = pieces.get_config()
    col = 0
    team = Constants.PLAYER_TWO_NAME if is_player2 else Constants.PLAYER_ONE_NAME
    for i, c in enumerate(p_config):
      self._board[int(6 + i // Constants.BOARD_SIZE)][col] = (
        get_piece_from_rank(c, team))

      col = (col + 1) % Constants.BOARD_SIZE

    if is_player2:
      self._flip()

  """
  Print the board to the screen
  """
  def draw(self):
    board = self._board
    for i in range(len(board)):
      print(str(i) + ' ', end='')
      for j in range(len(board[i])):
        if ([i,j] in Constants.LAKE_COORDS):
          print('~', end='')
        elif(board[i][j] is None):
          print('_', end='')
        elif (board[i][j].get_team() == Constants.PLAYER_TWO_NAME):
          print('\033[31m' + board[i][j].get_rank() + '\033[0m', end='')
        else:
          print('\033[34m' + board[i][j].get_rank() + '\033[0m', end='')

      print()

    print('  ABCDEFGHIJ')
 
  """
  Serialize the board given the current player's name, 
  and messages to include, and the player's name who should move next
  """ 
  def to_json(self, current_player_name, messages, turn):
    if current_player_name == Constants.PLAYER_TWO_NAME:
      self._flip()

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
        elif (board[i][j].get_team() != current_player_name):
          json += '{"rank": "X", "team": "Red"}'
        else:
          json += '{"rank": "' + board[i][j].get_rank() + '", "team": "Blue"}'
        
        json += (']' if j == len(board) - 1 else ',')        
      
      json += (']' if i == len(board) - 1 else ',')

    if (self.has_win()):
      winner_name = self.get_winner()
      message = 'You win!' if winner_name == current_player_name else 'Your opponent wins!'
      messages.append(message)

    json += ',"messages": ['
    for i in range(len(messages)):
      json += '"' + messages[i] + '"'
      if i < len(messages) - 1:
        json += ','
    
    json += '], "turn": ';
    json += '"Blue"' if turn == current_player_name else '"Red"'
    json += '}'

    if current_player_name == Constants.PLAYER_TWO_NAME:
      self._flip()

    return json

  """
  Rotate the board 180 degrees
  """
  def _flip(self): 
    for row in range(len(self._board)):
      self._board[row] = self._board[row][::-1]
    
    for col in range(len(self._board)):
      column = [self._board[x][col] for x in range(len(self._board))]
      column = column[::-1]
      
      for x in range(len(self._board)):
        self._board[x][col] = column[x]

  """
  Swap two game pieces
  positions are lists: [row, col]
  """ 
  def swap_pieces(self, pos1, pos2):
    tmp = self._board[pos1[0]][pos1[1]]
    self._board[pos1[0]][pos1[1]] = self._board[pos2[0]][pos2[1]]
    self._board[pos2[0]][pos2[1]] = tmp

  """
  Return true iff the position holds one of the specified player's pieces
  precondition: 'pos' is a valid position on the board
  """
  def has_player_piece(self, pos, player_name):
    obj = self._board[pos[0]][pos[1]]
    if (obj is None):
      return False

    return obj.get_team() == player_name

  """
  Validate a player's movement. Returns true iff the move is valid
  """
  def validate_move(self, src_pos, dst_pos, team_to_move):
    if any(x < 0 or x >= len(self._board) for x in src_pos + dst_pos):
      return False

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

  """
  Execute a valid move.
  Return any combat results as a list of pairs: [dead_piece, attacking_piece]
  """
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
    combat_results = []
    if (dst_obj is None):
      # Moved to empty space
      board[dst_y][dst_x] = src_obj
    else:
      # Moved to enemy space
    
      # Both pieces engaging in combat; their ranks are now known to each other
      src_obj.set_is_visible()
      dst_obj.set_is_visible()
      
      combat_res = src_obj.combat(dst_obj)
      
      if (combat_res < 0):
        # src_obj gets captured
        combat_results.append([src_obj, dst_obj])
      elif (combat_res > 0):
        # dst_obj gets captured
        board[dst_y][dst_x] = src_obj
        combat_results.append([dst_obj, src_obj])
      else:
        # both pieces get captured
        board[dst_y][dst_x] = None
        combat_results.append([dst_obj, src_obj])
        combat_results.append([src_obj, dst_obj])

    return combat_results

  """
  Check win condition. Return true iff there's a winner
  """
  def has_win(self):
    # return true if there's only 1 flag on the board
    # or if only one team has moveable pieces
    has_moveable_list = []
    board = self._board
    flag_count = 0
    for row in range(len(board)):
      for col in range(len(board)):
        piece = board[row][col]
        if (piece is not None):
          if (piece.get_rank() == 'F'):
            flag_count = flag_count + 1
          elif piece.get_rank() != 'B' and self._has_move(row, col, piece.get_team()):
            if (piece.get_team() not in has_moveable_list):
              has_moveable_list.append(piece.get_team())

    return flag_count == 1 or len(has_moveable_list) < 2

  """
  Check if a piece is able to make a move
  """
  def _has_move(self, row, col, team):
    res = False
    src_pos = [row, col]
    for x in [-1, 1]:
      res = res or self.validate_move(src_pos, [row + x, col], team)
      res = res or self.validate_move(src_pos, [row, col + x], team)
    return res


  """
  get the winner of the game
  precondition: a team has won the game
  """
  def get_winner(self):
    board = self._board
    has_flag_list = []
    has_moveable_list = []
    for row in range(len(board)):
      for col in range(len(board)):
        piece = board[row][col]
        if (piece is not None):
          if (piece.get_rank() == 'F'):
            if (piece.get_team() not in has_flag_list):
              has_flag_list.append(piece.get_team())
          elif (piece.get_rank() != 'B') and self._has_move(row, col, piece.get_team()):
            if (not (piece.get_team() in has_moveable_list)):
              has_moveable_list.append(piece.get_team())

    if (len(has_flag_list) == 1):
      return has_flag_list[0]
    else:
      return has_moveable_list[0]
