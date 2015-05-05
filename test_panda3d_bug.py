from __future__ import division
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Point3
from panda3d.core import OrthographicLens
from panda3d.core import WindowProperties
import sys


class World(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.base = ShowBase()
        resolution = (1024, 768)
        wp = WindowProperties()
        wp.setSize(int(resolution[0]), int(resolution[1]))
        wp.setOrigin(0, 0)
        self.base.win.requestProperties(wp)
        # depth completely doesn't matter for this, since just 2d, and no layers
        self.depth = 0
        self.base.setBackgroundColor(115 / 255, 115 / 255, 115 / 255)
        # set up a 2d camera
        camera = self.base.camList[0]
        lens = OrthographicLens()
        lens.setFilmSize(int(resolution[0]), int(resolution[1]))
        lens.setNearFar(-100, 100)
        camera.node().setLens(lens)
        camera.reparentTo(self.base.render)
        self.accept("escape", sys.exit)
        # spread out some positions
        self.positions = [(-200, 0, -200),
                          (0, 0, -200),
                          (200, 0, -200),
                          (-200, 0, 0),
                          (0, 0, 0),
                          (200, 0, 0),
                          (-200, 0, 200),
                          (0, 0, 200),
                          (200, 0, 200)]
        self.all_smiles()

    def next_smile(self, index):
        pos = self.positions[index]
        smiley = loader.loadModel('smiley.egg')
        smiley.setPos(Point3(pos))
        smiley.setScale(20)
        smiley.reparentTo(self.base.render)
        print smiley.getPos()

    def all_smiles(self):
        for ind in range(9):
            self.next_smile(ind)


if __name__ == "__main__":
    W = World()
    W.base.run()


