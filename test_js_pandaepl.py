from pandaepl.common import *
from pandaepl import Joystick
from panda3d.core import LineSegs, Vec4
from panda3d.core import WindowProperties
import sys
try:
    sys.path.insert(1, '../goBananas')
    from bananas import Bananas
    from load_models import PlaceModels, load_models
except ImportError:
    print 'need to load Bananas'
    sys.exit()


#import inspect


class TestJoystickPandaEPL:
    def __init__(self):
        """
        Initialize the experiment
        """
        # Get experiment instance.
        exp = Experiment.getInstance()
        #exp.setSessionNum(0)
        # true for x vs y, false for xy vs t
        self.plot_choice_xy = False
        # Set session to today's date and time
        exp.setSessionNum(datetime.datetime.now().strftime("%y_%m_%d_%H_%M"))
        print exp.getSessionNum()
        #config = Conf.getInstance().getConfig()  # Get configuration dictionary.
        # Models must be attached to self
        #self.envModels = []
        #self.load_environment(config)
        #self.bananas = Bananas(config)
        # get rid of cursor
        win_props = WindowProperties()
        #print win_props
        win_props.setCursorHidden(True)
        #win_props.setOrigin(20, 20)  # make it so windows aren't on top of each other
        #win_props.setSize(800, 600)  # normal panda window
        # base is global, used by pandaepl from panda3d
        base.win.requestProperties(win_props)
        self.now = 0
        self.gain = 0.3
        self.offset = 0.5
        # plotting stuff
        self.y_mag = -self.offset
        self.x_mag = self.offset
        # render2d starts at -1 on left
        self.time = -1
        self.old_x = 0
        self.old_y = 0
        self.plot = []
        self.plot_zero_lines()
        vr = Vr.getInstance()
        #self.banana_models = Bananas(config)
        self.js = Joystick.Joystick.getInstance()
        #print self.js
        vr.inputListen("close", self.close)
        vr.inputListen("change_axis", self.change_axis)
        # set up task to be performed between frames
        vr.addTask(Task("checkJS",
                            lambda taskInfo:
                            self.plot_position()))

    def plot_position(self):
        if self.plot_choice_xy:
            self.plot_xy()
        else:
            self.plot_xy_vs_t()

    def plot_xy(self):
        joy_in = self.js.getEvents()
        if joy_in:
            #print type(joy_in)
            for event_name in joy_in:
                #print event_name
                event = joy_in[event_name]
                #print event
                #print type(event)
                #print inspect.getmembers(event, predicate=inspect.ismethod)
                event_mag = event.getMagnitude()
                if event_name == 'moveForward':
                    self.y_mag = event_mag
                    print('forward', self.y_mag)
                elif event_name == 'moveBackward':
                    self.y_mag = -event_mag
                    print('backward', self.y_mag)
                elif event_name == 'turnRight':
                    self.x_mag = event_mag
                    print('right', self.x_mag)
                elif event_name == 'turnLeft':
                    self.x_mag = -event_mag
                    print('left', self.x_mag)
            plot_xy = LineSegs()
            plot_xy.setThickness(2.0)
            plot_xy.setColor(Vec4(1, 1, 0, 1))
            plot_xy.moveTo(self.old_x, 0, self.old_y)
            plot_xy.drawTo(self.x_mag, 0, self.y_mag)
            base.render2d.attach_new_node(plot_xy.create(True))
            self.old_x = self.x_mag
            self.old_y = self.y_mag

    def plot_xy_vs_t(self):
        then = self.now
        if self.now == 0:
            then = time.time()
        self.now = time.time()
        #print self.now
        dt = (self.now - then) / 10
        joy_in = self.js.getEvents()
        if joy_in:
            #print type(joy_in)
            for event_name in joy_in:
                #print event_name
                event = joy_in[event_name]
                #print event
                #print type(event)
                #print inspect.getmembers(event, predicate=inspect.ismethod)
                event_mag = event.getMagnitude()
                if event_name == 'moveForward':
                    y_mag = event_mag
                    #print('forward', y_mag)
                    self.y_mag = (y_mag * self.gain) - self.offset
                    #print('forward', self.y_mag)
                elif event_name == 'moveBackward':
                    y_mag = -event_mag
                    #print('backward', y_mag)
                    self.y_mag = (y_mag * self.gain) - self.offset
                    #print('backward', self.y_mag)
                elif event_name == 'turnRight':
                    x_mag = event_mag
                    #print('right', x_mag)
                    self.x_mag = (x_mag * self.gain) + self.offset
                    #print('right', self.x_mag)
                elif event_name == 'turnLeft':
                    x_mag = -event_mag
                    #print('left', x_mag)
                    self.x_mag = (x_mag * self.gain) + self.offset
                    #print('left', self.x_mag)
        plot_x = LineSegs()
        plot_x.setThickness(2.0)
        plot_x.setColor(Vec4(1, 1, 0, 1))
        plot_x.moveTo(self.time, 0, self.old_x)

        plot_y = LineSegs()
        plot_y.setThickness(2.0)
        plot_y.setColor(Vec4(1, 0, 0, 1))
        plot_y.moveTo(self.time, 0, self.old_y)

        self.time += dt
        #print('dt', dt)
        #print('time', self.time)
        plot_x.drawTo(self.time, 0, self.x_mag)
        node = base.render2d.attach_new_node(plot_x.create(True))
        self.plot.append(node)
        plot_y.drawTo(self.time, 0, self.y_mag)
        node = base.render2d.attach_new_node(plot_y.create(True))
        self.plot.append(node)
        self.old_x = self.x_mag
        self.old_y = self.y_mag
        if self.time > 1:
            self.clear_plot()

    def clear_plot(self):
        for seg in self.plot:
            seg.removeNode()
        self.plot = []
        self.time = -1

    def plot_zero_lines(self):
        plot_zero = LineSegs()
        plot_zero.setThickness(2.0)
        plot_zero.setColor(Vec4(1, 0, 1, 1))
        plot_zero.moveTo(-1, 0, self.x_mag)
        plot_zero.drawTo(1, 0, self.x_mag)
        plot_zero.moveTo(-1, 0, self.y_mag)
        plot_zero.drawTo(1, 0, self.y_mag)
        base.render2d.attach_new_node(plot_zero.create(True))

    def load_environment(self, config):
        load_models()
        #print config['environ']
        for item in PlaceModels._registry:
            #print item.group
            #print item.name
            if config['environ'] in item.group:
            #if 'better' in item.group:
                #print item.name
                item.model = config['path_models'] + item.model
                #print item.model
                model = Model(item.name, item.model, item.location)
                if item.callback is not None:
                    #print 'not none'
                    model.setCollisionCallback(eval(item.callback))
                    # white wall is bright, and sometimes hard to see bananas,
                    # quick fix.
                    model.nodePath.setColor(0.8, 0.8, 0.8, 1.0)
                model.setScale(item.scale)
                model.setH(item.head)
                self.envModels.append(model)

    def change_axis(self):
        self.plot_choice_xy = not self.plot_choice_xy

    def start(self):
        """
        Start the experiment.
        """
        #print 'start'
        Experiment.getInstance().start()

    def close(self, inputEvent):
        Experiment.getInstance().stop()

if __name__ == '__main__':
    TestJoystickPandaEPL().start()
else:
    pass
