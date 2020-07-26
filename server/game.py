# Implements the Stratego game
from board import *
from board_configuration import *
from bot import *


class Game:
  """
  Extract coordinate pair from raw string
  return empty list if invalid input
  """
  def get_coord_pair(string):
    string = "".join(string.split())
    string = string.upper()
    if (len(string) != 4):
      return []

    src_pos = [ord(string[0]) - ord('0'), ord(string[1]) - ord('0')]
    dst_pos = [ord(string[2]) - ord('0'), ord(string[3]) - ord('0')]
    ret = [src_pos, dst_pos]

    for p in ret:
      for i in range(len(p)):
        if p[i] > 9 or p[i] < 0:
          return []

    return ret

  def __init__(self):
    self._bot = Bot()
    bot_config = "15689599957933297BB6494S56B76948887BFBB8"
    player_config = "FS99999999888887777666655554443321BBBBBB"

    bot_setup = BoardConfiguration(bot_config)
    player_setup = BoardConfiguration(player_config)

    self._game_board = Board(bot_setup, player_setup)

    self._game_board_state = self._game_board.to_json("blue", "swap pieces")

  def get_board_state(self):
    return self._game_board_state

  def process_move(self, coord_pair, setup_state):
    game_board = self._game_board
    message = ""
    if (setup_state):
      print('processing swap in game.py')
    
      if (coord_pair != [] and game_board.has_player_piece(coord_pair[0]) 
        and game_board.has_player_piece(coord_pair[1])):
   
        game_board.swap_pieces(coord_pair[0], coord_pair[1])
      else:
        message = "invalid swap"

    elif (game_board.validate_move(coord_pair[0], coord_pair[1],
      Constants.PLAYER_NAME)):
    
      move_res = game_board.do_move(coord_pair[0], coord_pair[1])
      message = move_res
    
      if (not game_board.has_win()):
        bot_move = self._bot.get_move(game_board)
        moveRes = game_board.do_move(bot_move[0], bot_move[1])
        message = message + "\\n" + move_res 
    else:
      message = "invalid move"

    print('drawing board')
    game_board.draw()
    self._game_board_state = game_board.to_json('blue', message)
    return self._game_board_state

  def has_winner(self):
    return self._game_board.has_win()
