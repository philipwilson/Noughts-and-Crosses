#!/usr/bin/env python

import random

class Cell:
    def __init__(self, position):
        self.__s = ' '
        self.__i = position

    @property
    def empty(self):
        return True if (self.__s == ' ') else False  

    @property
    def player(self):
        return "empty" if (self.empty) else self.__s

    @property
    def index(self):
        return self.__i

    @player.setter
    def player(self, player):
        if self.empty:
            self.__s = player
        else:
            raise Exception("trying to set occupied cell error!")

class Board:
    def __init__(self):
        self.board = [Cell(0), Cell(1), Cell(2), Cell(3), Cell(4), Cell(5), Cell(6), Cell(7), Cell(8)]
        self.__turn = 0
        self.players = ['X', 'O']

    @property
    def turn(self):
        return self.__turn

    @property
    def player_up(self):
        return self.players[self.turn % 2]

    @property
    def first_player(self):
        return self.players[0]

    @property
    def second_player(self):
        return self.players[1]

    def rows(self):
        return [[self.board[0], self.board[1], self.board[2]],
                [self.board[3], self.board[4], self.board[5]],
                [self.board[6], self.board[7], self.board[8]]]

    def cols(self):
        return [[self.board[0], self.board[3], self.board[6]],
                [self.board[1], self.board[4], self.board[7]],
                [self.board[2], self.board[5], self.board[8]]]

    def diags(self):
        return [[self.board[0], self.board[4], self.board[8]],
                [self.board[2], self.board[4], self.board[6]]]

    def vectors(self):
        return self.rows() + self.cols() + self.diags()
    
    def vectors_for_cell(self, cell):
        candidates = []
        for vector in self.vectors():
            if cell in vector:
                candidates.append(vector)
        return candidates

    def vector_stats(self, vector):
        # return a dict with cell counts for each player and empty 
        stats = {'empty' : 0}
        for player in self.players:
            stats[player] = 0
            
        for cell in vector:
            stats[cell.player] = stats[cell.player] + 1
        return stats

    def winning_move(self, cell):
        for v in self.vectors_for_cell(cell):
            stats = self.vector_stats(v)

            if (stats[cell.player] == 3):
                return True
        return False

    def set_cell(self, position, player):
        cell = self.board[position]
        cell.player = player
        self.__turn = self.__turn + 1
        return cell

    def in_cell(self, index):
        return self.board[index].player

    def cell_empty(self, index):
        return self.board[index].empty
        
    def opponent(self, player):
        return self.players[1] if (player == self.players[0]) else self.players[0]

    def empty_cells(self):
        empties = []
        for cell in self.board:
            if (cell.empty):
                empties.append(cell)
        return empties

    def display_cell(self, cell):
        return ' ' if cell.empty else cell.player
    
    def string(self):
        r = self.rows()
        
        return "\n".join(["|".join(map(lambda x: self.display_cell(x), r[0])),
                          "-----",
                          "|".join(map(lambda x: self.display_cell(x), r[1])),
                          "-----",
                          "|".join(map(lambda x: self.display_cell(x), r[2]))])

    def winnable_vector(self, v, player):
        stats = self.vector_stats(v)
        return True if (stats[player] == 2 and stats['empty'] == 1) else False

    def winning_move_for(self, player):
        for vector in self.vectors():
            if (self.winnable_vector(vector, player)):
                for cell in vector:
                    if (cell.empty):
                        return cell.index
        return False

    def move_makes_fork(self, cell, player):
        count = 0
        for v in self.vectors_for_cell(cell):
            stats = self.vector_stats(v)
            if ((stats[player] == 1) and (stats['empty'] == 2)):
                count = count + 1

        return True if (count == 2) else False

    def possible_wins(self, player):
        possibles = {}
        for cell in self.empty_cells():
            for v in self.vectors_for_cell(cell):
                stats = self.vector_stats(v)
                if (stats[self.opponent(player)] == 0):
                    possibles[cell.index] = 1
                    break
        return possibles.keys()

# ------------------------------
# Helper functions:
# ------------------------------

def debug(s):
    print(s)

def random_from_array(a):
    return a[random.randrange(len(a))]

# ----------------------------------
# play:  strategy for a move is here
# ----------------------------------

def play(b, player):
    opponent = b.opponent(player)
    empty_cells = b.empty_cells()

    # If I have the first move, choose a random corner
    if (b.turn == 0):
        return b.set_cell(random_from_array([0, 2, 6, 8]), player)
    
    # Does player have a winning move?  Take it!
    move = b.winning_move_for(player)
    if (move != False):
        return b.set_cell(move, player)

    # Does opponent have a winning move?  Block it!
    move = b.winning_move_for(opponent)
    if (move != False):
        debug("block win!")
        return b.set_cell(move, player)

    # Can player create a "fork"?  Do it!
    for cell in empty_cells:
        if (b.move_makes_fork(cell, player)):
            debug("create fork!")
            return b.set_cell(cell.index, player)
    
    # Opponent have diagonal corners with me in center? block a fork and grab a side!
    if (len(empty_cells) == 6):
        if (b.in_cell(4) == player):
            if ((b.in_cell(0) == opponent and b.in_cell(8) == opponent) or ((b.in_cell(2) == opponent and b.in_cell(6) == opponent))):
                debug("block opposite-corners fork!")
                return b.set_cell(random_from_array([1, 3, 5, 7]), player)

    # Can opponent create a "fork"?  Block it!
    for cell in empty_cells:
        if (b.move_makes_fork(cell, opponent)):
            debug("block fork!")
            return b.set_cell(cell.index, player)

    # prefer center, then corner, then side
    preferred_move_order = [4, 0, 2, 6, 8, 1, 3, 5, 7]

    # prefer moves that could lead to winning!
    could_wins = b.possible_wins(player)
    for move in preferred_move_order:
        if move in could_wins:
            return b.set_cell(move, player)
    
    for move in preferred_move_order:
        if (b.cell_empty(move)):
            debug("killing time")
            return b.set_cell(move, player)

# --------------------
# Main game loop:
# --------------------
        
b = Board()

while(len(b.empty_cells()) > 0):
    player = b.player_up
    if (player == b.first_player):
        cell = play(b, player)
#        move = int(input("move? "))
#        cell = b.set_cell(move, player)
    else:
#        cell = play(b, player)
        move = int(input("move? "))
        cell = b.set_cell(move, player)

    print(b.string() + "\n")
    if (b.winning_move(cell)):
        print(cell.player + " Wins!")
        break
