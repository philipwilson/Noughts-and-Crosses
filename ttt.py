#!/usr/bin/env python

"""  Board and playing strategy for Noughts & Crosses.
"""

import random

class Cell:
    """ Cells are either empty, or hold a player's mark.  I use objects for easy pass-by-reference,
        so the same cell can be in multiple vectors (row, column, diagonal) in the game.
    """

    def __init__(self, position):
        self.__owner = None
        self.__index = position

    @property
    def empty(self):
        """  Is this cell empty?
        """
        return self.__owner is None

    @property
    def player(self):
        """  Which player has marked this cell.
        """
        return "empty" if (self.empty) else self.__owner

    @property
    def index(self):
        """  Which cell am I?
        """
        return self.__index

    @player.setter
    def player(self, player):
        """  Used to mark the cell for a player.
        """
        if self.empty:
            self.__owner = player
        else:
            raise Exception("trying to set cell " + str(self.index) + " occupied by " + self.player)

class Board:
    """ Noughts and Crosses board.  Contains 9 cells in a 3x3 grid, with vectors for rows,
        columns, and diagonals.  A player wins by marking all 3 cells in a vector.
    """
    def __init__(self):
        self.board = [Cell(0), Cell(1), Cell(2), Cell(3), Cell(4), Cell(5),
                      Cell(6), Cell(7), Cell(8)]
        self.__turn = 0
        self.players = ['X', 'O']
        self.empty_char = ' '

    @property
    def turn(self):
        """  How many moves have been made so far.
        """
        return self.__turn

    @property
    def player_up(self):
        """  Which player plays next.
        """
        return self.players[self.turn % 2]

    @property
    def first_player(self):
        """  First player.
        """
        return self.players[0]

    @property
    def second_player(self):
        """  Second player.
        """
        return self.players[1]

    def rows(self):
        """  Row vectors.
        """
        return [[self.board[0], self.board[1], self.board[2]],
                [self.board[3], self.board[4], self.board[5]],
                [self.board[6], self.board[7], self.board[8]]]

    def columns(self):
        """  Column vectors.
        """
        return [[self.board[0], self.board[3], self.board[6]],
                [self.board[1], self.board[4], self.board[7]],
                [self.board[2], self.board[5], self.board[8]]]

    def diagonals(self):
        """  Diagonal vectors.
        """
        return [[self.board[0], self.board[4], self.board[8]],
                [self.board[2], self.board[4], self.board[6]]]

    def vectors(self):
        """  All vectors.
        """
        return self.rows() + self.columns() + self.diagonals()

    def vectors_for_cell(self, cell):
        """  All the vectors containing this cell.  Lazy inefficient implementation.
        """
        return [vector for vector in self.vectors() if cell in vector]

    def empty_cells(self):
        """ Count the remaining empty cells.
        """
        return [cell for cell in self.board if cell.empty]

    def __vector_stats(self, vector):
        """ Return a dict with cell counts for each player and empty.
        """
        stats = {'empty' : 0}
        for player in self.players:
            stats[player] = 0

        for cell in vector:
            stats[cell.player] = stats[cell.player] + 1
        return stats

    def winning_move(self, cell):
        """ Does this cell make three in a row?
        """
        for vector in self.vectors_for_cell(cell):
            stats = self.__vector_stats(vector)
            if stats[cell.player] == 3:
                return True

        return False

    def set_cell(self, position, player):
        """ Claim a cell for the player, adjust turn
        """
        cell = self.board[position]
        cell.player = player
        self.__turn = self.__turn + 1
        return cell

    def in_cell(self, index):
        """ Return the owner of the cell at index.
        """
        return self.board[index].player

    def cell_empty(self, index):
        """ Test emptiness of cell at index
        """
        return self.board[index].empty

    def opponent(self, player):
        """ Given a player, return the opposing player.
        """
        return self.players[1] if (player == self.players[0]) else self.players[0]

    def __display_cell(self, cell):
        """ Return displayable character for cell's owner (blank char for None.
        """
        return self.empty_char if cell.empty else cell.player

    def string(self):
        """ Return displayable string representation of the board.
        """
        rows = self.rows()

        return "\n".join(["|".join([self.__display_cell(x) for x in rows[0]]),
                          "-----",
                          "|".join([self.__display_cell(x) for x in rows[1]]),
                          "-----",
                          "|".join([self.__display_cell(x) for x in rows[2]])])

    def winnable_vector(self, vector, player):
        """ Could player win this vector by taking the remaining cell?
        """
        stats = self.__vector_stats(vector)
        return stats[player] == 2 and stats['empty'] == 1

    def winning_move_for(self, player):
        """ Return a winning move if one exists (see above).
        """
        for vector in self.vectors():
            if self.winnable_vector(vector, player):
                for cell in vector:
                    if cell.empty:
                        return cell.index
        return None

    def move_makes_fork(self, cell, player):
        """ A fork is when two different vectors could be won in the next move,
            i.e., winning can't be blocked.
        """
        count = 0
        for vector in self.vectors_for_cell(cell):
            stats = self.__vector_stats(vector)
            if (stats[player] == 1) and (stats['empty'] == 2):
                count = count + 1

        return count >= 2

    def possible_wins(self, player):
        """ Return a list of moves that are in vectors with no opponent cells.
            These are vectors that could still be won.
        """
        possibles = {}
        for cell in self.empty_cells():
            for vector in self.vectors_for_cell(cell):
                stats = self.__vector_stats(vector)
                if stats[self.opponent(player)] == 0:
                    possibles[cell.index] = 1
                    break
        return possibles.keys()


