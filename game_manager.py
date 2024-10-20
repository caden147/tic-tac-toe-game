class Game:
    def __init__(self, creator_username):
        self.creator_username = creator_username
        self.players = [creator_username]
        self.board = [' ' for _ in range(9)]
        self.current_turn = creator_username

    def add_player(self, username):
        # check for game capacity, add if capacity != 2
        # tie up username properly
        return None
    
    def make_move(self, username, move):
        # if it's a user's turn, allow them to make a move.
        # tie up username and move properly
        return None

    def check_winner(self):
        # make list of winning combos
        # if gameboard contains winning combo, identify the player, establish them as the winner.
        # if combo doesn't exist and there are no more moves on the gameboard, tie and end game.
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