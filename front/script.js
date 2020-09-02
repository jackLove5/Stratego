let gameBoard = {};

function initBoard() {
  for (let i = 0; i < gameBoard.size; i++) {
    gameBoard.pieces[i] = new Array(gameBoard.size);
    for (let j = 0; j < gameBoard.size; j++) {
      gameBoard.pieces[i][j] = {rank: 1, team: "Blue"};
    }
  }
}

function initSquares() {
  for (let row = 0; row < gameBoard.size; row++) {
    for (let col = 0; col < gameBoard.size; col++) {
      let obj = gameBoard.pieces[row][col];
      let divStr = `<div class="square row${row} col${col} ${obj.team}">${obj.rank}</div>`
      $("#board").append(divStr);
    }
  }
}

function updateSquares() {
  for (let row = 0; row < gameBoard.size; row++) {
    for (let col = 0; col < gameBoard.size; col++) {
      let obj = gameBoard.pieces[row][col];
 
      $(".row" + row).filter(".col" + col).html('');
      $(".row" + row).filter(".col" + col).text('');
      $(".row" + row).filter(".col" + col).removeClass(['Red', 'Blue', 'None']);

      if (obj.rank === "~") {
        $(".row" + row).filter(".col" + col).addClass('lake');
      } else {

        $(".row" + row).filter(".col" + col).addClass(obj.team);
        if (obj.team === "Blue") {
          let width = $(".row" + row).filter(".col" + col).width();
          let height = $(".row" + row).filter(".col" + col).height();
          let html = `<img src="/images/${obj.rank}.svg" width="${width}" height="${height}">`;
          html += '<div class="rank-display">';
          if (obj.rank !== 'B' && obj.rank !== 'F') {
            html += obj.rank;
          }

          html += '</div>';
          $(".row" + row).filter(".col" + col).html(html);
        }
        else
        {
          let rankText = obj.rank === 'None' ? '' : obj.rank;
          $(".row" + row).filter(".col" + col).text(rankText);
        }
      }
    }
  }
}

function sendMove(src, dst) {
  let boardStr = `${src.row}${src.col}${dst.row}${dst.col}`
  socket.emit("receive_move", boardStr);
}

function startGame() {
  let board_config = getBoardConfig();
  socket.emit("receive_config", board_config);
  $('#start-button').hide();
  gameBoard.inSetup = false;
}

function sendChat() {
  let msg = $('#message-text').val();
  $('#message-text').val('');
  if (msg === '') {
    return;
  }

  let msgDiv = `<div class="message-item chat-item"><strong class="you-msg">You: </strong>${msg}</div>`;
  $('#message-box').append(msgDiv);
  $('#message-box').scrollTop($('#message-box')[0].scrollHeight);
  socket.emit('receive_chat', msg);
}

function setDivHeights() {
  let boardWidth = $('#board').width();

  $('#board').css({
    'height': boardWidth + 'px'
  });

  $('#chat').css({
    'height': boardWidth + 'px'
  });
}

function centerSquareText() {
  let squareHeight = $('.square').height();
  let squareWidth = $('.square').width();
  
  $('.square').css({
    'line-height': squareHeight + 'px'
  });
  
  $('img').css({
    'height': squareHeight,
    'width': squareWidth
  });
}


function initGame() {
  gameBoard.size = 10;
  gameBoard.pieces = new Array(gameBoard.size);
  gameBoard.selected = {};
  gameBoard.gameOver = false;
  gameBoard.inSetup = true;
  $('#start-button').off('click').click(startGame);
  $('#start-button').text('Start game');
  $('#start-button').show();

  $('#board').empty();
  $('#message-box').empty();
  initBoard();
  initSquares();
  centerSquareText();
}

const socket = io();

socket.on("boardUpdate", function(data) {
  let obj = JSON.parse(data);
  gameBoard.pieces = obj.board;
  gameBoard.turn = obj.turn;
  updateSquares();

  let messages = obj.messages;
  for (let i = 0; i < messages.length; i++) {
    let msgDiv = `<div class="message-item"><i>${messages[i]}</i></div>`;
    $('#message-box').append(msgDiv);
    $('#message-box').scrollTop($('#message-box')[0].scrollHeight);
  }
});

socket.on('receiveMessage', function(msgText) { 
  let msgDiv = `<div class="message-item"><i>${msgText}</i></div>`;
  $('#message-box').append(msgDiv);
  $('#message-box').scrollTop($('#message-box')[0].scrollHeight);
});

