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

swapping = False
initialized = False
winner = False
game = None

# front end emits "message" event
@sio.on('receive_move')
async def make_move(sid, str):
  global initialized
  global swapping
  global winner
  global game

  print('received move ' + str)
  if initialized and not winner:
    coord_pair = Game.get_coord_pair(str)
    board_state = game.process_move(coord_pair, swapping)
    if (game.has_winner()):
      winner = True

    await sio.emit('boardUpdate', board_state)
    print('emmited board')

@sio.on('start_game')
async def start_game(sid):
  global swapping
  print('starting game')
  swapping = False

@sio.on('connection')
async def init_game(sid):
  global initialized
  global swapping
  global winner
  global game

  print('connection from ' + sid)
  game = Game()
  board_state = game.get_board_state()

  await sio.emit('boardUpdate', board_state)

  initialized = True
  swapping = True
  winner = False

app.router.add_get('/', index)
app.router.add_get('/jquery-3.5.1.min.js', jquery)
app.router.add_get('/script.js', js)
app.router.add_get('/styles.css', style)

if __name__ == '__main__':
  web.run_app(app)
