__author__ = 'zshimanchik'
import math
import random

from NeuralNetwork.NeuralNetwork import NeuralNetwork
from NeuralNetwork.Neuron import Neuron
import World

TWO_PI = math.pi * 2


class Food(object):
    SMELL_SIZE_RATIO = 8.0
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.smell_size = self.size * Food.SMELL_SIZE_RATIO

    def beating(self, size):
        value = min(self.size, size)
        self.size -= value
        return value


class Animal(object):
    DEBUG = False
    MAX_ENERGY = 20
    ENERGY_FOR_EXIST = 0.007
    MOVE_ENERGY_RATIO = 0.01

    # sensor_count_in_head / sensor_count
    SENSOR_COUNT_IN_HEAD_RATIO = 0.5
    # head angle
    HEAD_ANGLE = math.pi / 4.0
    HALF_HEAD_ANGLE = HEAD_ANGLE / 2.0

    ENERGY_FULLNES_TO_BUD = 0.7
    CHANGE_TO_BUD = 0.005
    ENERGY_FOR_BUD = 2

    def __init__(self, world):
        self.world = world
        self._x = random.randint(0, self.world.width)
        self._y = random.randint(0, self.world.height)
        self.size = 7
        self.angle = 0

        self.sensor_count = 7
        self._sensor_count_in_head = int(self.sensor_count * Animal.SENSOR_COUNT_IN_HEAD_RATIO)
        self._sensor_count_not_in_head = self.sensor_count - self._sensor_count_in_head
        self.sensor_values = []
        self._sensors_positions = []
        self._sensors_positions_calculated = False

        self.energy = 10

        self.brain = NeuralNetwork([self.sensor_count, 5, 2])

    @property
    def sensors_positions(self):
        # on 45 degrees (pi/4) of main angle located 75% of all sensors
        if not self._sensors_positions_calculated:
            self._sensors_positions = []

            # calc sensor positions in head


            delta_angle = Animal.HEAD_ANGLE / (self._sensor_count_in_head-1)
            angle = -Animal.HALF_HEAD_ANGLE + self.angle
            for _ in range(self._sensor_count_in_head):
                self._sensors_positions.append(
                    (math.cos(angle) * self.size + self._x, math.sin(angle) * self.size + self._y))
                angle += delta_angle

            # calc sensor positions in body
            delta_angle = (TWO_PI - Animal.HEAD_ANGLE) / (self._sensor_count_not_in_head+1)
            angle = Animal.HALF_HEAD_ANGLE + self.angle
            for _ in range(self._sensor_count_not_in_head):
                angle += delta_angle
                self._sensors_positions.append(
                    (math.cos(angle) * self.size + self._x, math.sin(angle) * self.size + self._y))

            self._sensors_positions_calculated = True
        return self._sensors_positions

    def update(self, sensor_values):
        self.sensor_values = sensor_values
        answer = self.brain.calculate(sensor_values)
        if self.DEBUG:
            print(("answ=" + "{:.6f} " * len(answer) + "\tinp=" + "{:.6f} " * len(self.sensor_values)).format(
                *(answer + self.sensor_values)))

        self.energy -= Animal.ENERGY_FOR_EXIST
        if self.energy / Animal.MAX_ENERGY > Animal.ENERGY_FULLNES_TO_BUD and random.random() < Animal.CHANGE_TO_BUD * (1.0 - len(self.world.animals)/30):
            self.bud()

        self.move(answer[0], answer[1])

    def bud(self):
        self.energy -= Animal.ENERGY_FOR_BUD
        child = Animal(self.world)
        child.x = self.x + random.randint(-15, 15)
        child.y = self.y + random.randint(-15, 15)
        child.brain = clone_brain(self.brain)
        self.world.add_animal(child)

    def eat(self, food):
        value = min(World.World.EATING_VALUE, max(0, Animal.MAX_ENERGY - self.energy))
        value = food.beating(value)
        self.energy += value

    def move(self, move, rotate):
        self.energy -= (abs(move) + abs(rotate))*Animal.MOVE_ENERGY_RATIO

        self._sensors_positions_calculated = False
        self.angle += rotate
        self._x += math.cos(self.angle) * move * 2.0
        self._y += math.sin(self.angle) * move * 2.0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._sensors_positions_calculated = False

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._sensors_positions_calculated = False


def clone_brain(old_brain):
    brain = NeuralNetwork(old_brain.shape)
    for i in range(len(old_brain)):
        old_layer = old_brain[i]
        new_layer = brain[i]
        for j in range(len(old_layer)):
            old_neuron = old_layer[j]
            new_neuron = new_layer[j]
            if new_neuron.__class__ == Neuron:
                new_neuron.w = [ w + (random.random()*0.2 - 0.1)*(random.random() < 0.2) for w in old_neuron.w ]
                new_neuron.w0 = old_neuron.w0 + (random.random()*0.2 - 0.1)*(random.random() < 0.2)
    return brain