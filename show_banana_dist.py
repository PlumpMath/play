from __future__ import division
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from panda3d.core import WindowProperties
from panda3d.core import Point3, LineSegs
from math import sqrt, pi, radians, cos, sin
import random
import sys
try:
    sys.path.insert(1, '../goBananas')
    import moBananas as mB
except ImportError:
    print 'need to load moBananas'
    sys.exit()


class BananaWorld(DirectObject):
    def __init__(self):
        self.base = ShowBase()
        # graphics
        # window
        props = WindowProperties()
        self.win_size = 600
        props.setSize(self.win_size, self.win_size)
        self.base.win.requestProperties(props)
        # set up key
        self.accept("c", self.move_center)
        self.accept("b", self.plot_bananas)
        self.accept("space", self.change_both)
        self.num_bananas = 10
        # total area is 100 (not true of the game, but just scales.
        # was easier to make everything 1/2 size for this size window)
        high_area = 0.25 * 0.33 * 100
        middle_area = 0.25 * 100
        self.high_radius = sqrt(high_area / pi)
        self.middle_radius = sqrt(middle_area / pi)
        self.high_reward = 6
        self.middle_reward = 4
        self.low_reward = 2
        #print self.high_radius
        #print self.middle_radius
        self.weight_center = (random.uniform(-5, 5), random.uniform(-5, 5))
        #print('weight center', self.weight_center)
        self.banana_model = []
        self.center_model = None
        self.high_node = None
        self.high_circle = None
        self.middle_node = None
        self.middle_circle = None
        self.plot_border()
        self.plot_bananas()
        self.plot_circles()

    def plot_bananas(self):
        pos_list = []
        #(x, y) = 0, 0
        avatar_pos = (0, 0)
        for i, j in enumerate(range(self.num_bananas)):
            (x, y) = mB.setXY(pos_list, avatar_pos)
            #print(x, y)
            (x, y) = (x/2, y/2)
            #print(x, y)
            pos_list.append((x, y))
            self.banana_model.append(self.base.loader.loadModel('ball'))
            self.banana_model[i].setPos(
                Point3(float(pos_list[i][0]), 25, float(pos_list[i][1])))
            self.banana_model[i].setScale(0.5)
            self.banana_model[i].setColor(1, 1, 0, 1)
            self.banana_model[i].reparentTo(self.base.render)
            #(x, y) = x + 1 / 2, y + 1 / 2

    def plot_border(self):
        border = LineSegs()
        border.setThickness(2.0)
        corner = self.win_size/100 * 5/6
        #print('corner', corner)
        border.move_to(corner, 25, corner)
        border.draw_to(corner, 25, -corner)
        border.draw_to(-corner, 25, -corner)
        border.draw_to(-corner, 25, corner)
        border.draw_to(corner, 25, corner)
        self.base.render.attach_new_node(border.create(True))

    def plot_circles(self):
        if self.center_model is None:
            # center
            self.center_model = self.base.loader.loadModel('ball')
            self.center_model.setPos(self.weight_center[0], 25, self.weight_center[1])
            self.center_model.setScale(0.2)
            self.center_model.setColor(1, 0, 1, 1)
            self.center_model.reparentTo(self.base.render)

            # first circle
            self.high_circle = LineSegs()
            self.high_circle.setThickness(2.0)
            self.high_circle.setColor(0, 1, 1, 1)

            # second circle
            self.middle_circle = LineSegs()
            self.middle_circle.setThickness(2.0)
            self.middle_circle.setColor(0, 1, 0, 1)

        if self.high_node is not None:
            self.high_node.detachNode()
            self.middle_node.detachNode()

        self.center_model.setPos(self.weight_center[0], 25, self.weight_center[1])
        angle_radians = radians(360)
        for i in range(50):
            a = angle_radians * i / 49
            y = self.high_radius * sin(a)
            x = self.high_radius * cos(a)
            self.high_circle.drawTo((x + self.weight_center[0], 25, y + self.weight_center[1]))
        self.high_node = self.base.render.attach_new_node(self.high_circle.create(True))
        for i in range(50):
            a = angle_radians * i / 49
            y = self.middle_radius * sin(a)
            x = self.middle_radius * cos(a)
            self.middle_circle.drawTo((x + self.weight_center[0], 25, y + self.weight_center[1]))
        self.middle_node = self.base.render.attach_new_node(self.middle_circle.create(True))

    def move_center(self):
        self.weight_center = (random.uniform(-5, 5), random.uniform(-5, 5))
        #print('weight center', self.weight_center)
        self.plot_circles()

    def change_both(self):
        self.move_center()
        self.plot_bananas()

if __name__ == "__main__":
    BW = BananaWorld()
    BW.base.run()