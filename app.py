from flask import Flask, render_template, request, jsonify
import chess
import ai_engine

app = Flask(__name__)
game_boards = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def make_move():
    data = request.json
    game_id = data.get('game_id', 'default')
    move = data.get('move')
    level = data.get('level', 'unbeatable')

    if game_id not in game_boards:
        game_boards[game_id] = chess.Board()

    board = game_boards[game_id]

    if move:
        try:
            board.push_uci(move)
        except:
            return jsonify({'error': 'Invalid move'}), 400

    if not board.is_game_over():
        ai = ai_engine.ai_agents.get(level, ai_engine.ai_agents['unbeatable'])
        ai_move = ai.get_best_move(board)
        if ai_move:
            board.push_uci(ai_move)
            return jsonify({
                'fen': board.fen(),
                'ai_move': ai_move,
                'game_over': board.is_game_over(),
                'result': board.result() if board.is_game_over() else None
            })
    
    return jsonify({
        'fen': board.fen(),
        'ai_move': None,
        'game_over': board.is_game_over(),
        'result': board.result() if board.is_game_over() else None
    })

@app.route('/reset', methods=['POST'])
def reset():
    game_id = request.json.get('game_id', 'default')
    game_boards[game_id] = chess.Board()
    return jsonify({'fen': chess.Board().fen()})

if __name__ == '__main__':
    app.run(debug=True)
