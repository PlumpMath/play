from __future__ import division
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from panda3d.core import Point3, LineSegs
from numpy import sqrt, pi
import random
import sys
try:
    sys.path.insert(1, '../goBananas')
    import moBananas as mB
except ImportError:
    print 'need to load moBananas'
    sys.exit()


class BananaWorld():
    def __init__(self):
        self.base = ShowBase()
        # graphics
        # window
        props = WindowProperties()
        self.win_size = 600
        props.setSize(self.win_size, self.win_size)
        self.base.win.requestProperties(props)
        # set lens so we can manipulate it.
        #lens = PerspectiveLens()
        # assume standard panda3d window
        #lens.setAspectRatio(600.0 / 600.0)
        # use stuff from pandaepl
        #lens.setFov(60)
        #lens.setNear(0.1)
        #self.base.cam.node().setLens(lens)
        # set up key
        self.accept("c", self.move_center)
        self.accept("b", self.plot_bananas)
        self.num_bananas = 10
        # total area is 100
        high_area = 0.25 * 0.33 * 100
        middle_area = 0.25 * 100
        self.high_radius = sqrt(high_area / pi)
        self.mid_radius = sqrt(middle_area / pi)
        self.high_reward = 6
        self.mid_reward = 4
        self.low_reward = 2
        print self.high_radius
        print self.mid_radius
        self.weight_center = (random.uniform(-5, 5), random.uniform(-5, 5))
        print('weight center', self.weight_center)
        self.banana_model = []
        self.center_model = None
        self.plot_border()
        self.plot_bananas()
        self.plot_circles()

    def plot_bananas(self):
        pos_list = []
        (x, y) = 0, 0
        avatar_pos = (0, 0)
        for i, j in enumerate(range(self.num_bananas)):
            #(x, y) = mB.setXY(pos_list, avatar_pos)
            print(x, y)
            pos_list.append((x, y))
            self.banana_model.append(self.base.loader.loadModel('ball'))
            self.banana_model[i].setPos(
                Point3(float(pos_list[i][0]), 25, float(pos_list[i][1])))
            self.banana_model[i].setScale(0.5)
            self.banana_model[i].setColor(1, 1, 0, 1)
            self.banana_model[i].reparentTo(self.base.render)
            (x, y) = x + 1 / 2, y + 1 / 2

    def plot_border(self):
        border = LineSegs()
        border.setThickness(2.0)
        corner = self.win_size/100 * 5/6
        print('corner', corner)
        border.move_to(corner, 25, corner)
        border.draw_to(corner, 25, -corner)
        border.draw_to(-corner, 25, -corner)
        border.draw_to(-corner, 25, corner)
        border.draw_to(corner, 25, corner)
        node = self.base.render.attach_new_node(border.create(True))

    def plot_circles(self):
        self.center_model = self.base.loader.loadModel('ball')
        self.center_model.setPos(self.weight_center[0], 25, self.weight_center[1])
        self.center_model.setScale(0.4)
        self.center_model.setColor(1, 0, 1, 1)
        self.center_model.reparentTo(self.base.render)

    def move_center(self):
        self.weight_center = (random.uniform(-5, 5), random.uniform(-5, 5))
        print('weight center', self.weight_center)
        self.plot_circles()

if __name__ == "__main__":
    BW = BananaWorld()
    BW.base.run()