socket.on('receiveChat', function(msg) {
  let msgDiv = `<div class="message-item chat-item"><strong class="opp-msg">Opponent: </strong>${msg}</div>`;
  $('#message-box').append(msgDiv);
  $('#message-box').scrollTop($('#message-box')[0].scrollHeight);
});

socket.on("gameOver", function() {
  gameBoard.gameOver = true;
  if (gameBoard.type === "BOT") {
    $('#message-box').append(`<div class="message-item"><i>Click the button to play again</i></div>`);
    $('#message-box').scrollTop($('#message-box')[0].scrollHeight);
    $('#start-button').text('New game');
    $('#start-button').off('click').click(() => newGame('BOT'));
    $('#start-button').show();
  }
  else {
    $('#start-button').text('Rematch? (0/2)');
    $('#start-button').off('click').click(() => socket.emit('rematch'));
    $('#start-button').show();
  }
});

socket.on('rematchCount', function(rematchCount) {
  $('#start-button').text(`Rematch? (${rematchCount}/2)`);
});

socket.on('resetGui', initGame);

window.addEventListener('resize', function() {
  setDivHeights();
  centerSquareText();
});

$(document).keyup(function(e) {
  if ($('#message-text').is(':focus') && $('#message-text').val !== ''
    && e.key == 'Enter') {
    sendChat();
  }
});

$(document).on('click', '.square', function(e) {
  if (gameBoard.gameOver || (gameBoard.turn != 'Blue' && !gameBoard.inSetup)) {
    return;
  }

  let target = e.target;
  if (target.nodeName.toLowerCase() == 'img' || $(target).hasClass('rank-display')) {
    target = $(target).parent();
  }

  let classList = $(target).attr('class').split(/\s+/);
  let row = classList.filter((x) => x.search('row') !== -1)[0][3];
  let col = classList.filter((x) => x.search('col') !== -1)[0][3];

  let squareObj = gameBoard.pieces[row][col];
  if (!gameBoard.inSetup && (squareObj.rank === 'F' || squareObj.rank === 'B')) {
    return;
  }

  if (jQuery.isEmptyObject(gameBoard.selected)) {
    if (squareObj.team === 'Blue'){
      $(target).addClass('select');
      gameBoard.selected = {row: row, col: col};
    }
  }
  else {
    let dst = {row: row, col: col};
    $('.square').each(function(index) {
      $(this).removeClass('select');
    });

    if (gameBoard.inSetup && squareObj.team === 'Blue') {
      let srcRow = gameBoard.selected.row;
      let srcCol = gameBoard.selected.col;
      let dstRow = dst.row;
      let dstCol = dst.col;

      let tmp = gameBoard.pieces[srcRow][srcCol];
      gameBoard.pieces[srcRow][srcCol] = gameBoard.pieces[dstRow][dstCol];
      gameBoard.pieces[dstRow][dstCol] = tmp;
      updateSquares();
    }
    else if (!gameBoard.inSetup){
      sendMove(gameBoard.selected, dst);
      if (gameBoard.type === 'BOT') {
        socket.emit('do_bot_move');
      }
    }

    gameBoard.selected = {};
  }
});

function getBoardConfig() {
  let ret = '';
  gameBoard.pieces.forEach((row) => row.forEach(piece => 
    ret += piece.team === 'Blue' ? piece.rank : ''));

  return ret;
}

function newGame(type) {
  initGame();
  gameBoard.type = type;

  $('#new-bot-game').hide();
  $('#new-pvp-game').hide();
  $('#start-button').show();
  $('#message-text').show();
  $('#send-button').show();

  let funcName = type === 'PVP' ? 'new_pvp_game' : 'new_bot_game';
  socket.emit(funcName);
}

window.onload = function() {
  setDivHeights();
  $('#start-button').hide();
  $('#message-text').hide();
  $('#send-button').hide();

  let pathname = window.location.pathname;
  if (pathname.indexOf('join') !== -1) {
    let id = pathname.substr(pathname.indexOf('join') + 'join/'.length);
    initGame();
    $('#new-bot-game').hide();
    $('#new-pvp-game').hide();
    $('#start-button').show();
    $('#message-text').show();
    $('#send-button').show();
    socket.emit('join', id);
  }
};
