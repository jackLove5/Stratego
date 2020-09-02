from constants import Constants
from board_configuration import BoardConfiguration
from board import Board
from message import Message

"""
An "abstract" class representing a game of Stratego.
Subclasses should provide a method to process moves
"""
class AbstractGame:
  
  """
  Extract coordinate pair from raw string.
  Return empty list if invalid input
  """
  def get_coord_pair(self, string):
    string = "".join(string.split())
    string = string.upper()
    if len(string) != 4:
      return []

    src_pos = [ord(string[0]) - ord('0'), ord(string[1]) - ord('0')]
    dst_pos = [ord(string[2]) - ord('0'), ord(string[3]) - ord('0')]
    ret = [src_pos, dst_pos]

    if any(x < 0 or x >= 10 for x in src_pos + dst_pos):
      return []

    return ret

  def __init__(self, player1_sid):
    self._player1_sid = player1_sid
    self._player2_sid = None

    self._sid_to_name = {player1_sid: Constants.PLAYER_ONE_NAME}
    self._name_to_sid = {Constants.PLAYER_ONE_NAME: player1_sid, Constants.PLAYER_TWO_NAME: None}
    self._name_to_config = {Constants.PLAYER_ONE_NAME: None, Constants.PLAYER_TWO_NAME: None}
    player2_setup = BoardConfiguration(Constants.DEFAULT_CONFIG)
    player1_setup = BoardConfiguration(Constants.DEFAULT_CONFIG)

    self._board = Board(player1_setup, player2_setup)
    self._started = False
    self._completed = False
  
  """
  Given a player's socket id, return the other player's socket id
  """
  def get_opponent_sid(self, sid):
    return self._player2_sid if sid == self._player1_sid else self._player1_sid

  """
  Project a list of pairs representing combat results into messages
  Input: list of pairs [dead_piece, attacking_piece]
  """
  def _results_to_messages(self, combat_results):
    messages = []
    for result in combat_results:
      lose_piece = result[0]
      win_piece = result[1]

      win_full_name = win_piece.get_name() + ' (' + win_piece.get_rank() + ')'
      lose_full_name = lose_piece.get_name() + ' (' + lose_piece.get_rank() + ')'

      win_sid = self._name_to_sid[win_piece.get_team()]
      lose_sid = self._name_to_sid[lose_piece.get_team()]

      if win_sid is not None:
        messages.append(Message(win_sid, 'Your ' + win_full_name + 
          " captured opponent's " + lose_full_name))

      if lose_sid is not None:
        messages.append(Message(lose_sid, 'Your ' + lose_full_name + 
          " was captured by opponent's " + win_full_name))

    return messages

  """
  Serialize the board given the requesting player and a
  list of messages from the move that got executed
  """
  def get_board_json(self, player_sid, message_list):
    player_name = self._sid_to_name[player_sid]
    return self._board.to_json(player_name, message_list, self._turn)

  """
  Verify the user's starting configuration, and either start the game
  or continue waiting for players to submit their starting configuration
  """
  def set_board_config(self, sid, config_str):
    name = self._sid_to_name[sid]
    
    try:
      self._name_to_config[name] = BoardConfiguration(config_str)
    except ValueError:
      self._name_to_config[name] = None
      return [Message(sid, 'ERROR: Invalid configuration')]
   
    messages = []
    num_ready = len([x for x in self._name_to_config.values() if x is not None])

    if num_ready == len(self._name_to_config):
      self._begin_play()
      messages.append(Message(self._player1_sid, 'Game started'))
      messages.append(Message(self._player1_sid, 'Your turn'))
      messages.append(Message(self._player2_sid, 'Game started'))
      messages.append(Message(self._player2_sid, "Opponent's turn"))
    else:
      opponent_sid = self.get_opponent_sid(sid)
      messages.append(Message(sid, 'Pieces set. Waiting for opponent...'))
      messages.append(Message(opponent_sid, 'Opponent is ready'))

    return messages

  """
  Start the game
  """
  def _begin_play(self):
    player1_config = self._name_to_config[Constants.PLAYER_ONE_NAME]
    player2_config = self._name_to_config[Constants.PLAYER_TWO_NAME]
    self._board = Board(player1_config, player2_config)
    self._turn = Constants.PLAYER_ONE_NAME
    self._started = True

  def has_begun(self):
    return self._started

  """
  Check if the game is in a completed state
  """
  def has_winner(self):
    if (self._completed):
      return True
    else:
      self._completed = self._board.has_win()
      return self._completed
