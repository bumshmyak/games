#!/usr/bin/env python

import pygame
import random
import copy

WIDTH = 600
HEIGHT = 800
FPS = 60

CAR_COLOR = (255, 140, 0)
CAR_WIDTH = 40
CAR_HEIGHT = 40
CAR_SPEED = 8

PIECE_COLOR = (0, 128, 255)
MIN_PIECE_WIDTH = 40
MAX_PIECE_WIDTH = 100
PIECE_HIEGHT = 40
PIECE_SPEED = 4
PIECE_RATE= 20

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))


class Piece:
  def __init__(self, x, y, w, h, speed, color, allow_out):
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.speed = speed
    self.color = color
    self.allow_out = allow_out
    self.dx = 0
    self.dy = 0

  def move(self):
    self.x += self.speed * self.dx
    self.x = max(self.x, 0)
    self.x = min(self.x, WIDTH - self.w)

    self.y += self.speed * self.dy
    self.y = max(self.y, 0)
    self.y = min(self.y, HEIGHT - (not self.allow_out) * self.h)

  def contains(self, x, y):
    return (x >= self.x and x <= (self.x + self.w) and
            y >= self.y and y <= self.y + self.h)
      

  def intersects(self, other):
    return (
      other.contains(self.x, self.y) or
      other.contains(self.x + self.w, self.y) or
      other.contains(self.x, self.y + self.h) or
      other.contains(self.x + self.w, self.y + self.h) or
      self.contains(other.x, other.y) or
      self.contains(other.x + other.w, other.y) or
      self.contains(other.x, other.y + other.h) or
      self.contains(other.x + other.w, other.y + other.h)
    )


  def draw(self):
    self.move()
    pygame.draw.rect(
      SCREEN, self.color, pygame.Rect(
        self.x, self.y, self.w, self.h))    

  @classmethod
  def generate(cls):
    x = random.randrange(0, WIDTH - MIN_PIECE_WIDTH)
    w = min(random.randrange(MIN_PIECE_WIDTH, WIDTH - x), MAX_PIECE_WIDTH)
    p = Piece(x, 0, w, PIECE_HIEGHT, PIECE_SPEED, PIECE_COLOR, True) 
    p.dy = 1
    return p

  def is_out(self):
    return self.y >= HEIGHT

def init_car():
  return Piece(
    x=(WIDTH - CAR_WIDTH) // 2, y=HEIGHT - CAR_HEIGHT,
    w=CAR_WIDTH, h=CAR_HEIGHT, speed=CAR_SPEED, color=CAR_COLOR,
    allow_out=False)  

def main():
  done = False
  clock = pygame.time.Clock()

  car = init_car()
  pieces = []
  i = 0

  while not done:
    SCREEN.fill((0, 0, 0))

    if i == 0:
      pieces.append(Piece.generate())
    i = (i + 1) % PIECE_RATE

    car.draw()

    survived = []
    for p in pieces:
      p.draw()

      if car.intersects(p):
        survived = []
        car = init_car()
        break

      if not p.is_out():
        survived.append(p)

    pieces = survived

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        done = True
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP: car.dy = -1
        if event.key == pygame.K_DOWN: car.dy = 1
        if event.key == pygame.K_LEFT: car.dx = -1
        if event.key == pygame.K_RIGHT: car.dx = 1 
      elif event.type == pygame.KEYUP:
        if event.key in (pygame.K_UP, pygame.K_DOWN):
          car.dy = 0
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
          car.dx = 0

    pygame.display.update()
    clock.tick(FPS)

if __name__ == '__main__':
  main()
