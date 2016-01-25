#!/usr/bin/env python

"""  Do nothing.
"""

import random

class Cell:
    """ Cells hold blegga.
    """

    def __init__(self, position):
        self.__owner = None
        self.__index = position

    @property
    def empty(self):
        """  Do nothing.
        """
        return True if (self.__owner is None) else False

    @property
    def player(self):
        """  Do nothing.
        """
        return "empty" if (self.empty) else self.__owner

    @property
    def index(self):
        """  Do nothing.
        """
        return self.__index

    @player.setter
    def player(self, player):
        """  Do nothing.
        """
        if self.empty:
            self.__owner = player
        else:
            raise Exception("trying to set occupied cell error!")

class Board:
    """ Noughts and Crosses board.
    """
    def __init__(self):
        self.board = [Cell(0), Cell(1), Cell(2), Cell(3), Cell(4), Cell(5),
                      Cell(6), Cell(7), Cell(8)]
        self.__turn = 0
        self.players = ['X', 'O']

    @property
    def turn(self):
        """  Do nothing.
        """
        return self.__turn

    @property
    def player_up(self):
        """  Do nothing.
        """
        return self.players[self.turn % 2]

    @property
    def first_player(self):
        """  Do nothing.
        """
        return self.players[0]

    def rows(self):
        return [[self.board[0], self.board[1], self.board[2]],
                [self.board[3], self.board[4], self.board[5]],
                [self.board[6], self.board[7], self.board[8]]]

    def columns(self):
        return [[self.board[0], self.board[3], self.board[6]],
                [self.board[1], self.board[4], self.board[7]],
                [self.board[2], self.board[5], self.board[8]]]

    def diagonals(self):
        return [[self.board[0], self.board[4], self.board[8]],
                [self.board[2], self.board[4], self.board[6]]]

    def vectors(self):
        return self.rows() + self.columns() + self.diagonals()

    def vectors_for_cell(self, cell):
        return [vector for vector in self.vectors() if cell in vector]

    def empty_cells(self):
        """ Count the remaining empty cells.
        """
        return [cell for cell in self.board if cell.empty]

    def vector_stats(self, vector):
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
            stats = self.vector_stats(vector)
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
        return ' ' if cell.empty else cell.player

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
        stats = self.vector_stats(vector)
        return True if (stats[player] == 2 and stats['empty'] == 1) else False

    def winning_move_for(self, player):
        """ Return a winning move if one exists (see above).
        """
        for vector in self.vectors():
            if self.winnable_vector(vector, player):
                for cell in vector:
                    if cell.empty:
                        return cell.index
        return False

    def move_makes_fork(self, cell, player):
        """ A fork is when two different vectors could be won in the next move,
            i.e., winning can't be blocked.
        """
        count = 0
        for vector in self.vectors_for_cell(cell):
            stats = self.vector_stats(vector)
            if (stats[player] == 1) and (stats['empty'] == 2):
                count = count + 1

        return True if (count >= 2) else False

    def possible_wins(self, player):
        """ Return a list of moves that are in vectors with no opponent cells.
            These are vectors that could still be won.
        """
        possibles = {}
        for cell in self.empty_cells():
            for vector in self.vectors_for_cell(cell):
                stats = self.vector_stats(vector)
                if stats[self.opponent(player)] == 0:
                    possibles[cell.index] = 1
                    break
        return possibles.keys()

# ------------------------------
# Helper functions:
# ------------------------------

def debug(msg):
    print(msg)

def random_from_array(array):
    return array[random.randrange(len(array))]

def play(board, player):
    """ Strategy for next move.
    """
    opponent = board.opponent(player)
    empty_cells = board.empty_cells()

    # If I have the first move, choose a random corner
    if board.turn == 0:
        return board.set_cell(random_from_array([0, 2, 6, 8]), player)

    # Does player have a winning move?  Take it!
    move = board.winning_move_for(player)
    if move != False:
        return board.set_cell(move, player)

    # Does opponent have a winning move?  Block it!
    move = board.winning_move_for(opponent)
    if move != False:
        debug("block win!")
        return board.set_cell(move, player)

    # Can player create a "fork"?  Do it!
    for cell in empty_cells:
        if board.move_makes_fork(cell, player):
            debug("create fork!")
            return board.set_cell(cell.index, player)

    # Opponent have diagonal corners with me in center? block a fork and grab a side!
    if len(empty_cells) == 6:
        for diag in board.diagonals():
            if diag[1].player == player:
                if diag[0].player == opponent and diag[2].player == opponent:
                    debug("block opposite-corners fork!")
                    return board.set_cell(random_from_array([1, 3, 5, 7]), player)

    # Can opponent create a "fork"?  Block it!
    for cell in empty_cells:
        if board.move_makes_fork(cell, opponent):
            debug("block fork!")
            return board.set_cell(cell.index, player)

    # prefer center, then corner, then side
    preferred_move_order = [4, 0, 2, 6, 8, 1, 3, 5, 7]

    # prefer moves that could lead to winning!
    could_wins = board.possible_wins(player)
    for move in preferred_move_order:
        if move in could_wins:
            return board.set_cell(move, player)

    for move in preferred_move_order:
        if board.cell_empty(move):
            debug("killing time...")
            return board.set_cell(move, player)

# --------------------
# Main game loop:
# --------------------

def main():
    """ Main playing loop.  Alternate input between players.
    """
    tboard = Board()

    while len(tboard.empty_cells()) > 0:
        activeplayer = tboard.player_up
        if activeplayer == tboard.first_player:
            #        tcell = play(tboard, activeplayer)
            umove = int(input("move? "))
            tcell = tboard.set_cell(umove, activeplayer)
        else:
            tcell = play(tboard, activeplayer)
            #        umove = int(input("move? "))
            #        tcell = tboard.set_cell(umove, activeplayer)

        print(tboard.string() + "\n")
        if tboard.winning_move(tcell):
            print(tcell.player + " Wins!")
            break

if __name__ == "__main__":
    # execute only if run as a script
    main()
