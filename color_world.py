from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import ActorNode, Camera
from panda3d.core import WindowProperties, NodePath, LVector3, KeyboardButton
from panda3d.core import GeomNode, LineSegs
from color import make_square, make_color_vertices
import sys
try:
    import pygame
except ImportError:
    pygame = False
    print 'Pygame not found, necessary for joystick use'
# from direct.task import Task
# from panda3d.core import CardMaker
# from direct.gui.OnscreenImage import OnscreenImage


def make_color_map(colors):
    # colors is a list that corresponds to (x, y, z) so
    # ('b', 'r') means blue varies with x, and red with y
    # this is a 2 dimensional space, so z corresponds to varies
    # with both x and y
    #
    # output is a dictionary, that shows mapping from x,y,z space to color space
    # second output is a list of which corresponds to (r,g,b) so if colors was ('b', 'g')
    # axis_keys will be (None, 1, 0) because red is not changing, green is changing with y,
    # and blue is changing with x. color_map would be {'x_axis': 2, 'y_axis': 1, 'z_axis': None,
    # 0: None, 1: 1, 2: 0}
    # r: None, g: y, b: x
    axis_map = ['x_axis', 'y_axis', 'z_axis']
    color_map = {'x_axis': None, 'y_axis': None, 'z_axis': None, 0: None, 1: None, 2: None}
    # color_map = [None, None, None]
    axis_keys = [None, None, None]
    for i, j in enumerate(colors):
        if j == 'r':
            axis_keys[0] = i
            color_map[axis_map[i]] = 0
            color_map[0] = i
            # color_map[0] = axis_map[i]
        elif j == 'g':
            axis_keys[1] = i
            color_map[axis_map[i]] = 1
            color_map[1] = i
            # color_map[1] = axis_map[i]
        elif j == 'b':
            axis_keys[2] = i
            color_map[axis_map[i]] = 2
            color_map[2] = i
            # color_map[2] = axis_map[i]
    return color_map, axis_keys


class ColorWorld(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        # joystick
        js_count = 0
        self.joystick = None
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
            # threshold for joystick
            self.threshold = 0.1
        print self.joystick
        # keep track of velocity, this allows me to counteract joystick with keyboard
        self.velocity = LVector3(0)
        config = {}
        execfile('color_config.py', config)
        # starting position is middle of space.
        pos = config['variance'][0] + (config['variance'][1] - config['variance'][0])/2
        self.color_list = [pos, pos, pos]

        # self.color_map always corresponds to (r, g, b)
        self.color_dict, axis_keys = make_color_map(config['colors'])
        for i, j in enumerate(axis_keys):
            if j is None:
                self.color_list[i] = config['static']

        # self.color_list = [config['static'] if i is None else i for i in axis_keys]
        print 'start color',  self.color_list

        # start_map = [config['static'] if i is None else i for i in self.color_map]
        self.variance = config['variance']
        # map avatar variables
        self.render2 = None
        self.render2d = None
        self.last_avt = [0, 0]
        self.map_avt_node = []
        # need a multiplier to the joystick output to tolerable speed
        self.vel_base = 3
        self.max_vel = [500, 500, 0]

        self.base = ShowBase()
        self.base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        print config.get('resolution')
        if config.get('resolution'):
            props.set_size(int(config['resolution'][0]), int(config['resolution'][1]))
            props.set_origin(0, 0)
        else:
            props.set_size(600, 600)
            props.set_origin(400, 50)
        self.base.win.requestProperties(props)
        print self.base.win.get_size()
        sq_node = self.setup_square(config)
        self.setup_display2(sq_node, config)

        # courtyard = self.base.loader.loadModel('../goBananas/models/play_space/round_courtyard.bam')
        # courtyard.reparentTo(self.base.render)
        # courtyard.setPos(0, 0, 0)

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
        self.base.setBackgroundColor(self.color_list[:])
        # print 'end init'

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.poll_joystick()
        self.poll_keyboard()
        move = self.move_avatar(dt)
        stop = self.change_background(move)
        self.move_map_avatar(move, stop)

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
        else:
            self.velocity.x = 0
            self.velocity.y = 0
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
        # print 'velocity', self.velocity
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
            # print move
            self.avatar.setFluidPos(self.avatar, move)
        return move

    def change_background(self, move):
        stop = [False, False]
        if move:
            #move *= 0.003
            move *= 0.1
            # colors map to x and y, blue changes with both x and y
            # print('r,g,b', self.red, self.green, self.blue)
            # print('move', move)
            # self.blue -= move[0]
            # print self.color_list
            # print 'should change by ', move
            self.color_list[self.color_dict['x_axis']] += move[0]
            self.color_list[self.color_dict['y_axis']] += move[1]

            # self.blue -= move[1]
            # print('r,g,b', self.red, self.green, self.blue)
            for i, j in enumerate(self.color_list):
                if self.color_dict[i] is None:
                    continue
                if j < self.variance[0]:
                    self.color_list[i] = self.variance[0]
                    # stop corresponds to x and y
                    stop[self.color_dict[i]] = True
                    # print('min')
                if j > self.variance[1]:
                    self.color_list[i] = self.variance[1]
                    stop[self.color_dict[i]] = True
                    # print('max')
            # print self.color_list[:]
            self.base.setBackgroundColor(self.color_list[:])
            # print self.base.getBackgroundColor()
        return stop

    def move_map_avatar(self, move, stop):
        # print move
        if move:
            avt = LineSegs()
            avt.setThickness(1)
            avt.setColor(1, 1, 1)
            # print 'last', self.last_avt
            avt.move_to(self.last_avt[0], 1, self.last_avt[1])
            new_move = [i + j for i, j in zip(self.last_avt, move)]
            if stop[0]:
                new_move[0] = self.last_avt[0]
            if stop[1]:
                new_move[1] = self.last_avt[1]
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

    def setup_display2(self, display_node, config):
        props = WindowProperties()
        props.setCursorHidden(True)
        if config.get('resolution'):
            props.setSize(750, 750)
            props.setOrigin(-int(config['resolution'][0]), 0)
        else:
            props.setSize(300, 300)
            props.setOrigin(10, 10)
        window2 = self.base.openWindow(props=props, aspectRatio=1)
        self.render2 = NodePath('render2')
        camera = self.base.camList[-1]
        camera.reparentTo(self.render2)
        camera.setPos(0, -5, 0)
        self.render2.attach_new_node(display_node)
        print 'render2', self.render2
        self.render2d = NodePath('render2d')
        camera2d = self.base.makeCamera(window2)
        camera2d.reparentTo(self.render2d)

    def setup_square(self, config):
        sq_colors = make_color_vertices(config)
        square = make_square(sq_colors)
        sq_node = GeomNode('square')
        sq_node.addGeom(square)
        return sq_node

    def close(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    CW = ColorWorld()
    CW.base.run()
