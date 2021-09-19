#!/usr/bin/env python

import math
import pygame
import random
import copy

from dataclasses import dataclass

WIDTH = 800
HEIGHT = 600
D = 10
FPS = 60

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

def round_to_multiple(x, k):
  return (int(x) // k) * k

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
      SCREEN, self.color, pygame.Rect(
        self.x, HEIGHT - (self.y + self.h), self.w, self.h))

  def intersects(self, other):
    return (
      segment_intersects((self.x, self.x + self.w),
                         (other.x, other.x + other.w)) and
      segment_intersects((self.y, self.y + self.h),
                         (other.y, other.y + other.h)))


@dataclass
class Hero(SceneObject):
  x: float = 0
  y: float = 0
  w: float = 3 * D
  h: float = 3 * D
  dx: float = 0
  dy: float = 0
  color: tuple = (255, 140, 0)
  speed: float = D

  jump_event_id: int = pygame.USEREVENT + 1
  jump_time_ms: float = 100
  jump_speed: float = 3 * D

  fall_speed: float = D

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
      if self.y <= 0 or (self.on_platform and self.dy <= 0):
        self.is_jumping = False
        self.dy = 0
      else:
        self.dy = max(self.dy - self.jump_speed / 10, -self.fall_speed)
        pygame.time.set_timer(
          self.jump_event_id, int(self.jump_time_ms / 10), loops=1)

  def intersects_x(self, p):
    return segment_intersects(
      (self.x + 1, self.x + self.w - 1), (p.x, p.x + p.w))

  def intersects_y(self, p):
    return segment_intersects(
      (self.y + 1, self.y + self.h - 1), (p.y, p.y + p.h))

  def intersect(self, platforms):
    self.on_platform = False
    for p in platforms:
      if self.intersects_y(p):
        if self.x + self.w > p.x and self.x + self.w <= p.x + D:
          self.dx = 0
          self.x = p.x - self.w
        elif self.x < p.x + p.w and self.x >= p.x + p.w - D:
          self.dx = 0
          self.x = p.x + p.w
      if self.intersects_x(p):
        if (self.y >= p.y + p.h and
            self.y + self.dy <= p.y + p.h):
          self.y = p.y + p.h
          self.on_platform = True
          self.is_jumping = False
          self.dy = 0
        if (self.y + self.h <= p.y and
            self.y + self.h + self.dy >= p.y):
          self.y = p.y - self.h
          self.dy = 0

    if not (self.on_platform or self.is_jumping):
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
    self.x += self.dx
    self.y += self.dy
    self.x = round_to_multiple(self.x, D)
    self.y = round_to_multiple(self.y, D)
    self.y = max(self.y, 0)
    self.y = min(self.y, HEIGHT - self.h)
    self.x = max(self.x, 0)
    self.x = min(self.x, WIDTH - self.w)

  def draw(self):
    self.move()
    pygame.draw.rect(
      SCREEN, self.color, pygame.Rect(
        self.x, HEIGHT - (self.y + self.h), self.w, self.h))

def main():
  done = False
  clock = pygame.time.Clock()

  hero = Hero()
  platforms = [Platform(100, 30, 300, 20), Platform(500, 150, 200, 20)]
  objects = [hero] + platforms

  while not done:
    SCREEN.fill((0, 0, 0))

    hero.intersect(platforms)

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
