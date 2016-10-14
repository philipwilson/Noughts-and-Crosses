#!/usr/bin/env python

"""  Board and playing strategy for Noughts & Crosses.
"""

from random import choice
import sys

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
        stats = {}
        for cell in vector:
            stats[cell.player] = stats.get(cell.player, 0) + 1

        return stats

    def winning_move(self, cell):
        """ Does this cell make three in a row?
        """
        for vector in self.vectors_for_cell(cell):
            stats = self.__vector_stats(vector)
            if stats.get(cell.player, 0) == 3:
                return True

        return False

    def set_cell(self, position, player=None):
        """ Claim a cell for the player, adjust turn
        """

        if player is None:
            player = self.player_up

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

    def __winnable_vector(self, vector, player):
        """ Could player win this vector by taking the remaining cell?
        """
        stats = self.__vector_stats(vector)
        return stats.get(player, 0) == 2 and stats.get('empty', 0) == 1

    def __winning_move_for(self, player):
        """ Return a winning move if one exists (see above).
        """
        for vector in self.vectors():
            if self.__winnable_vector(vector, player):
                for cell in vector:
                    if cell.empty:
                        return cell.index
        return None

    def __move_makes_fork(self, cell, player):
        """ A fork is when two different vectors could be won in the next move,
            i.e., winning can't be blocked.
        """
        count = 0
        for vector in self.vectors_for_cell(cell):
            stats = self.__vector_stats(vector)
            if (stats.get(player, 0) == 1) and (stats.get('empty', 0) == 2):
                count = count + 1

        return count >= 2

    def __possible_wins(self, player):
        """ Return a list of moves that are in vectors with no opponent cells.
            These are vectors that could still be won.
        """
        possibles = {}
        for cell in self.empty_cells():
            for vector in self.vectors_for_cell(cell):
                stats = self.__vector_stats(vector)
                if stats.get(self.opponent(player), 0) == 0:
                    possibles[cell.index] = 1
                    break
        return possibles.keys()

    def __first_move(self):
        """  Grab a corner if moving first.  Randomize for fun..
        """
        return choice([0, 2, 6, 8]) if self.turn == 0 else None

    def __take_winning_move(self):
        """  If player can complete a vector, do it.
        """
        player = self.player_up
        return self.__winning_move_for(player)

    def __block_winning_move(self):
        """  If opponent could win next turn, block it.
        """
        player = self.player_up
        opponent = self.opponent(player)
        return self.__winning_move_for(opponent)

    def __create_fork(self):
        """  Create a fork.  See:  Board.__move_makes_fork().
        """
        player = self.player_up
        for cell in self.empty_cells():
            if self.__move_makes_fork(cell, player):
                return cell.index
        return None

    def __block_diag_fork(self):
        """  Block opposite-corners special case.
        """
        player = self.player_up
        if len(self.empty_cells()) == 6:
            opponent = self.opponent(player)
            for diag in self.diagonals():
                if diag[1].player == player:
                    if diag[0].player == opponent and diag[2].player == opponent:
                        return choice([1, 3, 5, 7])
        return None

    def __block_fork(self):
        """  Stop opponent creating fork.
        """
        player = self.player_up
        opponent = self.opponent(player)
        for cell in self.empty_cells():
            if self.__move_makes_fork(cell, opponent):
                return cell.index
        return None

    def __default_move(self):
        """  Prefer center, then corners, then sides.
             First try  moves that could lead to winning!
        """
        player = self.player_up
        preferred_move_order = [4, 0, 2, 6, 8, 1, 3, 5, 7]
        could_wins = self.__possible_wins(player)
        for candidate in preferred_move_order:
            if candidate in could_wins:
                return candidate

        for candidate in preferred_move_order:
            if self.cell_empty(candidate):
                return candidate

    def generate_move(self):
        """  Try move generators in order till one returns a move.
        """
        for tactic in [self.__first_move,
                       self.__take_winning_move,
                       self.__block_winning_move,
                       self.__create_fork,
                       self.__block_diag_fork,
                       self.__block_fork,
                       self.__default_move]:

            move = tactic()
            if move is not None:
                return move

def main(argv):
    """ Main playing loop.  Alternate input between players.
    """
    game = Board()
    movefunc = [game.generate_move, game.generate_move]

    try:
        if argv[1] == 'first':
            movefunc[0] = lambda: int(input("move? "))

        elif argv[1] == 'second':
            movefunc[1] = lambda: int(input("move? "))

        elif argv[1] == 'both':
            pass

    except IndexError:
        print("Usage:  " + argv[0] + " [first|second|both]")
        sys.exit(0)

    while game.turn < 9:
        cell = game.set_cell(movefunc[game.turn %2]())
        print(game.string() + "\n")
        if game.winning_move(cell):
            print(cell.player + " Wins!")
            break

if __name__ == "__main__":
    main(sys.argv)
