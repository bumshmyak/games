import numpy as np
import random
import copy  
import itertools
import pygame



class RandomAgent:
  def act(self, env):
    return random.choice(env.legal_actions())


class Node:
  def __init__(self, env, action=None, reward=0, done=False, parent=None):
    self.env = env
    self.action = action
    self.reward = reward
    self.done = done
    self.parent = parent
    self.n = 0
    self.total_reward = 0
    self.children = []

  def value(self):
    assert self.n > 0
    return self.total_reward / self.n

  def select_leaf(self):
    if not self.children:
      return self
    else:
      return random.choice(self.children).select_leaf()

  def expand(self):
    for action in self.env.legal_actions():
      next_env = copy.deepcopy(self.env)
      next_observation, reward, done = next_env.step(action)
      self.children.append(Node(next_env, action, reward, done, self))
    return random.choice(self.children)

  def rollout(self):
    done = self.done
    reward = self.reward
    env = copy.deepcopy(self.env)
    observation = env.observation()
    while not done:
      action = random.choice(env.legal_actions())
      observation, reward, done = env.step(action) 
    return reward

  def backprop(self, reward):
    self.total_reward += reward
    self.n += 1
    if self.parent:
      self.parent.backprop(reward)
  


class MCTSAgent:
  def __init__(self, num_trials=50):
    self.num_trials = num_trials

  def act(self, env):
    player, board = env.observation()
    is_max = (player == 0)
    
    root = Node(env)
    root.expand()

    best_reward = -float('inf') if is_max else float('inf')
    best_action = None

    for child in root.children:
      for i in range(self.num_trials):
        leaf = child.select_leaf()
        if not leaf.done:
          leaf = leaf.expand()
        reward = leaf.rollout()
        leaf.backprop(reward)

      candidate_reward = child.value()

      if ((is_max and (candidate_reward > best_reward)) or
          ((not is_max) and (candidate_reward < best_reward))):
        best_reward = candidate_reward
        best_action = child.action

    return best_action 


def display(game, screen):
  if screen is None:
    print(game)
  else:
    game.display(screen)
    pygame.display.flip()


def RunGame(game, agents, screen=None):
  assert len(agents) == 2
  player = 0

  game.reset()
  display(game, screen)
  while True:
    print('Player %d move.' % (player + 1))
    action = agents[player].act(game)
    player, reward, done = game.step(action)
    display(game, screen)
    if done:
      break
  if reward == 1:
    print('Player 1 won!')
  else:
    print('Player 2 won!')


BOARD_SIZE = 8
CELL_SIZE = 100
RADIUS = 30
BACK_COLORS = [(227, 209, 197), (150, 104, 75)]
FIGURE_COLORS = [(59, 25, 2), (212, 183, 163)]
HIGHLIGHT_COLOR = (240, 237, 105)


def sign(x):
  return 1 if x >= 0 else -1

