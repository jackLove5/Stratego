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
  for (var row = 1; row <= 10; row++) {
    for (var col = 1; col <= 10; col++) {
      var obj = (typeof gameBoard.pieces[row-1][col-1]) !== 'undefined' ? gameBoard.pieces[row-1][col-1] : {};
      var displayText = ('rank' in obj) ? obj.rank : '';
      var color = ('team' in obj) ? obj.team : 'Black';
      var divStr = "<div class=\"Piece " + "row"+row + " col"+col + " " + color + " \">" +  displayText + "</div>";
      $("#Board").append(divStr);
    }
  }
}

function updateSquares() {
  for (var row = 1; row <= 10; row++) {
    for (var col = 1; col <= 10; col++) {
      var obj = (typeof gameBoard.pieces[row-1][col-1]) !== 'undefined' ? gameBoard.pieces[row-1][col-1] : {};
      var displayText = ('rank' in obj) ? obj.rank : '';
      displayText = displayText == "None" ? " " : displayText;
      var color = ('team' in obj) ? obj.team : 'Black';
      $(".row" + row).filter(".col" + col).text(displayText);
      $(".row" + row).filter(".col" + col).removeClass(['Red', 'Blue', 'None']);
      $(".row" + row).filter(".col" + col).addClass(color);
    }
  }
}

function setSelected(row, col) {
  $('.Piece').each( function(index) {
    if (row == Math.floor($(this).position().top / 60) && col == Math.floor($(this).position().left / 60)) {
      $(this).addClass('Select');
    }
  });
}

function deselect(row, col) {
  $('.Piece').each( function(index) {
    if (row == Math.floor($(this).position().top / 60) && col == Math.floor($(this).position().left / 60)) {
      $(this).removeClass('Select');
    }
  });
}

$(document).on('click', '.Piece', function(e) {
  var boardPosition = $('#Board').position();
  var localX = Math.floor(e.pageX - boardPosition.left);
  var localY = Math.floor(e.pageY - boardPosition.top);
  var row = Math.floor(localY / 60);
  var col = Math.floor(localX / 60);
  var obj = gameBoard.pieces[row][col];
  if (jQuery.isEmptyObject(gameBoard.selected)) {
    if (('team' in obj) && obj.team == 'Blue'){
      setSelected(row, col);
      gameBoard.selected = {row: row, col: col};
    }
  }
  else {
    var dst = {row: row, col: col};
    deselect(gameBoard.selected.row, gameBoard.selected.col);
    sendMsg(gameBoard.selected, dst);
    gameBoard.selected = {};
  }
});

const socket = io("http://localhost:8080");
socket.on("boardUpdate", function(data) {
  console.log(data);
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

initBoard();
initSquares();
socket.emit("connection");
