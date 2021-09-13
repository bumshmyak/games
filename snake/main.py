#!/usr/bin/env python

import pygame
import random

def random_not_in_snake(w, h, snake):
  empty_cells = []
  for i in range(w):
    for j in range(h):
      if (i, j) not in snake:
        empty_cells.append((i, j))
  return random.choice(empty_cells)

def main():  
  width = 800
  height = 600
  fps = 10
  cell_size = 40
  w = width // cell_size
  h = height // cell_size
  color = (0, 128, 255)
  dx = [0, 0, -1, 1]
  dy = [-1, 1, 0, 0]

  def draw_cell(x, y, is_empty=False):
    c = (0, 0, 0) if is_empty else color
    pygame.draw.rect(
      screen, c, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))

  pygame.init()
  screen = pygame.display.set_mode((width, height))
  done = False
  clock = pygame.time.Clock()

  snake = [random_not_in_snake(w, h, [])]
  food = random_not_in_snake(w, h, snake)
  direction = 0

  while not done:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        done = True
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP and direction != 1: direction = 0
        if event.key == pygame.K_DOWN and direction != 0: direction = 1
        if event.key == pygame.K_LEFT and direction != 3: direction = 2
        if event.key == pygame.K_RIGHT and direction != 2: direction = 3

    draw_cell(*food)

    head = ((snake[0][0] + dx[direction]) % w, (snake[0][1] + dy[direction]) % h)
    draw_cell(*head)

    if head in snake:
      done = True
    if head == food:
      snake = [head] + snake
      food = random_not_in_snake(w, h, snake)
    else:
      draw_cell(*snake[-1], is_empty=True)
      snake = [head] + snake[:-1]


    pygame.display.flip()
    clock.tick(fps)


if __name__ == '__main__':
  main()
