class Game:
    def __init__(self, creator_username, invited_username):
        self.creator_username = creator_username
        self.invited_username = invited_username
        self.players = [creator_username, invited_username]
        self.board = [' ' for _ in range(9)]
        self.current_turn = creator_username

    def make_move(self, username, move):
        if username != self.current_turn:
            return False
        move_index = int(move) - 1
        if self.board[move_index] != ' ':
            return False
        self.board[move_index] = 'X' if username == self.creator_username else 'O'
        self.current_turn = self.players[0] if username == self.players[1] else self.players[1]
        return True

    def check_winner(self):
        winning_combos = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for combo in winning_combos:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' ':
                return self.board[combo[0]]
        if ' ' not in self.board:
            return 'Tie'
        return None

class GameHandler:
    def __init__(self):
        self.games = {}

    def create_game(self, creator_username, invited_username):
        game_id = self.sorted_game_id(creator_username, invited_username)
        if game_id in self.games:
            return False
        self.games[game_id] = Game(creator_username, invited_username)
        return game_id

    def get_game(self, creator_username, invited_username):
        game_id = self.sorted_game_id(creator_username, invited_username)
        return self.games.get(game_id)

    def game_exists(self, creator_username, invited_username):
        game_id = self.sorted_game_id(creator_username, invited_username)
        return game_id in self.games
    
    def sorted_game_id(self, creator_username, invited_username):
        return ' '.join(sorted([creator_username, invited_username]))
