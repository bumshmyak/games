#!/usr/bin/env python

import math
import pygame
import random
import copy

from dataclasses import dataclass

WIDTH = 800
HEIGHT = 600
FPS = 60

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

class SceneObject:
  def draw(self):
    pass

  def handle_event(self, event):
    pass

def segment_intersects(s1, s2):
  return not ((s1[1] < s2[0]) or (s2[1] < s1[0]))

@dataclass
class Platform(SceneObject):
  x: float
  y: float
  w: float
  h: float
  color: tuple = (0, 128, 255)

  def draw(self):
    pygame.draw.rect(
      SCREEN, self.color, pygame.Rect(self.x, HEIGHT - self.y, self.w, self.h))

  def intersects(self, other):
    return (
      segment_intersects((self.x, self.x + self.w),
                         (other.x, other.x + other.w)) and
      segment_intersects((self.y, self.y + self.h),
                         (other.y, other.y + other.h)))


@dataclass
class Ball(SceneObject):
  x: float
  y: float
  dx: float = 0
  dy: float = 0
  color: tuple = (255, 140, 0)
  speed: float = 8
  radius: float = 20

  jump_event_id: int = pygame.USEREVENT + 1
  jump_time_ms: float = 100
  jump_speed: float = 20

  fall_speed: float = 10

  on_platform: bool = False
  hit_platform: bool = False
  is_jumping: bool = False

  def jump(self, speed):
    if not self.is_jumping:
      self.is_jumping = True
      self.dy = speed
      pygame.time.set_timer(
        self.jump_event_id, int(self.jump_time_ms / 10), loops=1)

  def handle_jump(self):
    if self.is_jumping:
      if self.y <= self.radius or (self.on_platform and self.dy <= 0):
        self.is_jumping = False
        self.dy = 0
      else:
        self.dy -= self.jump_speed / 10
        pygame.time.set_timer(
          self.jump_event_id, int(self.jump_time_ms / 10), loops=1)

  def intersect(self, platforms):
    self.on_platform = False
    for p in platforms:
      if ((self.x >= p.x) and
          (self.x <= p.x + p.w)):
        if (math.fabs(self.y - self.radius - (p.y + p.h)) <= 2):
          self.on_platform = True
        elif (math.fabs(self.y + self.radius - p.y) <= 2):
          self.hit_platform = True

    if self.hit_platform and self.dy > 0:
      self.dy = 0
      self.hit_platform = False

    if self.on_platform:
      if self.is_jumping and self.dy < 0:
        self.dy = 0
        self.is_jumping = False
    elif not self.is_jumping:
      self.dy = -self.fall_speed

  def keydown(self, key):
    if key == pygame.K_LEFT: self.dx = -self.speed
    if key == pygame.K_RIGHT: self.dx = self.speed
    if key == pygame.K_UP: self.jump(self.jump_speed)

  def keyup(self, key):
    if key in (pygame.K_LEFT, pygame.K_RIGHT):
      self.dx = 0

  def handle_event(self, event):
    if event.type == pygame.KEYDOWN: self.keydown(event.key)
    if event.type == pygame.KEYUP: self.keyup(event.key)
    if event.type == self.jump_event_id: self.handle_jump()

  def move(self):
    self.x += int(self.dx)
    self.y += int(self.dy)
    self.y = max(self.y, self.radius)
    self.y = min(self.y, HEIGHT - self.radius)
    self.x = max(self.x, self.radius)
    self.x = min(self.x, WIDTH - self.radius)

  def draw(self):
    self.move()
    pygame.draw.circle(SCREEN, self.color, (self.x, HEIGHT - self.y),
                       self.radius, 0)

def main():
  done = False
  clock = pygame.time.Clock()

  ball = Ball(Ball.radius, Ball.radius)
  platforms = [Platform(100, 70, 300, 5), Platform(500, 150, 200, 10)]
  objects = [ball] + platforms

  while not done:
    SCREEN.fill((0, 0, 0))

    ball.intersect(platforms)

    for obj in objects:
      obj.draw()

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        done = True
      for obj in objects:
        obj.handle_event(event)

    pygame.display.update()
    clock.tick(FPS)

if __name__ == '__main__':
  main()