class Checkers:
  def __init__(self):
    self.reset()

  def reset(self):
    self.board = np.array([
       [0, 2, 0, 2, 0, 2, 0, 2],
       [2, 0, 2, 0, 2, 0, 2, 0],
       [0, 2, 0, 2, 0, 2, 0, 2],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0],
       [1, 0, 1, 0, 1, 0, 1, 0],
       [0, 1, 0, 1, 0, 1, 0, 1],
       [1, 0, 1, 0, 1, 0, 1, 0]],
       dtype=np.uint8) 
    self.player = 1
    self.must_i = None
    self.must_j = None

  def __str__(self):
    r = []
    for i in range(BOARD_SIZE):
      r.append(str(BOARD_SIZE - i) + ''.join('|' + x for x in map(str, self.board[i,:])))
      r.append(' ' + '-' * 2 * BOARD_SIZE)
    r.append(' ' + ''.join([' ' + chr(ord('a') + i) for i in range(BOARD_SIZE)]))
    return '\n'.join(r)

  def display(self, screen, highlight=None):
    for i in range(BOARD_SIZE):
      for j in range(BOARD_SIZE):
        x = j * CELL_SIZE
        y = i * CELL_SIZE
        pygame.draw.rect(                               
          screen, BACK_COLORS[(i + j) % 2], pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))
        if self.board[i][j] != 0:
          pygame.draw.circle(screen, FIGURE_COLORS[self.board[i][j] % 2],
                             (x + CELL_SIZE // 2, y + CELL_SIZE // 2), RADIUS, 0)        
    if highlight is not None:
        x = highlight[1] * CELL_SIZE
        y = highlight[0] * CELL_SIZE
        pygame.draw.rect(                               
          screen, HIGHLIGHT_COLOR, pygame.Rect(x, y, CELL_SIZE, CELL_SIZE), 5)


  def observation(self):
    return self.player - 1, self.board


  @staticmethod
  def observation_hash(observation):
    _, board = observation
    return hash(np.array_str(board))

  def is_valid(self, i, j):
    return (i >= 0 and i < BOARD_SIZE and j >= 0 and j < BOARD_SIZE)

  def is_empty(self, i, j):
    return self.is_valid(i, j) and self.board[i][j] == 0

  def is_self(self, i, j):
    return self.is_valid(i, j) and self.board[i][j] != 0 and self.board[i][j] % 2 == self.player % 2

  def is_opponent(self, i, j):
    return self.is_valid(i, j) and self.board[i][j] != 0 and self.board[i][j] % 2 != self.player % 2

  def is_capture(self, i, j, di, dj, p):
    if not self.is_empty(i + p * di, j + p * dj):
      return False
    has_opponent = False 
    for k in range(1, p):
      ni, nj = i + k * di, j + k * dj
      if self.board[ni][nj] == 0:
        continue
      elif self.is_opponent(ni, nj):
        if has_opponent:
          return False
        else:
          has_opponent = True
      else:
        return False
    return has_opponent

  def is_legal_simple(self, i, j, di, dj, p):
    if not self.is_empty(i + p * di, j + p * dj):
      return False
    for k in range(1, p):
      ni, nj = i + k * di, j + k * dj
      if not self.board[ni][nj] == 0:
        return False
    return True


  def can_capture(self, i, j):
    is_simple = self.board[i][j] == self.player
    if is_simple:
      k = 1
    else:
      k = BOARD_SIZE
    for di in (-1, 1):
      for dj in (-1, 1):
        for p in range(2, 2 + k):
          if self.is_capture(i, j, di, dj, p):
            return True
    return False


  def legal_actions(self):
    capture_only = False
    legal = []
    valid_di = -1 if self.player == 1 else 1
    if self.must_i is not None:
      valid_starts = [(self.must_i, self.must_j)]
    else:
      valid_starts = itertools.product(range(BOARD_SIZE), repeat=2) 
    for i, j in valid_starts:
      if self.board[i][j] == 0 or self.board[i][j] % 2 != (self.player % 2):
        continue
      is_simple = self.board[i][j] == self.player
      if is_simple:
        k = 1
      else:
        k = BOARD_SIZE
      for di in (-1, 1):
        for dj in (-1, 1):
          # check captures
          for p in range(2, 2 + k):
            if self.is_capture(i, j, di, dj, p):
              move = (i, j, i + p * di, j + p * dj)
              if not capture_only:
                capture_only = True
                legal = [move]
              else:
                legal.append(move)

          # check simple moves
          if not capture_only:
            for p in range(1, k + 1):
              if is_simple and di != valid_di:
                continue
              if self.is_legal_simple(i, j, di, dj, p):
                legal.append((i, j, i + p * di, j + p * dj))
    # print(legal)
    return legal

  def step(self, action):
    self.must_i, self.must_j = None, None
    i, j, ni, nj = action

    self.board[ni][nj] = self.board[i][j] 
    self.board[i][j] = 0

    # make queen
    if (self.player % 2 == 1 and ni == 0) or (self.player % 2 == 0 and ni == 7):
      self.board[ni][nj] = self.player + 2

    di = sign(ni - i)
    dj = sign(nj - j)

    has_capture = False
    ti, tj = i + di, j + dj
    while ti != ni:
      if self.board[ti][tj] != 0:
        has_capture = True
        self.board[ti][tj] = 0
        break
      ti += di
      tj += dj

    reward = 0
    done = self.is_finished()
    if done:
      reward = 1 if self.player == 1 else -1

    if has_capture and self.can_capture(ni, nj):
      self.must_i, self.must_j = ni, nj
    else:
      self.player = 1 + (self.player % 2)
    return self.player - 1, reward, done 

  def is_finished(self):
    self.player = 1 + (self.player % 2)
    done = len(self.legal_actions()) == 0
    self.player = 1 + (self.player % 2)
    return done

  def __repr__(self):
    return np.array_str(self.board)


class TextHumanAgent:
  def act(self, env):
    legal = env.legal_actions()
    while True:
      frm, to = map(lambda x: (7 - (ord(x[1]) - ord('1')), ord(x[0]) - ord('a')),
                    input('Input move (from/to): ').split())
      move = frm + to
      if move in legal:
        break
    return move

class MouseHumanAgent:
  def __init__(self, screen):
    self.screen = screen

  def act(self, env):
    legal = env.legal_actions()
    src = None
    dst = None
    while True:
      event = pygame.event.wait()
      if event.type == pygame.QUIT:
        break
      if event.type == pygame.MOUSEBUTTONDOWN:
        (i, j) = (event.pos[1] // CELL_SIZE, event.pos[0] // CELL_SIZE)
        if not env.is_valid(i, j):
          continue
        if env.is_self(i, j):
          src = (i, j)
          env.display(self.screen, highlight=src) 
          pygame.display.flip()
        elif src is not None and env.is_empty(i, j):
          dst = (i, j)
        if src is not None and dst is not None:
          move = (src[0], src[1], dst[0], dst[1])
          if move in legal:
            return move  
 
    return move


def main():
  pygame.init()                                     
  screen = pygame.display.set_mode((800, 800))
  g = Checkers()
  a = [MouseHumanAgent(screen), MCTSAgent()]
  RunGame(g, a, screen)

if __name__ == '__main__':
  main()
