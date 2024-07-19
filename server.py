from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import functools
import chess
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

users = {
    "p1": "pass",
    "p2": "pass",
    
}

games = {}
current_user = None

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not current_user:
            return jsonify({'error': 'You must be logged in to access this resource'}), 401
        return view(**kwargs)
    return wrapped_view

@app.route('/game/<game_id>')
def game(game_id):
    if game_id not in games:
        return redirect(url_for('home'))
    return render_template_string(game_template(), game_id=game_id)

@app.route('/')
def home():
    return render_template_string(game_template())

def game_template():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZeroChess</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #000000;
                color: #ffffff;
                margin: 0;
                padding: 40px;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                overflow: hidden;
            }
            .container {
                display: flex;
                width: 1300px;
                justify-content: space-between;
            }
            .left-panel {
                width: 220px;
                margin-right: 40px;
            }
            .center-panel {
                width: 560px;
                margin-right: 40px;
            }
            .right-panel {
                width: 400px;
            }
            .logo {
                width: 60px;
                height: 60px;
                background-color: #FF0000;
                border-radius: 50%;
                margin-bottom: 30px;
            }
            .status-info {
                margin-bottom: 30px;
                font-size: 14px;
            }
            .status-info p {
                margin-bottom: 15px;
            }
            #myBoard {
                width: 560px;
                height: 560px;
                margin-bottom: 30px;
                display: grid;
                grid-template-columns: repeat(8, 1fr);
                grid-template-rows: repeat(8, 1fr);
                border: 2px solid #333;
            }
            .square {
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 40px;
                cursor: pointer;
            }
            .white {
                background-color: #f0d9b5;
            }
            .black {
                background-color: #b58863;
            }
            .white-piece {
                color: #fff;
                text-shadow: 0 0 3px #000;
            }
            .black-piece {
                color: #000;
                text-shadow: 0 0 3px #fff;
            }
            .message {
                background-color: #000000;
                border: 1px solid #ffffff;
                border-radius: 20px;
                padding: 15px 20px;
                margin-bottom: 15px;
                font-size: 14px;
            }
            .message:last-child {
                border-color: #8B00FF;
            }
            #newGameButton, #flipBoardButton {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #ffffff;
                border-radius: 20px;
                padding: 10px 20px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 20px;
            }
            #newGameButton:hover, #flipBoardButton:hover {
                background-color: #333333;
            }
            .login-form, .message-form {
                margin-top: 30px;
            }
            .login-form input, .message-form input {
                margin-bottom: 15px;
                padding: 12px;
                border: 1px solid #ffffff;
                border-radius: 20px;
                background-color: #000000;
                color: #ffffff;
                width: 100%;
                box-sizing: border-box;
                font-size: 14px;
            }
            .login-form button, .message-form button, #logoutButton {
                padding: 10px 20px;
                border: 1px solid #ffffff;
                border-radius: 20px;
                background-color: #000000;
                color: #ffffff;
                cursor: pointer;
                font-size: 16px;
                margin-top: 10px;
            }
            .login-form button:hover, .message-form button:hover, #logoutButton:hover {
                background-color: #333333;
            }
            #messages {
                height: 400px;
                overflow-y: auto;
                margin-bottom: 20px;
            }
            #logoutButton {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="left-panel">
                <div class="logo"></div>
                <div class="status-info">
                    <p>Status: <span id="status"></span></p>
                    <p>FEN: <span id="fen"></span></p>
                    <p>PGN: <span id="pgn"></span></p>
                </div>
                <button id="newGameButton">New game</button>
                <button id="flipBoardButton">Flip board</button>
            </div>
            <div class="center-panel">
                <div id="myBoard"></div>
            </div>
            <div class="right-panel">
                <div id="messages">
                    <!-- Messages will be appended here -->
                </div>
                <div class="message-form" id="messageFormContainer" style="display:none;">
                    <form id="messageForm">
                        <input type="text" id="message" placeholder="Type your message or move (e.g., e2e4)" required>
                        <button type="submit">Send</button>
                    </form>
                    <button id="logoutButton">Logout</button>
                </div>
                <div class="login-form" id="loginFormContainer">
                    <form id="loginForm">
                        <input type="text" id="username" placeholder="Username" required>
                        <input type="password" id="password" placeholder="Password" required>
                        <button type="submit">Login</button>
                    </form>
                </div>
            </div>
        </div>
        <script>
            const loginForm = document.getElementById('loginForm');
            const messageForm = document.getElementById('messageForm');
            const logoutButton = document.getElementById('logoutButton');
            const messagesDiv = document.getElementById('messages');
            const loginFormContainer = document.getElementById('loginFormContainer');
            const messageFormContainer = document.getElementById('messageFormContainer');
            const boardDiv = document.getElementById('myBoard');
            const newGameButton = document.getElementById('newGameButton');
            const flipBoardButton = document.getElementById('flipBoardButton');

            let game = new Chess();
            let $status = $('#status');
            let $fen = $('#fen');
            let $pgn = $('#pgn');
            let lastProcessedMessageIndex = -1;
            let selectedPiece = null;
            let boardOrientation = 'white';

            const piecesUnicode = {
                'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
                'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
            };

            function createBoard() {
                boardDiv.innerHTML = '';
                for (let i = 0; i < 64; i++) {
                    const square = document.createElement('div');
                    square.className = `square ${(i + Math.floor(i / 8)) % 2 === 0 ? 'white' : 'black'}`;
                    square.dataset.square = 'abcdefgh'[i % 8] + (8 - Math.floor(i / 8));
                    square.draggable = true;
                    square.addEventListener('dragstart', dragStart);
                    square.addEventListener('dragover', dragOver);
                    square.addEventListener('drop', drop);
                    square.addEventListener('click', handleClick);
                    boardDiv.appendChild(square);
                }
                updateBoard();
            }

            function updateBoard() {
                const squares = boardDiv.querySelectorAll('.square');
                squares.forEach(square => {
                    const piece = game.get(square.dataset.square);
                    if (piece) {
                        square.textContent = piecesUnicode[piece.type.toUpperCase()];
                        square.classList.remove('white-piece', 'black-piece');
                        square.classList.add(piece.color === 'w' ? 'white-piece' : 'black-piece');
                    } else {
                        square.textContent = '';
                        square.classList.remove('white-piece', 'black-piece');
                    }
                    square.draggable = !!piece;
                });
            }

            function handleClick(e) {
                const clickedSquare = e.target.dataset.square;
                const piece = game.get(clickedSquare);

                if (selectedPiece) {
                    const move = game.move({
                        from: selectedPiece,
                        to: clickedSquare,
                        promotion: 'q'
                    });

                    if (move) {
                        updateBoard();
                        updateStatus();
                        sendMove(selectedPiece + clickedSquare);
                    }

                    selectedPiece = null;
                    clearHighlights();
                } else if (piece && piece.color === (game.turn() === 'w' ? 'w' : 'b')) {
                    selectedPiece = clickedSquare;
                    highlightSquare(clickedSquare);
                }
            }

            function highlightSquare(square) {
                clearHighlights();
                document.querySelector(`[data-square="${square}"]`).style.backgroundColor = '#6200ea';
            }

            function clearHighlights() {
                document.querySelectorAll('.square').forEach(sq => {
                    sq.style.backgroundColor = '';
                });
            }

            function dragStart(e) {
                e.dataTransfer.setData('text/plain', e.target.dataset.square);
            }

            function dragOver(e) {
                e.preventDefault();
            }

            function drop(e) {
                e.preventDefault();
                const fromSquare = e.dataTransfer.getData('text');
                const toSquare = e.target.dataset.square;
                
                const move = game.move({
                    from: fromSquare,
                    to: toSquare,
                    promotion: 'q'
                });

                if (move) {
                    updateBoard();
                    updateStatus();
                    sendMove(fromSquare + toSquare);
                }
            }

            function updateStatus() {
                let status = '';

                let moveColor = 'White';
                if (game.turn() === 'b') {
                    moveColor = 'Black';
                }

                if (game.in_checkmate()) {
                    status = 'Game over, ' + moveColor + ' is in checkmate.';
                } else if (game.in_draw()) {
                    status = 'Game over, drawn position';
                } else {
                    status = moveColor + ' to move';
                    if (game.in_check()) {
                        status += ', ' + moveColor + ' is in check';
                    }
                }

                $status.html(status);
                $fen.html(game.fen());
                $pgn.html(game.pgn());
            }

            function sendMove(move) {
                const gameId = window.location.pathname.split('/').pop();
                fetch(`/send/${gameId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: move })
                }).then(response => {
                    if (response.status === 204) {
                        fetchMessages();
                    } else {
                        console.error('Failed to send move');
                    }
                }).catch(error => {
                    console.error('Error:', error);
                });
            }

            function newGame() {
                fetch('/new_game', {
                    method: 'POST'
                }).then(response => response.json())
                .then(data => {
                    if (data.game_url) {
                        window.location.href = data.game_url;
                    } else {
                        console.error('Failed to create new game');
                    }
                }).catch(error => {
                    console.error('Error:', error);
                });
            }

            function flipBoard() {
                boardOrientation = boardOrientation === 'white' ? 'black' : 'white';
                boardDiv.style.transform = boardOrientation === 'black' ? 'rotate(180deg)' : 'rotate(0deg)';
                document.querySelectorAll('.square').forEach(square => {
                    square.style.transform = boardOrientation === 'black' ? 'rotate(180deg)' : 'rotate(0deg)';
                });
            }

            newGameButton.addEventListener('click', newGame);
            flipBoardButton.addEventListener('click', flipBoard);

            loginForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;

                fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                }).then(response => {
                    if (response.status === 204) {
                        loginFormContainer.style.display = 'none';
                        messageFormContainer.style.display = 'block';
                        fetchMessages();
                        createBoard();
                    } else {
                        alert('Invalid username or password');
                    }
                });
            });

            messageForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const message = document.getElementById('message').value;

                if (message.length === 4 && /^[a-h][1-8][a-h][1-8]$/.test(message)) {
                    let move = game.move({
                        from: message.slice(0, 2),
                        to: message.slice(2, 4),
                        promotion: 'q'
                    });

                    if (move === null) {
                        alert('Invalid move');
                        return;
                    }

                    updateBoard();
                    updateStatus();
                    sendMove(message);
                } else {
                    sendMove(message);
                }

                document.getElementById('message').value = '';
            });

            logoutButton.addEventListener('click', function() {
                fetch('/logout', {
                    method: 'POST'
                }).then(response => {
                    if (response.status === 204) {
                        loginFormContainer.style.display = 'block';
                        messageFormContainer.style.display = 'none';
                        messagesDiv.innerHTML = '';
                        game.reset();
                        updateBoard();
                        lastProcessedMessageIndex = -1;
                    }
                });
            });

            function fetchMessages() {
                const gameId = window.location.pathname.split('/').pop();
                fetch(`/messages/${gameId}`)
                    .then(response => response.json())
                    .then(data => {
                        messagesDiv.innerHTML = '';
                        data.forEach((message, index) => {
                            const messageDiv = document.createElement('div');
                            messageDiv.className = 'message';
                            messageDiv.innerText = message;
                            messagesDiv.appendChild(messageDiv);

                            if (index > lastProcessedMessageIndex && message.includes('moved:')) {
                                let move = message.split(':')[1].trim();
                                game.move({
                                    from: move.slice(0, 2),
                                    to: move.slice(2, 4),
                                    promotion: 'q'
                                });
                                updateBoard();
                                updateStatus();
                            }
                        });
                        
                        lastProcessedMessageIndex = data.length - 1;
                    });
            }

            setInterval(fetchMessages, 5000);  // Refresh messages every 5 seconds

            createBoard();
            updateStatus();
        </script>
    </body>
    </html>
    '''

@app.route('/send/<game_id>', methods=['POST'])
@login_required
def send_message(game_id):
    global current_user
    if current_user and game_id in games:
        data = request.get_json()
        message = data.get('message')
        if message:
            if len(message) == 4 and message.isalnum():
                try:
                    move = chess.Move.from_uci(message)
                    if move in games[game_id]['board'].legal_moves:
                        games[game_id]['board'].push(move)
                        games[game_id]['messages'].append(f"{games[game_id]['current_player']} moved: {message}")
                        games[game_id]['current_player'] = 'white' if games[game_id]['current_player'] == 'black' else 'black'
                    else:
                        return jsonify({'error': 'Invalid move'}), 400
                except ValueError:
                    games[game_id]['messages'].append(f"{current_user}: {message}")
            else:
                games[game_id]['messages'].append(f"{current_user}: {message}")
        return ('', 204) 
    return jsonify({'error': 'Failed to send message'}), 400

@app.route('/messages/<game_id>', methods=['GET'])
@login_required
def get_messages(game_id):
    if game_id in games:
        return jsonify(games[game_id]['messages'])
    return jsonify([])

@app.route('/login', methods=['POST'])
def login():
    global current_user
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username in users and users[username] == password:
        current_user = username
        return ('', 204)
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    global current_user
    current_user = None
    return ('', 204)

@app.route('/login_status', methods=['GET'])
def login_status():
    return jsonify({'logged_in': current_user is not None})

@app.route('/new_game', methods=['POST'])
def new_game():
    game_id = str(uuid.uuid4())
    games[game_id] = {
        'board': chess.Board(),
        'messages': [],
        'players': [],
        'current_player': 'white'
    }
    return jsonify({'game_url': f'/game/{game_id}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
