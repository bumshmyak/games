#!/usr/bin/env python

import pygame
import random
import copy

MASKS = [
  ['.....',
   '.....',
   '..#..',
   '.###.',
   '.....'],
  ['.....',
   '..#..',
   '..#..',
   '..#..',
   '..#..'],
  ['.....',
   '..##.',
   '..#..',
   '..#..',
   '.....'],
  ['.....',
   '.##..',
   '..#..',
   '..#..',
   '.....'],
  ['.....',
   '.....',
   '..##.',
   '..##.',
   '.....'],
  ['.....',
   '.....',
   '..##.',
   '.##..',
   '.....'],
  ['.....',
   '.....',
   '.##..',
   '..##.',
   '.....'],
  ['.....',
   '.....',
   '..#..',
   '.....',
   '.....'],

]


class Piece:
  def __init__(self, x, y, mask, is_binary=False):
    self.x = x
    self.y = y
    if is_binary:
      self.binary_mask = mask
    else:
      self.binary_mask = [[int(mask[i][j] == '#') for j in range(5)] for i in range(5)]

  def rotate(self, times=1):
    binary_mask = copy.deepcopy(self.binary_mask)
    for k in range(times):
      binary_mask = [[binary_mask[4 - j][i] for j in range(5)]
                          for i in range(5)]
    return Piece(self.x, self.y, binary_mask, is_binary=True)

  def shift(self, dx, dy):
    return Piece(self.x + dx, self.y + dy,
                 self.binary_mask, is_binary=True)

  def at(self, x, y):
    return self.binary_mask[y][x]


def GeneratePiece(x, y):
  return Piece(x, y, random.choice(MASKS))


class Board:
  def __init__(self, w, h):
    self.w = w
    self.h = h
    self.pad = 5

    def get_initial(x, y):
      if (x >= self.pad and
          x < self.pad + self.w and
          y < self.pad + self.h):
        return 0
      else:
        return 1

    self.v = [[get_initial(col, row) for col in range(w + 2 * self.pad)]
              for row in range(h + 2 * self.pad)]

  def at(self, x, y):
    return self.v[y][x]

  def set(self, x, y, value):
    self.v[y][x] = value

  def can_add(self, piece, new_piece):
    self.remove(piece)

    can = True
    for dx in range(5):
      for dy in range(5):
        if new_piece.at(dx, dy) and self.at(new_piece.x + dx, new_piece.y + dy):
          can = False

    self.add(piece)
    return can

  def _add(self, piece, value):
    for dx in range(5):
      for dy in range(5):
        if piece.at(dx, dy):
          self.set(piece.x + dx, piece.y + dy, value)

  def add(self, piece):
    self._add(piece, 1)

  def remove(self, piece):
    self._add(piece, 0)

  def swap(self, piece, new_piece):
    self.remove(piece)
    self.add(new_piece)
    return new_piece

  def burn(self):
    for y in range(self.pad, self.pad + self.h):
      is_full = True
      for x in range(self.pad, self.pad + self.w):
        if not self.at(x, y):
          is_full = False
          break
      if is_full:
        for y1 in range(y, self.pad, -1):
          for x in range(self.pad, self.pad + self.w):
            self.set(x, y1, self.at(x, y1 - 1))

  def display(self, view):
    for x in range(self.w):
      for y in range(self.h):
        view.draw(x, y, self.at(self.pad + x, self.pad + y))


class View:
  def __init__(self, width, height, cell_size):
    self.screen = pygame.display.set_mode((width, height))
    self.cell_size = cell_size
    self.color = (0, 128, 255)

  def draw(self, x, y, is_solid):
    c = self.color if is_solid else (0, 0, 0)
    pygame.draw.rect(
      self.screen, c, pygame.Rect(
        x * self.cell_size, y * self.cell_size,
        self.cell_size, self.cell_size))



def main():
  screen_width = 600
  screen_height = 800
  cell_size = 40
  fps = 3

  w = screen_width // cell_size
  h = screen_height // cell_size
  initial_pos = (w // 2 + 2, 2)

  pygame.init()
  done = False
  clock = pygame.time.Clock()

  view = View(screen_width, screen_height, cell_size)
  board = Board(w, h)
  piece = GeneratePiece(*initial_pos)

  while not done:
    dx = 0
    full_drop = False
    rotate_times = 0
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        done = True
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT: dx = -1
        if event.key == pygame.K_RIGHT: dx = 1
        if event.key == pygame.K_DOWN: rotate_times = 1
        if event.key == pygame.K_UP: rotate_times = 3
        if event.key == pygame.K_SPACE: full_drop = True

    new_piece = None
    if dx:
      new_piece = piece.shift(dx, 0)
    elif rotate_times:
      new_piece = piece.rotate(rotate_times)
    elif full_drop:
      new_piece = piece.shift(0, 1)
      while board.can_add(piece, new_piece):
        piece = board.swap(piece, new_piece)
        new_piece = piece.shift(0, 1)

    if new_piece and board.can_add(piece, new_piece):
      piece = board.swap(piece, new_piece)

    new_piece = piece.shift(0, 1)
    if board.can_add(piece, new_piece):
      piece = board.swap(piece, new_piece)
    else:
      board.burn()
      piece = GeneratePiece(*initial_pos)

    board.display(view)
    pygame.display.update()
    clock.tick(fps)


if __name__ == '__main__':
  main()
