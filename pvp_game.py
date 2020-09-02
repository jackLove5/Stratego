from board import Board
from board_configuration import BoardConfiguration
from abstract_game import AbstractGame
from message import Message
from constants import Constants

"""
A class representing a Player vs Player game
"""
class PvPGame(AbstractGame):
 
  def __init__(self, player1_sid):
    super().__init__(player1_sid)
    self._turn = "None"
    self._rematch_votes = []
    self._join_id = None

  """
  Validate and process a move from one of the players
  """
  def process_move(self, sid, coord_pair):
    messages = []
    name = self._sid_to_name[sid]
    num_ready = len([x for x in self._name_to_config.values() if x is not None])
    if num_ready != len(self._name_to_config):
      return [Message(sid, 'Error. At least one player not ready')]

    if self._turn != name:
      return [Message(sid, 'Error. Not your turn')]
    
    if name == Constants.PLAYER_TWO_NAME:
      self._board._flip()
          
    if self._board.validate_move(coord_pair[0], coord_pair[1], name):
      combat_results = self._board.do_move(coord_pair[0], coord_pair[1])
      messages = self._results_to_messages(combat_results)  
      
      if self._turn == Constants.PLAYER_ONE_NAME:
        self._turn = Constants.PLAYER_TWO_NAME
      else:
        self._turn = Constants.PLAYER_ONE_NAME
     
    else:
      messages = [Message(sid, 'invalid move')]
    
    if name == Constants.PLAYER_TWO_NAME:
      self._board._flip()

    return messages

  """
  Given a second player's sid, add them to the game
  """
  def add_player2(self, sid):
    self._player2_sid = sid
    self._sid_to_name[sid] = Constants.PLAYER_TWO_NAME
    self._name_to_sid[Constants.PLAYER_TWO_NAME] = sid
 
  """
  Process a vote for a rematch from one of the players
  Return the number of players who voted for a rematch
  """ 
  def add_rematch_vote(self, sid):
    if sid not in self._rematch_votes:
      self._rematch_votes.append(sid)

    return len(self._rematch_votes)

  """
  Set the game's join id
  """
  def set_join_id(self, id):
    self._join_id = id

  """
  Get the game's join id
  """
  def get_join_id(self):
    return self._join_id
