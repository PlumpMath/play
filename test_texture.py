from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.task import Task
from math import pi, sin, cos
from panda3d.core import CardMaker
#from direct.gui.OnscreenImage import OnscreenImage


class FakeWorld(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.base = ShowBase()
        #courtyard = loader.loadModel('../panda_eggs/square_courtyard.egg')
        #courtyard.reparentTo(self.base.render)
        #myTexture = loader.loadTexture("textures/square_courtyard_fill.tga")
        #tex = loader.loadTexture('maps/noise.rgb')
        #courtyard.setTexture(tex, 1)

        #butterfly = loader.loadModel('../panda_eggs/butterfly.egg')
        #butterfly.reparentTo(self.base.render)
        #butterfly.setPos(0, 15, 1)
        #butterfly.setPos(0, 0, 1)
        #butterfly.setScale(0.05)

        # Add the spinCameraTask procedure to the task manager.
        #self.base.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        self.butterfly = Actor('models/butterfly.egg', {
            'fly': 'models/butterfly_animate.egg'
        })
        self.butterfly.reparentTo(self.base.render)
        self.butterfly.setPos(0, 15, 1)
        self.butterfly.setScale(0.05, 0.05, 0.05)
        #self.butterfly.play('fly')
        self.butterfly.loop('fly')
        #self.butterfly.pose('fly', 20)
        print self.butterfly.getNumFrames('fly')
        print self.butterfly.getCurrentAnim()
        print self.butterfly.getCurrentFrame()
        # imageObject = OnscreenImage(image='textures/square_courtyard_fill.tga')
        #cm = CardMaker('card')
        #card = self.base.render.attachNewNode(cm.generate())
        #card.setTexture(myTexture)
        # smiley = loader.loadModel('smiley.egg')
        # smiley.setPos(0, 0, 10)
        # smiley.reparentTo(self.base.render)

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.base.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.base.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont

if __name__ == "__main__":
    FW = FakeWorld()
    FW.base.run()
