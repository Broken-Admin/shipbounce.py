import pygame as pyg
import sys
from enum import Enum
from vectors import *
from interpolation import inverse_lerp
from random import randint
from math import sqrt

pyg.init()

size = width, height = 500, 250
white = (0xff, 0xff, 0xff)
gray = (0x56, 0x56, 0x56)
black = (0x00, 0x00, 0x00)

display = pyg.display.set_mode(size)

fps = 180;

Angles = {
    "RIGHT_UP": 45,
    "RIGHT_DOWN": 315,
    "LEFT_UP": 135,
    "LEFT_DOWN": 225
}


class Game:
    delta_time = 0
    last_tick = sys.maxsize * 2 + 1
    current_tick = 0
    # last tick in which a frame was rendered
    last_tick = 0

    def tick(self):
        self.current_tick = pyg.time.get_ticks()
        self.delta_time = self.current_tick - self.last_tick
        #print(self.last_tick, self.current_tick, self.delta_time)

    def frame_was_rendered(self):
        self.last_tick = self.current_tick

    def can_frame(self):
        # if a frame time has passed
        if (self.delta_time < (1000 / fps)):
            return False
        else:
            return True

    def prepare_for_render(self):
        display.fill(black)
    
    def render(self):
        pyg.display.flip()

class Ship:
    angle = 0;

    def __init__(self, speed, file):
        self.image = pyg.image.load(file)
        self.rect = self.image.get_rect()
        self.speed = speed; # Vector_2

    def refresh_image(self):
        self.image = pyg.image.load(file)

    def get_rect(self):
        return self.rect if self.angle == 0 else self.rotated_rect

    def rotate(self, angle):
        # No outside handling is necessary when rotating, other than assuring that the proper
        # rect is being operated on for movement and collisions
        self.angle = angle
        self.rotated_image = pyg.transform.rotate(self.image, angle)
        self.rotated_rect = self.rotated_image.get_rect()

    def get_directions(self):
        current_rect = self.get_rect()

        directions = []
        # x axis speed
        if self.speed.x > 0: directions.append("RIGHT")
        else: directions.append("LEFT")

        # y axis speed
        if self.speed.y > 0: directions.append("DOWN")
        else: directions.append("UP")

        return directions

    def get_boundaries_hit(self):
        current_rect = self.get_rect()

        boundaries = []
        if current_rect.left <= -5: boundaries.append("LEFT")
        # elif is used as the left and right boundaries cannot be hit at the same time
        elif current_rect.right >= width -5: boundaries.append("RIGHT")

        # elif is used as the top and bottom boundaries cannot be hit at the same time
        if current_rect.top <= -5: boundaries.append("TOP")
        elif current_rect.bottom >= height - 5: boundaries.append("BOTTOM")

        return boundaries

    def handle_movement(self):
        current_rect = self.get_rect()

        boundaries_hit = self.get_boundaries_hit()
        directions = self.get_directions()
        # Use a clever format string and a dict to get the proper angle
        angle = f"{directions[0]}_{directions[1]}"
        if "LEFT" in boundaries_hit or "RIGHT" in boundaries_hit:
            self.speed.x = -self.speed.x
        if "TOP" in boundaries_hit or "BOTTOM" in boundaries_hit:
            self.speed.y = -self.speed.y

        self.rotate(Angles[angle])
        self.angle = Angles[angle]
        current_rect = current_rect.move([self.speed.x, self.speed.y])

        if self.angle == 0: self.rect = current_rect
        else: self.rotated_rect = current_rect

    def display(self):
        if self.angle == 0:
            display.blit(self.image, self.rect)
        else:
            display.blit(self.rotated_image, self.rotated_rect)

class Star:
    lived_frames = 0

    def __init__(self, position, second_life):
        # Vector_3 position
        self.position = position
        # The life in seconds relative to the fps, if it lives n seconds, it should live fps * n seconds
        # The amount of frames through which this star should live
        self.frame_life = fps * second_life

        self.image = pyg.image.load('star.png')
        self.rect = self.image.get_rect()
        
        self.rect.topleft = (self.position.x, self.position.y)

    def elapse_frame(self):
        self.lived_frames += 1

    def calculate_alpha(self):
        inverse_lerp(0, self.frame_life, self.lived_frames)

    def is_alive(self):
        if self.lived_frames >= self.frame_life: return False
        else: return True

    def display(self):
        display.blit(self.image, self.rect)

game = Game()
ship = Ship(Vector_2(1, 1), 'ship.png')
stars = []

while 1:

    for event in pyg.event.get():
        if event.type == pyg.QUIT: sys.exit()

    game.tick()

    if not game.can_frame():
        continue

    # Handle creating and killing stars
    # 1800 * 2, 180 * 10 * 50, 180 frames per second, 10 seconds, 50 for less star generation chance
    if randint(0, int(sqrt(1800 * 50))) == randint(0, int(sqrt(1800 * 50))):
        stars.append(Star(Vector_3(randint(0,width-16), randint(0,height-16), randint(0,100)), randint(1,30)))
        stars.sort(key=lambda star: star.position.z)

    game.prepare_for_render()
    dead_stars = []
    for i in range(0, len(stars)):
        if(not stars[i].is_alive()):
            dead_stars.append(i)
        stars[i].calculate_alpha()
        stars[i].elapse_frame()
        stars[i].display()
    for i in dead_stars:
        del stars[i]
    ship.handle_movement()
    ship.display()
    game.render()
    game.frame_was_rendered()