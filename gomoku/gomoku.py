import numpy as np
import random
import copy  


class Gomoku:
  def __init__(self, board_size=3, cross_size=3):
    self.board_size = board_size
    self.cross_size = cross_size
    self.board = np.zeros((board_size, board_size))
    self.player = 0

  @staticmethod
  def observation_hash(observation):
    _, board = observation
    return hash(np.array_str(board))

  @staticmethod
  def legal_actions(observation):
    _, board = observation
    return list(zip(*np.where(board == 0)))

  def reset(self):
    self.board = np.zeros((self.board_size, self.board_size))
    self.player = 0
    return (self.player, self.board)

  def observation(self):
    return (self.player, self.board)

  def step(self, action):
    self.board[action] = self.player + 1
    reward = 0
    done = self.is_finished()
    if done:
      if self.is_win():
        reward = 1 - self.player
    self.player = 1 - self.player
    return (self.player, self.board), reward, done 

  def is_finished(self):
    return np.all(self.board) or self.is_win()

  def is_win(self):
    p = self.player + 1

    # Horizontal
    for i in range(self.board_size):
      for j in range(self.board_size - self.cross_size + 1):
        if np.all(self.board[i, j:j + self.cross_size] == p):
          return True

    # Vertical
    for i in range(self.board_size - self.cross_size + 1):
      for j in range(self.board_size):
        if np.all(self.board[i:i + self.cross_size, j] == p):
          return True

    # Diagonal
    for i in range(self.board_size - self.cross_size + 1):
      for j in range(self.board_size - self.cross_size + 1):
        ii = [i + k for k in range(self.cross_size)]
        jj = [j + k for k in range(self.cross_size)]
        if np.all(self.board[ii, jj] == p):
          return True

    # Reverse diagonal
    for i in range(self.cross_size - 1, self.board_size):
      for j in range(self.cross_size - 1, self.board_size):
        ii = [i - self.cross_size  + 1 + k for k in range(self.cross_size)]
        jj = [j - k for k in range(self.cross_size)]
        if np.all(self.board[ii, jj] == p):
          return True

    return False

  def __repr__(self):
    return np.array_str(self.board)


class HumanAgent:
  def act(self, observation, unused_env=None):
    legal = Gomoku.legal_actions(observation)
    while True:
      ij = tuple(map(int, input('Input row/col: ').split()))
      if ij in legal:
        break
    return ij


