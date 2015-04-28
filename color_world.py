from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import ActorNode, Camera
from panda3d.core import WindowProperties, NodePath, LVector3, KeyboardButton
from panda3d.core import GeomNode, LineSegs
from color import make_square
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
        map_avatar = True
        if pygame:
            pygame.init()
            js_count = pygame.joystick.get_count()
        if js_count > 1:
            raise NotImplementedError("More than one Joystick is connected")
        elif js_count == 1:
            self.joystick = pygame.joystick.Joystick(0)
            print 'load joystick'
            self.joystick.init()
            print 'joystick open'
            print self.joystick.get_numaxes()
            # keep track of velocity, this allows me to counteract joystick with keyboard
            self.velocity = LVector3(0)
            # threshold for joystick
            self.threshold = 0.1
        print self.joystick
        # map avatar variables
        self.render2 = None
        self.render2d = None
        self.last_avt = [0, 0]
        self.map_avt_node = []
        # need a multiplier to the joystick output to tolerable speed
        self.vel_base = 3
        self.max_vel = [500, 500, 0]

        self.base = ShowBase()
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)
        self.base.disableMouse()

        if map_avatar:
            self.setup_display2()

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

        self.setup_inputs()
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.last = 0  # task time of the last frame
        # print 'end init'

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.poll_joystick()
        self.poll_keyboard()
        move = self.move_avatar(dt)
        self.move_map_avatar(move)
        return task.cont

    def poll_joystick(self):
        if not self.joystick:
            return
        # joystick input -1 to 1,
        # if I get the event, it only has a signal when
        # there is movement, so loop through the events,
        # to collect events into axis call, but call
        # axis after, since it will stay at whatever the
        # last signal was, instead of zeroing out whenever
        # no movement. Much more convenient that way.
        for ev in pygame.event.get():
            pass
        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)

        # if both are under threshold, assume noise
        # if one is deliberate, noise in the other won't affect much
        if -self.threshold < x < self.threshold and -self.threshold < y < self.threshold:
            # print 'threshold'
            # print 'x', x, 'y', y
            self.velocity.x = 0
            self.velocity.y = 0
        else:
            self.velocity.x = x
            self.velocity.y = -y

    def poll_keyboard(self):
        # under normal circumstances, use median of joytick output
        x_speed = 0.5
        y_speed = 0.5
        # checks keyboard, not mouse, in this case
        is_down = self.base.mouseWatcherNode.is_button_down
        # Instead of usual movement, exactly counteract joystick,
        # if using joystick and currently moving
        if self.joystick:
            if abs(self.velocity.x) > self.threshold:
                if self.velocity.x > 0:
                    x_speed = self.velocity.x
                else:
                    x_speed = -self.velocity.x
            if abs(self.velocity.y) > self.threshold:
                if self.velocity.y > 0:
                    y_speed = self.velocity.y
                else:
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
        move = None
        if self.velocity.normalize():
            # go left in increasing amount
            # print 'dt', dt
            # print 'normalized'
            # print 'velocity', self.velocity
            # print 'magnitude', magnitude
            self.velocity *= magnitude
            # print 'velocity', self.velocity
            # this makes for smooth movement
            move = self.velocity * self.vel_base * dt
            self.avatar.setFluidPos(self.avatar, move)
        return move

    def move_map_avatar(self, move):
        # print move
        if move:
            move *= 0.01
            avt = LineSegs()
            avt.setThickness(1)
            avt.setColor(1, 1, 1)
            # print 'last', self.last_avt
            avt.move_to(self.last_avt[0], 1, self.last_avt[1])
            new_move = [i + j for i, j in zip(self.last_avt, move)]
            # print 'new', new_move
            self.last_avt = [new_move[0], new_move[1]]
            avt.draw_to(new_move[0], 1, new_move[1])
            self.map_avt_node.append(self.render2d.attach_new_node(avt.create()))
            # can't let too many nodes pile up
            if len(self.map_avt_node) > 299:
                for i, j in enumerate(self.map_avt_node):
                    j.removeNode()
                    if i > 49:
                        break
                del self.map_avt_node[0:50]

    def setup_inputs(self):
        self.accept('q', self.close)

    def setup_display2(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setSize(400, 400)
        props.setOrigin(128, 128)
        window2 = self.base.openWindow(props=props, aspectRatio=1)
        self.render2 = NodePath('render2')
        camera = self.base.camList[-1]
        camera.reparentTo(self.render2)
        camera.setPos(0, -5, 0)
        square = make_square(-1, -1, -1, 1, -1, 1)
        sq_node = GeomNode('square')
        sq_node.addGeom(square)
        self.render2.attach_new_node(sq_node)
        print 'render2', self.render2
        self.render2d = NodePath('render2d')
        camera2d = self.base.makeCamera(window2)
        camera2d.reparentTo(self.render2d)
        # env = self.base.loader.loadModel('environment.egg')
        # env.reparentTo(self.render2)

    def close(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    CW = ColorWorld()
    CW.base.run()
