from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.task import Task
from math import pi, sin, cos
from panda3d.core import CardMaker
#from direct.gui.OnscreenImage import OnscreenImage


class ColorWorld(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.base = ShowBase()
        self.base.disableMouse()
        courtyard = self.base.loader.loadModel('../goBananas/models/play_space/round_courtyard.bam')
        courtyard.reparentTo(self.base.render)
        courtyard.setPos(0, 0, 0)
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.last = 0  # task time of the last frame

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.move_avatar(dt)

    def move_avatar(self, dt):


    def set_move(self, js_dir, magnitude):
        # Threshold. If too low, noise will create movement.
        if abs(magnitude) < 0.1:
            magnitude = 0
        # we are moving the camera in the opposite direction of the joystick,
        # x and y inputs will both be inverted
        if js_dir == 'x' or js_dir == 'x_key':
            # print js_input
            # x direction is reversed
            self.x_mag = -magnitude
            # print('x_mag', self.x_mag)
        else:
            # y direction is also reversed,
             self.y_mag = -js_input


    def setup_inputs(self):
        self.accept('x_axis', self.set_move, ['x'])
        self.accept('y_axis', self.set_move, ['y'])
        self.accept('arrow_right', self.set_move, ['x_key', 0.5])
        self.accept('arrow_left', self.set_move, ['x_key', -0.5])
        self.accept('arrow_right-up', self.set_move, ['x_key', 0])
        self.accept('arrow_left-up', self.set_move, ['x_key', 0])
        self.accept('arrow_right-repeat', self.set_move, ['x_key', 0.5])
        self.accept('arrow_left-repeat', self.set_move, ['x_key', -0.5])
        self.accept('arrow_up', self.set_move, ['y_key', -0.5])
        self.accept('arrow_up-up', self.set_move, ['y_key', 0])
        self.accept('arrow_up-repeat', self.set_move, ['y_key', -0.5])
        self.accept('q', self.close)

if __name__ == "__main__":
    CW = ColorWorld()
    CW.base.run()
