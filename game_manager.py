class Game:
    def __init__(self, creator_username):
        self.creator_username = creator_username
        self.players = [creator_username]
        self.board = [' ' for _ in range(9)]
        self.current_turn = creator_username

    def add_player(self, username):
        if len(self.players) < 2:
            self.players.append(username)
            return True
        return False

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

    def create_game(self, creator_username):
        game_id = len(self.games)
        self.games[game_id] = Game(creator_username)
        return game_id

    def join_game(self, game_id, username):
        if game_id in self.games:
            return self.games[game_id].add_player(username)
        return False

    def get_game(self, game_id):
        return self.games.get(game_id)