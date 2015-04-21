from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import ActorNode
from panda3d.core import WindowProperties, NodePath, Vec3, LVector3
import sys
# from direct.task import Task
# from panda3d.core import CardMaker
# from direct.gui.OnscreenImage import OnscreenImage


class ColorWorld(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.base = ShowBase()
        # Hide mouse
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)
        self.base.disableMouse()

        courtyard = self.base.loader.loadModel('../goBananas/models/play_space/round_courtyard.bam')
        courtyard.reparentTo(self.base.render)
        courtyard.setPos(0, 0, 0)

        # create the avatar
        self.avatar = NodePath(ActorNode("avatar"))
        self.avatar.reparentTo(self.base.render)
        self.avatar.setH(self.base.camera.getH())
        self.base.camera.reparentTo(self.avatar)
        self.base.camera.setPos(0, 0, 0)
        self.avatar.setPos(-10, -10, 2)

        # self.vel = [0, 0, 0]
        # values from joystick are 0 to 1, need to make
        # larger range
        self.vel = LVector3(0)
        self.vel_base = 10
        self.max_vel = [500, 500, 0]
        self.setup_inputs()
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.last = 0  # task time of the last frame

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.move_avatar(dt)
        return task.cont

    def move_avatar(self, dt):
        # print self.vel
        # this makes for smooth (correct speed) diagonal movement
        if self.vel.normalize():
            # this makes for smooth movement
            self.avatar.setFluidPos(self.avatar, self.vel * dt)
        # x, y, z = [dt * i for i in self.vel]
        # pos = Vec3(x, y, z)
        # print pos
        # self.avatar.setFluidPos(self.avatar, pos)

    def set_move(self, js_dir, magnitude):
        # print(js_dir, magnitude)
        # Threshold. If too low, noise will create movement.
        if abs(magnitude) < 0.1:
            magnitude = 0
        x_mag = 0
        y_mag = 0
        # we are moving the camera in the opposite direction of the joystick,
        # x and y inputs will both be inverted
        if js_dir == 'x' or js_dir == 'x_key':
            # print js_input
            # x direction
            x_mag = magnitude
            # print('x_mag', self.x_mag)
        else:
            # y direction is reversed,
            y_mag = -magnitude
        new_vel = [x_mag, y_mag, 0]
        # print new_vel
        # all velocities multiplied by base
        # if a velocity is greater than its max, velocity is max
        for i, j in enumerate(new_vel):
            self.vel[i] = j * self.vel_base
            if self.vel[i] > self.max_vel[i]:
                self.vel[i] = self.max_vel[i]


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
        self.accept('arrow_down', self.set_move, ['y_key', 0.5])
        self.accept('arrow_down-up', self.set_move, ['y_key', 0])
        self.accept('arrow_down-repeat', self.set_move, ['y_key', 0.5])
        self.accept('q', self.close)

    def close(self):
        sys.exit()

if __name__ == "__main__":
    CW = ColorWorld()
    CW.base.run()
