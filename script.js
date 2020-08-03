var gameBoard = {};
gameBoard.size = 10;
gameBoard.pieces = new Array(gameBoard.size);
gameBoard.selected = {};

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
      var displayText = ('rank' in obj) ? obj.rank : '';
      displayText = displayText == "None" ? " " : displayText;
      var color = ('team' in obj) ? obj.team : '';
      $(".row" + row).filter(".col" + col).text(displayText);
      $(".row" + row).filter(".col" + col).removeClass(['Red', 'Blue', 'None']);
      $(".row" + row).filter(".col" + col).addClass(color);
    }
  }
}

function setSelected(row, col) {
  $('.square').each( function(index) {
    var width = $(this).width();
    var height = $(this).height();
    if (row == Math.floor($(this).position().top / height) && col == Math.floor($(this).position().left / width)) {
      $(this).addClass('select');
    }
  });
}

function deselect() {
  $('.square').each(function(index) {
    $(this).removeClass('select');
  });
}

$(document).on('click', '.square', function(e) {
  var boardPosition = $('#board').position();
  var squareWidth = $('#board').width() / gameBoard.size;
  var squareHeight = $('#board').height() / gameBoard.size;

  var row = Math.floor((e.pageY - boardPosition.top) / squareHeight);
  var col = Math.floor((e.pageX - boardPosition.left) / squareWidth);

  var squareObj = gameBoard.pieces[row][col];
  if (jQuery.isEmptyObject(gameBoard.selected)) {
    if (('team' in squareObj) && squareObj.team == 'Blue'){
      setSelected(row, col);
      gameBoard.selected = {row: row, col: col};
    }
  }
  else {
    var dst = {row: row, col: col};
    deselect();
    sendMsg(gameBoard.selected, dst);
    gameBoard.selected = {};
  }
});

const socket = io("http://localhost:8080");
socket.on("boardUpdate", function(data) {
  var obj = JSON.parse(data);
  gameBoard.pieces = obj.board;
  updateSquares();
  $('#msgbox').val(obj.Message);
});

function sendMsg(src, dst) {
  var boardStr = src.row.toString() + src.col.toString() + dst.row.toString() + dst.col.toString();
  socket.emit("receive_move", boardStr);
}

function startGame() {
  socket.emit("start_game");
}

function setBoardWidth() {
  var boardWidth = $('#board').width();
  $('#board').css({
    'height': boardWidth + 'px'
  });
}

window.addEventListener('resize', setBoardWidth);

setBoardWidth();
initBoard();
initSquares();
socket.emit("connection");
