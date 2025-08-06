import chess
import random
import json
import os

if os.path.exists('openings.json'):
    with open('openings.json', 'r') as f:
        OPENING_BOOK = json.load(f)
else:
    OPENING_BOOK = {}

class ChessAI:
    def __init__(self, difficulty='hard'):
        self.difficulty = difficulty
        self.depth = {
            'easy': 1,
            'medium': 2,
            'hard': 3,
            'unbeatable': 6
        }.get(difficulty, 3)

    def get_best_move(self, board):
        fen_key = board.fen().split(' ')[0]
        turn = board.turn
        key = f"{fen_key}_{turn}"

        if key in OPENING_BOOK and self.difficulty in ['hard', 'unbeatable']:
            moves = OPENING_BOOK[key]
            if moves:
                return max(moves, key=moves.get)

        _, move = self.minimax(board, self.depth, True, float('-inf'), float('inf'))
        return move.uci() if move else None

    def evaluate_board(self, board):
        if board.is_checkmate():
            return -9999 if board.turn else 9999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

        score = 0
        for piece_type in piece_values:
            score += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        for sq in center_squares:
            if board.is_attacked_by(chess.WHITE, sq):
                score += 0.1
            if board.is_attacked_by(chess.BLACK, sq):
                score -= 0.1

        return score if board.turn == chess.WHITE else -score

    def minimax(self, board, depth, maximizing, alpha, beta):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board), None

        best_move = None
        if maximizing:
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score, _ = self.minimax(board, depth - 1, False, alpha, beta)
                board.pop()
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval_score, _ = self.minimax(board, depth - 1, True, alpha, beta)
                board.pop()
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

# Pre-load AI agents
ai_agents = {
    'easy': ChessAI('easy'),
    'medium': ChessAI('medium'),
    'hard': ChessAI('hard'),
    'unbeatable': ChessAI('unbeatable')
}
