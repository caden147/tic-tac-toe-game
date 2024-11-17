from game_actions import *

import unittest

def compute_flipped_board(board):
    flip = ""
    for character in board:
        flipped_character = ' '
        if character == 'X':
            flipped_character = 'O'
        elif character == 'O':
            flipped_character = 'X'
        flip += flipped_character
    return flip



class EndingTestCase(unittest.TestCase):
    def _assert_victory(self, board):
        self.assertEqual(check_winner(board), 'X')
        flipped_board = compute_flipped_board(board)
        self.assertEqual(check_winner(flipped_board), 'O')

    def test_empty_board(self):
        expected = None
        actual = check_winner(' '*9)
        self.assertEqual(expected, actual)

    def test_first_row(self):
        board = 'X'*3 + 'OO' + ' '*4
        self._assert_victory(board)

    def test_second_row(self):
        board = 'OO ' + 'X'*3 + ' '*3
        self._assert_victory(board)

    def test_last_row(self):
        board = 'OO ' + ' '*3 + 'X'*3
        self._assert_victory(board)

    def test_first_column(self):
        board = 'XO XO X  '
        self._assert_victory(board)

    def test_second_column(self):
        board = ' XO XO X  '
        self._assert_victory(board)

    def test_last_column(self):
        board = ' OX OX  X'
        self._assert_victory(board)

    def test_top_left_to_bottom_right_diagonal(self):
        board = 'XOO X   X'
        self._assert_victory(board)

    def test_bottom_left_to_top_right_diagonal(self):
        board = 'OOX X X  '
        self._assert_victory(board)

    

if __name__ == '__main__':
    unittest.main()