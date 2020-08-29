from aiohttp import web
from abstract_game import *
from bot_game import *
from pvp_game import *
import random, string
import socketio

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

async def index(request):
  with open('../index.html') as f:
    return web.Response(text=f.read(), content_type='text/html')

async def jquery(request):
  with open('../jquery-3.5.1.min.js') as f:
    return web.Response(text=f.read(), content_type='text/javascript')

async def js(request):
  with open('../script.js') as f:
    return web.Response(text=f.read(), content_type='text/javascript')

async def style(request):
  with open('../styles.css') as f:
    return web.Response(text=f.read(), content_type='text/css')

async def piece_img(request):
  with open('../images/{}.svg'.format(request.match_info['name'])) as f:
    return web.Response(text=f.read(), content_type='image/svg+xml')

async def handle_join(request):
  join_id = request.match_info['join_id']
  if join_id not in join_id_to_game:
    return web.Response(text='Error. Invalid or stale url', content_type='text/html')
  else:
    with open('../index.html') as f:
      return web.Response(text=f.read(), content_type='text/html')

sid_to_game = {}
join_id_to_game = {}
@sio.on('receive_move')
async def make_move(sid, string):
  global sid_to_game

  game = None if sid not in sid_to_game else sid_to_game[sid]
  if game is not None and not game.has_winner():
    coord_pair = game.get_coord_pair(string)
    all_messages = game.process_move(sid, coord_pair)

    player_messages = [x.message for x in all_messages if x.recipient_sid == sid] 
    player_json = game.get_board_json(sid, player_messages)
    await sio.emit('boardUpdate', player_json, sid)
    
    opponent_sid = game.get_opponent_sid(sid)
    if opponent_sid is not None:
      opponent_messages = [x.message for x in all_messages if x.recipient_sid != sid]
      opponent_json = game.get_board_json(opponent_sid, opponent_messages)
      await sio.emit('boardUpdate', opponent_json, opponent_sid)

    if game.has_winner():
      await sio.emit('gameOver')

@sio.on('receive_config')
async def receive_config(sid, string):
  game = None if sid not in sid_to_game else sid_to_game[sid]
  if game is not None:
    all_messages = game.set_board_config(sid, string)
    all_messages = [m for m in all_messages if m.recipient_sid is not None]
    for m in all_messages:
      await sio.emit('receiveChat', m.message, m.recipient_sid)
    if game.has_begun():
      json = game.get_board_json(sid, [])
      await sio.emit('boardUpdate', json, sid)
      opp_sid = game.get_opponent_sid(sid)
      if opp_sid is not None:
        json = game.get_board_json(opp_sid, [])
        await sio.emit('boardUpdate', json, opp_sid)

@sio.on('new_bot_game')
async def init_bot_game(sid):
  global sid_to_game
  sid_to_game[sid] = BotGame(sid)
  json = sid_to_game[sid].get_board_json(sid, ["Swap pieces then click the button to start the game"])

  await sio.emit('boardUpdate', json, sid)

def get_new_id():
  new_id = None
  while new_id is None or new_id in join_id_to_game:
    new_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(8))

  return new_id

@sio.on('new_pvp_game')
async def init_pvp_game(sid):
  global sid_to_game

  new_game = PvPGame(sid)
  sid_to_game[sid] = new_game
  
  join_id = get_new_id()
  join_id_to_game[join_id] = new_game

  join_url = '/join/' + join_id
  json = new_game.get_board_json(sid, ['Join url: ' + join_url, 'Swap pieces then click the button to ready up'])
  await sio.emit('boardUpdate', json, sid)

@sio.on('join')
async def join_pvp_game(sid, join_id):
  global sid_to_game

  if join_id not in join_id_to_game:
    await sio.emit('sendMessage', 'Error. Invalid or stale url', sid)
  else:
    game = join_id_to_game[join_id]
    del join_id_to_game[join_id]

    game.add_player2(sid)
    sid_to_game[sid] = game
    json = game.get_board_json(sid, ["Swap pieces then click the button to ready up"])
    await sio.emit('boardUpdate', json, sid)

@sio.on('rematch')
async def process_rematch_vote(sid):
  game = sid_to_game[sid]
  count = game.add_rematch_vote(sid)
  opp_sid = game.get_opponent_sid(sid)
  await sio.emit('rematchCount', count, sid)
  await sio.emit('rematchCount', count, opp_sid)
  if count == 2:
    new_game = PvPGame(sid)
    player1_json = new_game.get_board_json(sid, ["Swap pieces then click the button to ready up"])
    new_game.add_player2(opp_sid)
    player2_json = new_game.get_board_json(opp_sid, ["Swap pieces then click the button to ready up"])
    sid_to_game[sid] = new_game
    sid_to_game[opp_sid] = new_game
    await sio.emit('resetGui', sid)
    await sio.emit('resetGui', opp_sid)
    await sio.emit('boardUpdate', player1_json, sid)
    await sio.emit('boardUpdate', player2_json, opp_sid)

@sio.on('do_bot_move')
async def do_bot_move(sid):
  game = sid_to_game[sid]
  if isinstance(game, BotGame) and not game.has_winner() and game.get_turn() == Constants.PLAYER_TWO_NAME:
    messages = game.do_bot_move()
    messages = [x.message for x in messages if x.recipient_sid == sid]
    json = game.get_board_json(sid, messages)
    await sio.emit('boardUpdate', json, sid)

@sio.on('receive_msg')
async def receive_msg(sid, msg):
  game = sid_to_game[sid]
  opp_sid = game.get_opponent_sid(sid)
  if opp_sid is not None:
    await sio.emit('receiveChat', msg, opp_sid)

@sio.on('disconnect')
async def disconnect(sid):
  if sid in sid_to_game:
    game = sid_to_game[sid]
    opp_sid = game.get_opponent_sid(sid)
    if opp_sid is not None:
      await sio.emit('receiveChat', 'opponent disconnected')

    del sid_to_game[sid]
 
app.router.add_get('/', index)
app.router.add_get('/jquery-3.5.1.min.js', jquery)
app.router.add_get('/script.js', js)
app.router.add_get('/styles.css', style)
app.router.add_get('/{name:[1-9]|S|F|B}.svg', piece_img)
app.router.add_get('/join/{join_id}', handle_join)

if __name__ == '__main__':
  web.run_app(app)
