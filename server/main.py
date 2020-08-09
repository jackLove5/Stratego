from aiohttp import web
from game import *
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

sid_to_game = {}

# front end emits "message" event
@sio.on('receive_move')
async def make_move(sid, string):
  global sid_to_game

  game = None if sid not in sid_to_game else sid_to_game[sid]
  if game is not None and not game.has_winner():
    coord_pair = game.get_coord_pair(string)
    board_state = game.process_move(coord_pair)

    await sio.emit('boardUpdate', board_state, sid)
    if game.has_winner():
      await sio.emit('gameOver')

@sio.on('start_game')
async def start_game(sid):
  game = None if sid not in sid_to_game else sid_to_game[sid]
  if game is not None:
    game.begin_play()

@sio.on('connection')
async def init_game(sid):
  global sid_to_game

  sid_to_game[sid] = Game()
  board_state = sid_to_game[sid].get_board_state()

  await sio.emit('boardUpdate', board_state, sid)

@sio.on('receive_msg')
async def receive_msg(sid, msg):
  pass

app.router.add_get('/', index)
app.router.add_get('/jquery-3.5.1.min.js', jquery)
app.router.add_get('/script.js', js)
app.router.add_get('/styles.css', style)

if __name__ == '__main__':
  web.run_app(app)
