
var gameBoard = {};

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
      let displayText = ('rank' in obj) ? obj.rank : '';
      let color = ('team' in obj) ? obj.team : '';
      let divStr = `<div class="square row${row} col${col} ${color}">${displayText}</div>`
      $("#board").append(divStr);
    }
  }
}

function updateSquares() {
  for (let row = 0; row < gameBoard.size; row++) {
    for (let col = 0; col < gameBoard.size; col++) {
      let obj = gameBoard.pieces[row][col];
      let rankText = '';
      if ('rank' in obj && obj.rank !== 'None') {
        rankText = obj.rank;
      }
      
      let color = ('team' in obj) ? obj.team : '';
    
      $(".row" + row).filter(".col" + col).html('');
      $(".row" + row).filter(".col" + col).text('');
      $(".row" + row).filter(".col" + col).removeClass(['Red', 'Blue', 'None']);

      if (rankText === "~") {
        $(".row" + row).filter(".col" + col).addClass('lake');
      } else {

        $(".row" + row).filter(".col" + col).addClass(color);
        if (color === "Blue") {
          var width = $(".row" + row).filter(".col" + col).width();
          var height = $(".row" + row).filter(".col" + col).height();
          var html = '<img src="/' + rankText + '.svg" width="' + width + '" height="' + height + '">';
          html = html + '<div class="rank-display">';
          if (rankText !== 'B' && rankText !== 'F') {
            html = html + rankText;
          }

          html = html + '</div>';
          $(".row" + row).filter(".col" + col).html(html);
        }
        else
        {
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

  var msg = $('#message-text').val();
  $('#message-text').val('');
  if (msg === '') {
    return;
  }

  var msgDiv = '<div class="message-item chat-item"><strong class="you-msg">You: </strong>' + msg + '</div>';
  $('#message-box').append(msgDiv);
  $('#message-box').scrollTop($('#message-box')[0].scrollHeight);
  socket.emit('receive_chat', msg);
}

function setDivHeights() {
  var boardWidth = $('#board').width();

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

const socket = io("http://localhost:8080");

socket.on("boardUpdate", function(data) {
  var obj = JSON.parse(data);
  gameBoard.pieces = obj.board;
  gameBoard.turn = obj.turn;
  updateSquares();

  var messages = obj.messages;
  for (var i = 0; i < messages.length; i++) {
    var msgDiv = '<div class="message-item"><i>' + messages[i] + '</i></div>';
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
  let msgDiv = '<div class="message-item chat-item"><strong class="opp-msg">Opponent: </strong>' + msg + '</div>';
  $('#message-box').append(msgDiv);
  $('#message-box').scrollTop($('#message-box')[0].scrollHeight);
});

socket.on("gameOver", function() {
  gameBoard.gameOver = true;
  if (gameBoard.type === "BOT") {
    $('#message-box').append(`<div class="message-item"><i>Click the button to play again</i></div>`);
    $('#message-box').scrollTop($('#message-box')[0].scrollHeight);
    $('#start-button').text('New game');
    $('#start-button').off('click').click(newBotGame);
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

  var target = e.target;
  if (target.nodeName.toLowerCase() == 'img' || $(target).hasClass('rank-display')) {
    target = $(target).parent();
  }

  var classList = $(target).attr('class').split(/\s+/);
  var row;
  var col;

  for (var i = 0; i < classList.length; i++) {
    if (classList[i].search('row') !== -1) {
      row = parseInt(classList[i][3]);
    }
    else if (classList[i].search('col') !== -1) {
      col = parseInt(classList[i][3]);
    }
  }

  var squareObj = gameBoard.pieces[row][col];
  if (!gameBoard.inSetup && (squareObj.rank === 'F' || squareObj.rank === 'B')) {
    return;
  }

  if (jQuery.isEmptyObject(gameBoard.selected)) {
    if (('team' in squareObj) && squareObj.team == 'Blue'){
      $(target).addClass('select');
      gameBoard.selected = {row: row, col: col};
    }
  }
  else {
    var dst = {row: row, col: col};
    $('.square').each(function(index) {
      $(this).removeClass('select');
    });

    if (gameBoard.inSetup && 'team' in squareObj && squareObj.team == 'Blue') {
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
    ret += 'team' in piece && piece.team == 'Blue' ? piece.rank : ''));

  return ret;
}

function newBotGame() {
  initGame();
  gameBoard.type = 'BOT';

  $('#new-bot-game').hide();
  $('#new-pvp-game').hide();
  $('#start-button').show();
  $('#message-text').show();
  $('#send-button').show();
  socket.emit("new_bot_game");
}

function newPvpGame() {
  initGame();
  gameBoard.type = 'PVP';

  $('#new-bot-game').hide();
  $('#new-pvp-game').hide();
  $('#start-button').show();
  $('#message-text').show();
  $('#send-button').show();
  socket.emit("new_pvp_game");
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
