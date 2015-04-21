from direct.showbase.ShowBase import ShowBase
from panda3d.core import PNMImage, Texture, CardMaker
from direct.task import Task
from math import pi, sin, cos


class ColorWorld(object):
    def __init__(self):
        self.base = ShowBase()
        self.base.camera.setPos(1, -20, 3)
        self.base.camera.setHpr(0.5, 0, 0)

        self.color_image = PNMImage(16, 16)
        self.color_image.fill(0, 1, 0)
        self.color_texture = Texture()
        self.color_texture.load(self.color_image)
        # test_texture = loader.loadTexture("models/waterfall.JPG")

        cm = CardMaker('card')
        card = self.base.render.attachNewNode(cm.generate())
        card.setTexture(self.color_texture)
        # card.setTexture(test_texture)
        card.setPos(-5, 0, 0)
        card.setScale(10)

        self.environ = self.base.loader.loadModel("models/round_courtyard2.bam")
        self.environ.reparentTo(self.base.render)
        self.environ.setPos(0, 0, 0)

        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.last = 0

        # Add the spinCameraTask procedure to the task manager.
        # self.base.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        self.base.camera.setPos(1, -20, 3)
        self.base.camera.setHpr(0.5, 0, 0)
        for r in range(self.color_image.getYSize()):
            row = self.color_image[r]
            print('row', row)
            for xelval in row:
                pass
        # angleDegrees = task.time * 6.0
        # angleRadians = angleDegrees * (pi / 180.0)
        # self.base.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        # self.base.camera.setHpr(angleDegrees, 0, 0)
        # print self.base.camera.getPos()
        # print self.base.camera.getH()
        return Task.cont

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.base.camera.setPos(1, -20, 3)
        self.base.camera.setHpr(0.5, 0, 0)
        #self.move_ball(dt)
        return task.cont


if __name__ == "__main__":
    CW = ColorWorld()
    CW.base.run()