def random_from_array(array):
    """  Return a random element from the array.
    """
    return array[random.randrange(len(array))]

def first_move(board, player):
    """  Grab a corner if moving first.  Randomize for fun..
    """
    return random_from_array([0, 2, 6, 8]) if board.turn == 0 else None

def my_winning_move(board, player):
    """  If player can complete a vector, do it.
    """
    return board.winning_move_for(player)

def block_winning_move(board, player):
    """  If opponent could win next turn, block it.
    """
    opponent = board.opponent(player)
    return board.winning_move_for(opponent)

def create_fork(board, player):
    """  Create a fork.  See:  Board.move_makes_fork().
    """
    for cell in board.empty_cells():
        if board.move_makes_fork(cell, player):
            return cell.index
    return None

def block_diag_fork(board, player):
    """  Block opposite-corners special case.
    """
    if len(board.empty_cells()) == 6:
        opponent = board.opponent(player)
        for diag in board.diagonals():
            if diag[1].player == player:
                if diag[0].player == opponent and diag[2].player == opponent:
                    return random_from_array([1, 3, 5, 7])
    return None

def block_fork(board, player):
    """  Stop opponent creating fork.
    """
    opponent = board.opponent(player)
    for cell in board.empty_cells():
        if board.move_makes_fork(cell, opponent):
            return cell.index
    return None

def default_move(board, player):
    """  Prefer center, then corners, then sides.
         First try  moves that could lead to winning!
    """
    preferred_move_order = [4, 0, 2, 6, 8, 1, 3, 5, 7]
    could_wins = board.possible_wins(player)
    for move in preferred_move_order:
        if move in could_wins:
            return move

    for move in preferred_move_order:
        if board.cell_empty(move):
            return move

def play(board, player):
    """  Try move generators in order till one returns a move.
    """

    for func in [first_move, my_winning_move, block_winning_move, create_fork,
                 block_diag_fork, block_fork, default_move]:

        move = func(board, player)
        if move is not None:
            return move

def main():
    """ Main playing loop.  Alternate input between players.
    """
    game = Board()

    while game.turn < 9:
        if game.player_up == game.first_player:
            move = int(input("move? "))
        else:
            move = play(game, game.second_player)

        cell = game.set_cell(move, game.player_up)

        print(game.string() + "\n")
        if game.winning_move(cell):
            print(cell.player + " Wins!")
            break

if __name__ == "__main__":
    # execute only if run as a script
    main()
