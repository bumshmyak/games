#!/usr/bin/env python

import pygame
import random
import copy

WIDTH = 800
HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
PADDLE_SPEED = 8

BALL_RADIUS = 20


PADDLE_COLOR = (0, 128, 255)
BALL_COLOR = (255, 140, 0)

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))


class Paddle:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.dy = 0

  def move(self):
    self.y += self.dy
    self.y = max(self.y, 0)
    self.y = min(self.y, HEIGHT - PADDLE_HEIGHT)

  def touches(self, ball):
    for d in (-1, 1):
      x = ball.x + d * BALL_RADIUS
      y = ball.y
      if (x >= self.x and x <= (self.x + PADDLE_WIDTH) and
          y >= self.y and y <= (self.y + PADDLE_HEIGHT)):
        return True
    return False

  def draw(self):
    self.move()
    pygame.draw.rect(
      SCREEN, PADDLE_COLOR, pygame.Rect(
        self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT))


class Ball:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.dx = random.randrange(5, 10)
    self.dy = random.randrange(3, 6)

  def move(self):
    self.x += int(self.dx)
    self.y += int(self.dy)

  def reflect_updown(self):
    self.dy = -self.dy    

  def reflect_paddle(self):
    self.dx = -self.dx

  def draw(self):
    self.move()
    pygame.draw.circle(SCREEN, BALL_COLOR, (self.x, self.y), BALL_RADIUS, 0)



def main():
  done = False
  clock = pygame.time.Clock()

  p1 = Paddle(WIDTH - PADDLE_WIDTH, HEIGHT // 2)
  p2 = Paddle(0, HEIGHT // 2)
  ball = Ball(WIDTH // 2, HEIGHT // 2) 

  while not done:
    SCREEN.fill((0, 0, 0))

    if ball.y <= BALL_RADIUS or ball.y >= HEIGHT - BALL_RADIUS:
      ball.reflect_updown()

    if p1.touches(ball) or p2.touches(ball):
      ball.reflect_paddle()
      ball.dx = 1.1 * ball.dx
      ball.dy = 1.1 * ball.dy
    elif ball.x <= BALL_RADIUS or ball.x >= WIDTH - BALL_RADIUS:
      ball = Ball(WIDTH // 2, HEIGHT // 2) 

    p1.draw()
    p2.draw()
    ball.draw()

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        done = True
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_DOWN: p1.dy = PADDLE_SPEED
        if event.key == pygame.K_UP: p1.dy = -PADDLE_SPEED
        if event.key == pygame.K_f: p2.dy = PADDLE_SPEED
        if event.key == pygame.K_r: p2.dy = -PADDLE_SPEED
      elif event.type == pygame.KEYUP:
        if event.key in (pygame.K_DOWN, pygame.K_UP):
          p1.dy = 0
        if event.key in (pygame.K_f, pygame.K_r):
          p2.dy = 0

    pygame.display.update()
    clock.tick(FPS)

if __name__ == '__main__':
  main()

