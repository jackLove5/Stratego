from flask import Flask, Response, request
from flask_socketio import SocketIO
from markupsafe import escape
from abstract_game import *
from bot_game import *
from pvp_game import *
import random, string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'changeme'
sio = SocketIO(app)

sid_to_game = {}
join_id_to_game = {}
@sio.on('receive_move')
def make_move(string):
  global sid_to_game
  sid = request.sid

  game = None if sid not in sid_to_game else sid_to_game[sid]
  if game is not None and not game.has_winner():
    coord_pair = game.get_coord_pair(string)
    all_messages = game.process_move(sid, coord_pair)

    player_messages = [x.message for x in all_messages if x.recipient_sid == sid] 
    player_json = game.get_board_json(sid, player_messages)
    sio.emit('boardUpdate', player_json, room=sid)
    
    opponent_sid = game.get_opponent_sid(sid)
    if opponent_sid is not None:
      opponent_messages = [x.message for x in all_messages if x.recipient_sid != sid]
      opponent_json = game.get_board_json(opponent_sid, opponent_messages)
      sio.emit('boardUpdate', opponent_json, room=opponent_sid)

    if game.has_winner():
      sio.emit('gameOver', room=sid)
      if opponent_sid is not None:
        sio.emit('gameOver', room=opponent_sid)

@sio.on('receive_config')
def receive_config(string):
  sid = request.sid
  game = None if sid not in sid_to_game else sid_to_game[sid]
  if game is not None:
    all_messages = game.set_board_config(sid, string)
    all_messages = [m for m in all_messages if m.recipient_sid is not None]
    for m in all_messages:
      sio.emit('receiveMessage', m.message, room=m.recipient_sid)
    if game.has_begun():
      json = game.get_board_json(sid, [])
      sio.emit('boardUpdate', json, room=sid)
      opp_sid = game.get_opponent_sid(sid)
      if opp_sid is not None:
        json = game.get_board_json(opp_sid, [])
        sio.emit('boardUpdate', json, room=opp_sid)

@sio.on('new_bot_game')
def init_bot_game():
  sid = request.sid
  global sid_to_game
  sid_to_game[sid] = BotGame(sid)
  json = sid_to_game[sid].get_board_json(sid, ["Swap pieces then click the button to start the game"])

  sio.emit('boardUpdate', json, room=sid)

def get_new_id():
  new_id = None
  while new_id is None or new_id in join_id_to_game:
    new_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(8))

  return new_id

@sio.on('new_pvp_game')
def init_pvp_game():
  global sid_to_game
  sid = request.sid

  new_game = PvPGame(sid)
  sid_to_game[sid] = new_game
  
  join_id = get_new_id()
  join_id_to_game[join_id] = new_game

  join_url = '/join/' + join_id
  json = new_game.get_board_json(sid, ['Join url: ' + join_url, 'Swap pieces then click the button to ready up'])
  sio.emit('boardUpdate', json, room=sid)

@sio.on('join')
def join_pvp_game(join_id):
  global sid_to_game
  sid = request.sid

  if join_id not in join_id_to_game:
    sio.emit('receiveMessage', 'Error. Invalid or stale url', room=sid)
  else:
    game = join_id_to_game[join_id]
    del join_id_to_game[join_id]

    game.add_player2(sid)
    sid_to_game[sid] = game
    json = game.get_board_json(sid, ["Swap pieces then click the button to ready up"])
    sio.emit('boardUpdate', json, room=sid)

    opp_sid = game.get_opponent_sid(sid)
    sio.emit('receiveMessage', 'Opponent connected', room=opp_sid)

@sio.on('rematch')
def process_rematch_vote():
  sid = request.sid

  game = sid_to_game[sid]
  count = game.add_rematch_vote(sid)
  opp_sid = game.get_opponent_sid(sid)
  sio.emit('rematchCount', count, room=sid)
  sio.emit('rematchCount', count, room=opp_sid)
  if count == 2:
    new_game = PvPGame(sid)
    player1_json = new_game.get_board_json(sid, ["Swap pieces then click the button to ready up"])
    new_game.add_player2(opp_sid)
    player2_json = new_game.get_board_json(opp_sid, ["Swap pieces then click the button to ready up"])
    sid_to_game[sid] = new_game
    sid_to_game[opp_sid] = new_game
    sio.emit('resetGui', room=sid)
    sio.emit('resetGui', room=opp_sid)
    sio.emit('boardUpdate', player1_json, room=sid)
    sio.emit('boardUpdate', player2_json, room=opp_sid)

@sio.on('do_bot_move')
def do_bot_move():
  sid = request.sid
  game = sid_to_game[sid]
  if isinstance(game, BotGame) and not game.has_winner() and game.get_turn() == Constants.PLAYER_TWO_NAME:
    messages = game.do_bot_move()
    messages = [x.message for x in messages if x.recipient_sid == sid]
    json = game.get_board_json(sid, messages)
    sio.emit('boardUpdate', json, room=sid)
    
    if game.has_winner():
      sio.emit('gameOver', room=sid)

@sio.on('receive_chat')
def receive_chat(msg):
  sid = request.sid
  game = sid_to_game[sid]
  opp_sid = game.get_opponent_sid(sid)
  if opp_sid is not None:
    sio.emit('receiveChat', msg, room=opp_sid)

@sio.on('disconnect')
def disconnect():
  sid = request.sid
  if sid in sid_to_game:
    game = sid_to_game[sid]
    opp_sid = game.get_opponent_sid(sid)
    if opp_sid is not None:
      sio.emit('receiveMessage', 'opponent disconnected', room=opp_sid)

    del sid_to_game[sid]

@app.route('/')
def index():
  with open('front/index.html') as f:
    return Response(response=f.read(), mimetype='text/html')

@app.route('/script.js')
def script():
  with open('front/script.js') as f:
    return Response(response=f.read(), mimetype='text/javascript')

@app.route('/jquery-3.5.1.min.js')
def jquery():
  with open('front/jquery-3.5.1.min.js') as f:
    return Response(response=f.read(), mimetype='text/javascript')

@app.route('/styles.css')
def style():
  with open('front/styles.css') as f:
    return Response(response=f.read(), mimetype='text/css')

@app.route('/images/<filename>')
def image(filename):
  with open('front/images/{}'.format(escape(filename))) as f:
    return Response(response=f.read(), mimetype='image/svg+xml')

@app.route('/join/<join_id>')
def handle_join(join_id):
  if join_id not in join_id_to_game:
    return Response(response='Error. Invalid or stale url', mimetype='text/html')
  else:
    with open('front/index.html') as f:
      return Response(response=f.read(), mimetype='text/html')

if __name__ == '__main__':
  sio.run(app)
