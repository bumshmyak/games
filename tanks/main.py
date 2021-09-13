#!/usr/bin/env python

import pygame
import random
import copy

# Some colors
SHADOW = (192, 192, 192)
WHITE = (255, 255, 255)
LIGHTGREEN = (0, 255, 0 )
GREEN = (0, 200, 0 )
BLUE = (0, 0, 128)
LIGHTBLUE= (0, 0, 255)
RED= (200, 0, 0 )
LIGHTRED= (255, 100, 100)
PURPLE = (102, 0, 102)
LIGHTPURPLE= (153, 0, 153)
ORANGE = (255, 140, 0)

WIDTH = 800
HEIGHT = 600
FPS = 60

TANK_COLOR = ORANGE
TANK_WIDTH = 40
TANK_HEIGHT = 40
TANK_SPEED = 8
TOWER_COLOR = LIGHTPURPLE

ENEMY_COLOR = BLUE
ENEMY_SPEED = 4

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

DIRECTIONS = [UP, RIGHT, DOWN, LEFT]
DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]

TRIANGLES = [
  [(1, 3), (2, 1), (3, 3)],
  [(1, 1), (3, 2), (1, 3)],
  [(1, 1), (3, 1), (2, 3)],
  [(3, 1), (3, 3), (1, 2)],
]

BULLET_SHIFT = [(2, 0), (4, 2), (2, 4), (0, 2)]

BULLET_RADIUS = 5
BULLET_SPEED = 10
BULLET_COLOR = RED


pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))


class Bullet:
  def __init__(self, x, y, direction,
               r=BULLET_RADIUS,
               speed=BULLET_SPEED,
               color=BULLET_COLOR):
    self.x = x
    self.y = y
    self.dx = DX[direction]
    self.dy = DY[direction]
    self.r = r
    self.speed = speed
    self.color = color

  def move(self):
    self.x += self.speed * self.dx
    self.y += self.speed * self.dy


  def draw(self):
    self.move()
    pygame.draw.circle(SCREEN, self.color, (self.x, self.y), self.r)


  def is_out(self):
    return self.x <= 0 or self.x >= WIDTH or self.y <= 0 or self.y >= HEIGHT


class Tank:
  def __init__(self, x, y, direction,
               w=TANK_WIDTH,
               h=TANK_HEIGHT,
               speed=TANK_SPEED,
               color=TANK_COLOR):
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.speed = speed
    self.color = color
    self.direction = direction
    self.dx = 0
    self.dy = 0

  def move(self):
    self.x += self.speed * self.dx
    self.x = max(self.x, 0)
    self.x = min(self.x, WIDTH - self.w)

    self.y += self.speed * self.dy
    self.y = max(self.y, 0)
    self.y = min(self.y, HEIGHT - self.h)

  def contains(self, x, y):
    return (x > self.x and x < (self.x + self.w) and
            y > self.y and y < self.y + self.h)
      

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

  def hit_by(self, bullet):
    return self.contains(bullet.x, bullet.y)

  def draw(self):
    self.move()
    pygame.draw.rect(
      SCREEN, self.color, pygame.Rect(
        self.x, self.y, self.w, self.h))    
    pygame.draw.polygon(SCREEN, TOWER_COLOR,
      [(self.x + self.w * p[0] // 4, self.y + self.h * p[1] // 4)
       for p in TRIANGLES[self.direction]])


  def shoot(self):
    return Bullet(
      self.x + self.w * BULLET_SHIFT[self.direction][0] // 4,
      self.y + self.h * BULLET_SHIFT[self.direction][1] // 4,
      self.direction)


class EnemyTank(Tank):

  def __init__(self, x, y, leg_range,
               w=TANK_WIDTH, h=TANK_HEIGHT,
               speed=ENEMY_SPEED, color=ENEMY_COLOR):
    super(EnemyTank, self).__init__(x, y, UP, w, h, speed, color)
    self.leg_range = leg_range
    self.shoot_rage_range = shoot_rate_range
    self.leg_i = 0
    self.shoot_i = 0


  def move(self):
    if self.leg_i == 0:
      self.leg = random.randrange(*self.leg_range)
      self.direction = random.randrange(0, 4)
      self.dx = DX[self.direction]
      self.dy = DY[self.direction]
    self.leg_i = (self.leg_i + 1) % self.leg
    super(EnemyTank, self).move()

  def maybe_shoot(self, tank):
    # Check shoot line intersects tank(+neighborhod) rectangle
    pass


def init_tank():
  return Tank(
    x=(WIDTH - TANK_WIDTH) // 2, y=HEIGHT - TANK_HEIGHT,
    direction=UP)  

def init_enemies():
  return [
    EnemyTank(100, 100, (20, 30)),
    EnemyTank(300, 200, (20, 30)),
    EnemyTank(400, 300, (20, 30)),
    EnemyTank(500, 400, (20, 30)),
  ]


def main():
  done = False
  clock = pygame.time.Clock()

  tank = init_tank()
  enemies = init_enemies()
  bullets = []
  gameover = False

  while not done:
    SCREEN.fill((0, 0, 0))

    dead_bullets = set([])
    dead_enemies = set([])

    for i, bullet in enumerate(bullets):
      if bullet.is_out():
        dead_bullets.add(i)
        continue
      if tank.hit_by(bullet):
        gameover = True
      for j, enemy in enumerate(enemies):
        if enemy.hit_by(bullet):
          dead_bullets.add(i)
          dead_enemies.add(j)

    if gameover:
      tank = init_tank()
      enemies = init_enemies()
      bullets = []
      gameover = False
      continue     

    bullets = [b for (i, b) in enumerate(bullets)
               if i not in dead_bullets]
    enemies = [e for (i, e) in enumerate(enemies)
               if i not in dead_enemies]

    for f in [tank] + enemies + bullets:
      f.draw()

    for e in enemies:
      b = e.maybe_shoot(tank)
      if b is not None:
        bullets.append(b)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        done = True
      if event.type == pygame.KEYDOWN:
        # Tank movement
        if event.key == pygame.K_UP:
          tank.dy = -1
          tank.direction = UP
        if event.key == pygame.K_DOWN:
          tank.dy = 1
          tank.direction = DOWN
        if event.key == pygame.K_LEFT:
          tank.dx = -1
          tank.direction = LEFT
        if event.key == pygame.K_RIGHT:
          tank.dx = 1
          tank.direction = RIGHT

        # Shoot
        if event.key == pygame.K_f:
          bullets.append(tank.shoot())

      elif event.type == pygame.KEYUP:
        if event.key in (pygame.K_UP, pygame.K_DOWN):
          tank.dy = 0
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
          tank.dx = 0

    pygame.display.update()
    clock.tick(FPS)

if __name__ == '__main__':
  main()
