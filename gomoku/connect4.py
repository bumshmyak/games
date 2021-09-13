import numpy as np
import random
import copy

class HumanAgent:
  def __init__(self, game_cls):
    self.game_cls = game_cls

  def act(self, observation, unused_env=None):
    legal = self.game_cls.legal_actions(observation)
    while True:
      i = int(input('Input col: '))
      if i in legal:
        break
    return i

class Connect4:
  def __init__(self, board_height=6, board_width=7,cross_size=4):
    self.board_height = board_height
    self.board_width = board_width
    self.cross_size = cross_size
    self.board = np.zeros((board_height, board_width))
    self.player = 0

  @staticmethod
  def observation_hash(observation):
    _, board = observation
    return hash(np.array_str(board))

  @staticmethod
  def legal_actions(observation):
    _, board = observation
    return list(np.where(board[0,:] == 0)[0])

  def reset(self):
    self.board = np.zeros((self.board_height, self.board_width))
    self.player = 0
    return (self.player, self.board)

  def observation(self):
    return (self.player, self.board)

  def step(self, action):
    i = self.board_height - 1
    while i >= 0 and self.board[i][action] != 0:
      i -= 1
    assert(i >= 0)
    self.board[i][action] = self.player + 1
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
    for i in range(self.board_height):
      for j in range(self.board_width - self.cross_size + 1):
        if np.all(self.board[i, j:j + self.cross_size] == p):
          return True

    # Vertical
    for i in range(self.board_height - self.cross_size + 1):
      for j in range(self.board_width):
        if np.all(self.board[i:i + self.cross_size, j] == p):
          return True

    # Diagonal
    for i in range(self.board_height - self.cross_size + 1):
      for j in range(self.board_width - self.cross_size + 1):
        ii = [i + k for k in range(self.cross_size)]
        jj = [j + k for k in range(self.cross_size)]
        if np.all(self.board[ii, jj] == p):
          return True

    # Reverse diagonal
    for i in range(self.cross_size - 1, self.board_height):
      for j in range(self.cross_size - 1, self.board_width):
        ii = [i - self.cross_size  + 1 + k for k in range(self.cross_size)]
        jj = [j - k for k in range(self.cross_size)]
        if np.all(self.board[ii, jj] == p):
          return True

    return False

  def __repr__(self):
    return np.array_str(self.board)
