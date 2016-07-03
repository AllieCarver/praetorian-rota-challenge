# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 13:20:33 2015

@author: killerdigby
"""

import requests
import random
from itertools import permutations as perm
import rota 

class RotaBot():
    def __init__(self):
        self._circle = [0,1,2,5,8,7,6,3,0,1]
        self._cross = [(0,4,8),(1,4,7),(2,4,6),(3,4,5)]
        self._scores = {board:0.0 for board in perm('pppccc---',9)}
        self._player_boards = {}
        self._comp_boards = {}
        self.initialize_scores()
        self.inititialize_comp_boards()
    
    def initialize_scores(self):
        """
        Assign desirability value to boards for move selection
        """
        for board in self._scores:
            winner = self.check_winner(board)
            if winner == 'c':
                self._scores[tuple(board)] -= 3.0
                moves = self.available_moves(board,'c')
                for move in moves:
                    new_board = self.change_board(board,move,'c')
                    self._scores[tuple(new_board)] -= 2.0
                    inner_moves = self.available_moves(new_board,'c')
              
            if winner == 'p':
                self._scores[tuple(board)] += 3.0
                moves = self.available_moves(board,'p')
                for move in moves:
                    new_board = self.change_board(board,move,'p')
                    self._scores[tuple(new_board)] += 2.0
                    inner_moves = self.available_moves(new_board,'p')
                    for inner_move in inner_moves:
                        inner_board = self.change_board(new_board,inner_move,'p')
                        self._scores[tuple(inner_board)] += 1.0

 
    def inititialize_comp_boards(self):
        for board in self._scores:
            if self._scores[board] <= 0:
                player_pos = []                
                for idx in range(9):
                    if board[idx] == 'p':
                        player_pos.append(idx) 
                self._comp_boards[tuple(player_pos)] = self._scores[board]
        
    def check_winner(self, board):
        """
        Returns the winner
        """
        for pos in range(8):            
            if board[self._circle[pos]] != '-':    
                if board[self._circle[pos]] == board[self._circle[pos+1]] ==board[self._circle[pos+2]]:
                    return board[self._circle[pos]]
        for pos in self._cross:
            if board[pos[0]] != '-':
                if board[pos[0]] == board[pos[1]] == board[pos[2]]:
                    return board[pos[0]] 

    def change_board(self, board, move, player):
        """
        Move a piece 
        """
        fromm, to = move
        board = list(board)
        board[fromm] = '-'
        board[to] = player
        return ''.join(board)
    
    def available_moves(self, board, player):
        moves = [0,1,2,5,8,7,6,3]
        current = [idx for idx in range(9) if board[idx] == player]    
        #create list of (from, to moves
        available = []    
        for pos in current:
            if pos != 4:
                idx = moves.index(pos)
                if board[moves[idx-1]] == '-':
                    available.append((moves[idx],moves[idx-1]))
                if board[moves[(idx+1)%8]] == '-':
                    available.append((moves[idx], moves[(idx+1)%8]))
                if board[4] == '-':
                    available.append((moves[idx], 4))
            elif pos == 4:
                for idx in range(9):
                    if board[idx] == '-':
                        available.append((pos, idx))
        return available
    
    
    def update_scores(self, scores, board):
        """
        Scores board and updates  scores 
        """
        winner = self.check_winner(board)
        increment = 1.0
        if winner:    
            if winner == 'c':
                increment = 1.2
                other = 'p'          
            else:
                other = 'c'
            for idx in range(9):
                if board[idx] == winner:
                    scores[idx] += increment * 1.0
                elif board[idx] == other:
                    scores[idx] -= 1.0                      
                        
    def get_best_place(self, board, scores):
        """
        for place score
        """
        current_best =  (None,0)
        for idx in range(9):
            if board[idx] == '-':
                if current_best[0] == None:
                    current_best = (idx, scores[idx])
                elif scores[idx] > current_best[1]:
                    current_best = (idx, scores[idx])
        return current_best[0]                
                        
    
    def mc_placing_trial(self, board):
        """
        Randomly assign remaining player and computer choices
        """
        board = list(board)    
        empty_spaces =  [idx for idx in range(9) if board[idx] == u'-']
        while board.count('p') < 3:
            move = empty_spaces.pop(random.randrange(len(empty_spaces)))        
            board[move] = 'p'
            if board.count('c') < 3:
                move = empty_spaces.pop(random.randrange(len(empty_spaces)))                                  
                board[move] = 'c'
        return "".join(board)    

    def mc_place(self, board):
        """
        Returns best board position to place player piece
        """
        #score of each position initiialized to 0    
        scores = [0.0] * 9
        
        if board.count('-') == 9 :
            ans = random.choice(self._circle)    
            print ans
            return ans

        elif board.count('c') == 3:
                if board.count('p') == 2:
                    empty = [idx for idx in range(9) if board[idx] == '-']
                    available = []                
                    for idx in empty:
                        new_board = list(board)
                        new_board[idx] = 'p'
                        available.append(("".join(new_board), idx))
                    best_moves = []                
                    for move in available:
                        if best_moves == []:
                            best_moves.append((self._scores[tuple(move[0])], move[1]))
                        elif self._scores[tuple(move[0])] == best_moves[0][0]:
                            best_moves.append((self._scores[tuple(move[0])], move[1]))
                        elif self._scores[tuple(move[0])] > best_moves[0][0]:
                            best_moves = [(self._scores[tuple(move[0])], move[1])]
                                  
                    best_move = random.choice(best_moves)
                    return best_move[1] 
        
        for dummy_trial in range(10000):
            played_board = self.mc_placing_trial(board)   
            self.update_scores(scores, played_board)  
        return self.get_best_place(board, scores)    
    
    
    def learned_player_move(self, board):
        available = self.available_moves(board, 'p')
        best_moves=[]
        for move in available:
            result_board = self.change_board(board, move,'p')
           
            if best_moves == []:
                best_moves.append((self._scores[tuple(result_board)], move))
            elif self._scores[tuple(result_board)] == best_moves[0][0]:
                best_moves.append((self._scores[tuple(result_board)], move))
            elif self._scores[tuple(result_board)] > best_moves[0][0]:
                best_moves = [(self._scores[tuple(result_board)], move)]
        best_move = random.choice(best_moves)   
        return best_move[1]           

    def play(self):
        """
        hear of the beast...don't look it's nasty
        """
        found_hash=''
        trials = 0
        while found_hash == '':
            try:     
                game = rota.RotaAPI()
                res = game.json
                board = game.json['data']['board']
                trials +=1
                while res['status'] == 'success':
                    print res
                    move=self.mc_place(board) + 1
                    res = game.place(move)
                    print res
                    if res['status'] == 'success':
                        board = res['data']['board']
                        count = 0        
                        if board.count('p') == 3:
                            board_history = [board]
                            while res['status'] == 'success' and found_hash == '':
                                old_board =  res['data']['board']
                                board_history.append(old_board)
                                
                                fromm, to = self.learned_player_move(old_board)
                                res = game.move(fromm + 1, to + 1)
                                print res                   
                                try:    
                                    if res['data']['computer_wins'] == 1:
                                        self._scores[tuple(res['data']['board'])] -= 3
                                        amt = 2 
                                        for board in board_history[::-1]:
                                            if board:
                                                self._scores[tuple(board)] -= amt
                                                amt -= 1
                                        print count
                                        break
                                except KeyError:
                                    break
                                count+=1
                                if len(board_history) > 2:
                                    board_history.pop(0)
                                try:
                                    found_hash = res['data']['hash']
                                    print found_hash
                                except KeyError:
                                    pass
            except requests.exceptions.ConnectionError:
                pass     
            
x= RotaBot()
x.play()
