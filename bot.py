from random import randrange
from copy import deepcopy
from pieces import *

"""
AI class. "get_move" is the only public method
"""
class Bot(object):
  MAX_DEPTH = 2
  INF = 100000000000000
  BOT_NAME = Constants.PLAYER_TWO_NAME
  PLAYER_NAME = Constants.PLAYER_ONE_NAME

  def __init__(self):
    pass

  """
  Generate all possible moves for a given player (including invalid moves)
  """
  def _generate_actions(self, board, team_name):
    board = board._board
    res = []
    for i in range(len(board)):
      for j in range(len(board[i])):
        if (not (board[i][j] is None)):
          if (board[i][j].get_team() == team_name):
            for k in range(len(board)):
              res.append([[i,j],[k,j]])
              res.append([[i,j],[i,k]])
    return res
  
  """
  Given a piece "src_piece", return the "worst case scenario" piece that
  src_piece could face in combat
  """
  def _best_possible_piece(self, src_piece, dst_piece, board):
    prob_dist = self._get_prob_dist(dst_piece, board)

    # Bomb is the worst opponent a piece could face unless it's a miner
    if src_piece.get_rank() != '8' and ('B' in prob_dist and prob_dist['B'] > 0.0):
      return Piece('B', dst_piece.get_team())

    # Marshall is the worst opponent a piece could face unless it's a spy
    if src_piece.get_rank() != 'S' and ('1' in prob_dist and prob_dist['1'] > 0.0):
      return MoveablePiece('1', dst_piece.get_team())

    # check all other ranks in order
    for rank in Constants.RANKS:
      if (rank in prob_dist and prob_dist[rank] > 0.0):
        if (rank == 'S'):
          return Spy(dst_piece.get_team())
        elif (rank == '8'):
          return Miner(dst_piece.get_team())
        elif (rank.isdigit()):
          return MoveablePiece(rank, dst_piece.get_team())
        else:
          return Piece(rank, dst_piece.get_team())

  """
  Return a dictionary mapping ranks to the number of pieces of a particular
  team w/ the rank, the number of visible pieces,
  and the number of pieces that have moved
  """
  def _get_piece_count(self, board, team_name):
    board = board._board
    counts = {}
    for rank in Constants.RANKS:
      counts[rank] = 0

    visible_piece_count = 0
    moved_piece_count = 0
    for row in board:
      for piece in row:
        if (piece is not None):
          if (piece.get_team() == team_name):

            counts[piece.get_rank()] += 1 

            if (piece.is_visible()):
              visible_piece_count += 1
    
    return [counts, visible_piece_count]

  """
  returns dictionary mapping rank to the probability that the specified
  piece is the rank
  """
  def _get_prob_dist(self, dst_piece, board):
    board = board._board

    counts = {}
    for rank in Constants.RANKS:
      counts[rank] = 0

    moveable_count = 0
    moved_count = 0
    piece_count = 0
    for row in board:
      for piece in row:
        if ((piece is not None) and (piece.get_team() == dst_piece.get_team())
          and not piece.is_visible()):
         
          counts[piece.get_rank()] += 1
          
          if (piece.get_rank() != 'F' and piece.get_rank() != 'B'):
            moveable_count += 1
        
          if piece.has_moved():
            moved_count += 1
          
          piece_count += 1
   
    # calculate probabilities 
    ret = {}
    if (dst_piece.has_moved()):
       for rank in counts:
         if (dst_piece.is_known_scout()):
           # Piece previously moved more than one square; we know it's a scout
           if (rank == '9'):
             ret[rank] = 1.0
           else:
             ret[rank] = 0.0
         elif (rank == 'F' or rank == 'B'):
           # If the piece has moved, it can't be a flag or bomb
           ret[rank] = 0.0
         else:
           ret[rank] = (0.0 if counts[rank] == 0 else float(counts[rank])
            / float(moveable_count))
    else:
      if (piece_count - moved_count == 1):
        # All other pieces have moved. Must be flag
        for rank in counts:
          if (rank == 'F'):
            ret[rank] = 1.0
          else:
            ret[rank] = 0.0
      else:
        for rank in counts:
          # Piece hasn't moved. Could be moveable or not
          ret[rank] = (0.0 if counts[rank] == 0 else float(counts[rank]) 
            / float(piece_count))

    return ret

  """
  Return the resulting board after executing a given action
  """ 
  def _result(self, board, action):
    board_cpy = deepcopy(board)

    dst_piece = board_cpy._board[action[1][0]][action[1][1]]
    src_piece = board_cpy._board[action[0][0]][action[0][1]]

    """
    If the destination space is empty or contains a known enemy piece,
    or we can statistically determine that we would win in combat, perform
    the move like normal. Otherwise, assume src_piece gets defeated in combat
    """
    if (dst_piece is None or dst_piece.is_visible()):
      board_cpy.do_move(action[0], action[1])
    else:
      best_enemy_piece = self._best_possible_piece(src_piece, dst_piece, board)

      if (src_piece.combat(best_enemy_piece) >= 0):
        # We know we will defeat dstPiece in combat (or tie)
        board_cpy.do_move(action[0], action[1])
      else:
        # We don't know if we'll defeat dstPiece in combat. Assume that we lose
        board_cpy._board[action[0][0]][action[0][1]] = None

    return board_cpy

  """
  Return the best action for a particular board state
  """ 
  def get_move(self, board):

     alpha = -Bot.INF
     beta = Bot.INF

     v = self._max_value(board, alpha, beta, 0)
     return v[1] 

  def _utility(self, board):
    return (self._calculate_board_score(board, Bot.BOT_NAME)
      - self._calculate_board_score(board, Bot.PLAYER_NAME))
 
  def _calculate_board_score(self, board, team):

    piece_count = self._get_piece_count(board, team)[0]
    piece_value_sum = 0

    for rank in piece_count:
      if rank == 'F':
        piece_value_sum += 10000
      elif rank == 'B':
        piece_value_sum += 5 * piece_count[rank]
      elif rank == 'S':
        piece_value_sum += 4.5
      elif rank == '8':
        piece_value_sum += 3 * piece_count[rank]
      else:
        piece_value_sum += ((10 - (ord(rank) - ord('0'))) 
          / float(Constants.VALID_PIECE_COUNTS[rank]) * float(piece_count[rank]))

    return piece_value_sum
     
  def _evaluate(self, board):
    return self._utility(board)

  def _terminal(self, board):
    return board.has_win()

  def _max_value(self, board, alpha, beta, depth):
    if (depth == Bot.MAX_DEPTH or self._terminal(board)):
      return [self._evaluate(board), None]

    v = -Bot.INF
    actions = self._generate_actions(board, Bot.BOT_NAME)
    best_action = None
    for a in actions:
      if (board.validate_move(a[0], a[1], Bot.BOT_NAME)):
        new_v = self._min_value(self._result(board, a), alpha, beta, depth + 1)
        if (new_v[0] > v):
          v = new_v[0]
          best_action = a
        elif new_v[0] == v and randrange(0, 2) == 0:
          best_action = a

                      
        if (v >= beta):
          return [v, best_action]
        alpha = max(alpha, v)

    return [v, best_action]

  def _min_value(self, board, alpha, beta, depth):
    if (depth == Bot.MAX_DEPTH or self._terminal(board)):
      return [self._evaluate(board), None]
      
    v = Bot.INF
    actions = self._generate_actions(board, Bot.PLAYER_NAME)
    best_action = None
    for a in actions:
      if (board.validate_move(a[0], a[1], Bot.PLAYER_NAME)):  
        new_v = self._max_value(self._result(board, a), alpha, beta, depth + 1)
        if (new_v[0] < v):
          v = new_v[0]
          best_action = a
 
        if (v <= alpha):
          return [v, best_action]
        beta = min(beta, v)

    return [v, best_action]
