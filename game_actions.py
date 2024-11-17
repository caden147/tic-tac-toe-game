VICTORY = "W"
LOSS = "L"
TIE = "T"

def is_valid_move_text(text: str):
    return len(text) == 2 and text[0].lower() in 'abc' and text[1] in '123'

def convert_move_text_to_move_number(text: str):
    letter = text[0].lower()
    number = int(text[1])
    if letter == 'b':
        number += 3
    elif letter == 'c':
        number += 6
    return number

def compute_current_player(game_state: str) -> str:
    """Determines the current player based on game state."""
    x_moves = game_state.count('X')
    o_moves = game_state.count('O')
    return 'X' if x_moves == o_moves else 'O'

def compute_other_piece(piece: str):
    return 'X' if piece == 'O' else 'O'

def check_winner(board):
    winning_combos = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    for combo in winning_combos:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
            return board[combo[0]]
    if ' ' not in board:
        return TIE
    return None