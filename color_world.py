from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import ActorNode
from panda3d.core import WindowProperties, NodePath, LVector3, KeyboardButton
import sys
try:
    import pygame
except ImportError:
    pygame = False
    print 'Pygame not found, necessary for joystick use'
# from direct.task import Task
# from panda3d.core import CardMaker
# from direct.gui.OnscreenImage import OnscreenImage


class ColorWorld(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        # joystick
        js_count = 0
        self.joystick = None
        if pygame:
            # try getting rid of one of the joystick inits
            pygame.init()
            pygame.joystick.init()
            js_count = pygame.joystick.get_count()
        if js_count > 1:
            code = "More than one joystick connected"
            raise NotImplementedError("More than one Joystick is connected")
        elif js_count == 1:
            self.joystick = pygame.joystick.Joystick(0)
            print 'load joystick'
            self.joystick.init()
            print 'joystick open'
            print self.joystick.get_numaxes()
            # with keyboard polling, I get a response as long as the key is pressed,
            # so I don't have to remember the state, but with the joystick, I only
            # get a signal if things change, so have to remember previous velocity
            self.velocity = LVector3(0)
            # threshold for joystick
            self.threshold = 0.1
        print self.joystick
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
        # self.vel = LVector3(0)
        # self.vel[1] = 4
        # print self.vel
        self.vel_base = 3
        self.max_vel = [500, 500, 0]
        self.setup_inputs()
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.last = 0  # task time of the last frame
        print 'end init'

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        # if joystick and keyboard are doing the opposite, counteract each other
        change = self.poll_joystick()
        #self.poll_keyboard(change)
        self.move_avatar(dt)
        return task.cont

    def poll_joystick(self):
        # joystick input -1 to 1,
        change = [False, False]
        if not self.joystick:
            return change
        make_zero = 0
        print 'new poll'
        print self.joystick.get_axis(0)
        print self.joystick.get_axis(1)
        # x = self.joystick.get_axis(0)
        # y = self.joystick.get_axis(1)
        # if -self.threshold > x < self.threshold and -self.threshold > y < self.threshold:
        #     x = 0
        #     y = 0
        # if self.velocity.x != x:
        #     change[0] = True
        #     self.velocity.x = x
        # if self.velocity == y:
        #     change[1] = True
        #     self.velocity.y = y

        for ev in pygame.event.get():
            if ev.type is pygame.JOYAXISMOTION and ev.axis < 2:
                change[ev.axis] = True
                # why does this go to zero when I hold the joystick in one place?!?!?
                print 'in loop', ev.value, ev.axis
                # initially set to exact numbers
                if ev.axis == 1:
                    self.velocity.y = -ev.value
                else:
                    self.velocity.x = ev.value
                # but if both x and y are under threshold, assume we are stopped
                if -self.threshold > ev.value < self.threshold:
                    # print 'make zero', make_zero
                    make_zero += 1
                    # if both are under threshold, set to zero.
                    if make_zero == 2:
                        #print 'stop'
                        self.velocity.x = 0
                        self.velocity.y = 0
        return change

    def poll_keyboard(self, change):
        x_speed = 0.5
        y_speed = 0.5
        is_down = self.base.mouseWatcherNode.is_button_down
        # exactly counteract joystick, if used
        if change[0]:
            x_speed = -self.velocity.x
        if change[1]:
            y_speed = -self.velocity.y

        if is_down(KeyboardButton.up()):
            self.velocity.y += y_speed
        if is_down(KeyboardButton.down()):
            self.velocity.y -= y_speed
        if is_down(KeyboardButton.left()):
            self.velocity.x -= x_speed
            # print 'keyboard'
        if is_down(KeyboardButton.right()):
            self.velocity.x += x_speed

    def move_avatar(self, dt):
        # print self.velocity
        # this makes for smooth (correct speed) diagonal movement
        # print 'velocity', self.velocity
        magnitude = max(abs(self.velocity[0]), abs(self.velocity[1]))
        if self.velocity.normalize():
            # go left in increasing amount
            # print 'dt', dt
            # print 'normalized'
            # print 'velocity', self.velocity
            # print 'magnitude', magnitude
            self.velocity *= magnitude
            # print 'velocity', self.velocity
            # this makes for smooth movement
            self.avatar.setFluidPos(self.avatar, self.velocity * self.vel_base * dt)
            # x, y, z = [dt * i for i in self.vel]
            # pos = Vec3(x, y, z)
            # print pos
            # self.avatar.setFluidPos(self.avatar, pos)

    # def set_move(self, js_dir, magnitude):
    #     # print(js_dir, magnitude)
    #     # Threshold. If too low, noise will create movement.
    #     if abs(magnitude) < 0.1:
    #         magnitude = 0
    #     x_mag = 0
    #     y_mag = 0
    #     # we are moving the camera in the opposite direction of the joystick,
    #     # x and y inputs will both be inverted
    #     if js_dir == 'x' or js_dir == 'x_key':
    #         # print js_input
    #         # x direction
    #         x_mag = magnitude
    #         # print('x_mag', self.x_mag)
    #     else:
    #         # y direction is reversed,
    #         y_mag = -magnitude
    #     new_vel = [x_mag, y_mag, 0]
    #     # print new_vel
    #     # all velocities multiplied by base
    #     # if a velocity is greater than its max, velocity is max
    #     for i, j in enumerate(new_vel):
    #         self.vel[i] = j * self.vel_base
    #         if self.vel[i] > self.max_vel[i]:
    #             self.vel[i] = self.max_vel[i]

    def setup_inputs(self):
        # self.accept('x_axis', self.set_move, ['x'])
        # self.accept('y_axis', self.set_move, ['y'])
        # self.accept('arrow_right', self.set_move, ['x_key', 0.5])
        # self.accept('arrow_left', self.set_move, ['x_key', -0.5])
        # self.accept('arrow_right-up', self.set_move, ['x_key', 0])
        # self.accept('arrow_left-up', self.set_move, ['x_key', 0])
        # self.accept('arrow_right-repeat', self.set_move, ['x_key', 0.5])
        # self.accept('arrow_left-repeat', self.set_move, ['x_key', -0.5])
        # self.accept('arrow_up', self.set_move, ['y_key', -0.5])
        # self.accept('arrow_up-up', self.set_move, ['y_key', 0])
        # self.accept('arrow_up-repeat', self.set_move, ['y_key', -0.5])
        # self.accept('arrow_down', self.set_move, ['y_key', 0.5])
        # self.accept('arrow_down-up', self.set_move, ['y_key', 0])
        # self.accept('arrow_down-repeat', self.set_move, ['y_key', 0.5])
        self.accept('q', self.close)

    def close(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    CW = ColorWorld()
    CW.base.run()
