from board import Board
from board_configuration import BoardConfiguration
from bot import Bot
from abstract_game import AbstractGame
from message import Message
from constants import Constants
import random

"""
A class representing a game vs the computer
"""
class BotGame(AbstractGame):

 
  def __init__(self, player1_sid):
    super().__init__(player1_sid)
    self._name_to_config[Constants.PLAYER_TWO_NAME] = self._get_bot_config()
    self._bot = Bot()
    self._turn = Constants.PLAYER_ONE_NAME

  """
  Validate and perform a move from the player
  """
  def process_move(self, sid, coord_pair): 
    game_board = self._board
    messages = []

    if (self._board.validate_move(coord_pair[0], coord_pair[1],
      Constants.PLAYER_ONE_NAME)):
    
      combat_results = game_board.do_move(coord_pair[0], coord_pair[1])
      
      messages = self._results_to_messages(combat_results)
      self._turn = Constants.PLAYER_TWO_NAME
    else:
      messages = [Message(self._player1_sid, 'invalid move')]

    return messages

  """
  Generate and perform a move from the AI
  """
  def do_bot_move(self):
    game_board = self._board
    if (not game_board.has_win()):
      bot_move = self._bot.get_move(game_board)
      combat_results = game_board.do_move(bot_move[0], bot_move[1])
      self._turn = Constants.PLAYER_ONE_NAME
      return self._results_to_messages(combat_results)

  """
  Return the player that should move next
  """
  def get_turn(self):
    return self._turn
  
  """
  Select a random starting configuration for the AI
  """
  def _get_bot_config(self):
    config = Constants.BOT_CONFIGS[random.randrange(0, len(Constants.BOT_CONFIGS))]
    return BoardConfiguration(config)
