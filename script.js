var gameBoard = {};

function initBoard() {
  for (var i = 0; i < gameBoard.size; i++) {
    gameBoard.pieces[i] = new Array(gameBoard.size);
    for (var j = 0; j < gameBoard.size; j++) {
      gameBoard.pieces[i][j] = {rank: 1, team: "Blue"};
    }
  }
}

function initSquares() {
  for (var row = 0; row < gameBoard.size; row++) {
    for (var col = 0; col < gameBoard.size; col++) {
      var obj = (typeof gameBoard.pieces[row][col]) !== 'undefined' ? gameBoard.pieces[row][col] : {};
      var displayText = ('rank' in obj) ? obj.rank : '';
      var color = ('team' in obj) ? obj.team : '';
      var divStr = "<div class=\"square " + "row"+row + " col"+col + " " + color + " \">" +  displayText + "</div>";
      $("#board").append(divStr);
    }
  }
}

function updateSquares() {
  for (var row = 0; row < gameBoard.size; row++) {
    for (var col = 0; col < gameBoard.size; col++) {
      var obj = (typeof gameBoard.pieces[row][col]) !== 'undefined' ? gameBoard.pieces[row][col] : {};
      var rankText = ('rank' in obj) ? obj.rank : '';
      rankText = rankText == "None" ? "" : rankText;
      var color = ('team' in obj) ? obj.team : '';
    
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
  var boardStr = src.row.toString() + src.col.toString() + dst.row.toString() + dst.col.toString();
  socket.emit("receive_move", boardStr);
}

function startGame() {
  socket.emit("start_game");
  $('#start-button').hide();
}

function sendChat() { 
  var msg = $('#message-text').val();
  $('#message-text').val('');

  var msgDiv = '<div class="message-item">' + msg + '</div>';
  $('#message-box').append(msgDiv);
  socket.emit('receive_msg', msg);
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
  var squareHeight = $('.square').height();
  $('.square').css({
    'line-height': squareHeight + 'px'
  });
}


function initGame() {
  gameBoard.size = 10;
  gameBoard.pieces = new Array(gameBoard.size);
  gameBoard.selected = {};
  gameBoard.gameOver = false
  $('#start-button').off('click').click(startGame);
  $('#start-button').text('Start game');
  $('#start-button').show();

  $('#board').empty();
  $('#message-box').empty();
  initBoard();
  initSquares();
  centerSquareText();
  socket.emit("connection");
}

const socket = io("http://localhost:8080");

socket.on("boardUpdate", function(data) {
  var obj = JSON.parse(data);
  gameBoard.pieces = obj.board;
  updateSquares();

  var messages = obj.messages;
  for (var i = 0; i < messages.length; i++) {
    var msgDiv = '<div class="message-item">' + messages[i] + '</div>';
    $('#message-box').append(msgDiv);
  }

});

socket.on("gameOver", function() {
  gameBoard.gameOver = true;
  $('#message-box').append('Click the button to play again');
  $('#start-button').text('New game');
  $('#start-button').off('click').click(initGame);
  $('#start-button').show();
});

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

  if (gameBoard.gameOver) {
    return
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
     
    sendMove(gameBoard.selected, dst);
    gameBoard.selected = {};
  }
});

setDivHeights();
initGame();

