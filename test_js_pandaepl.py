from pandaepl.common import *
from pandaepl import Joystick
from panda3d.core import LineSegs, Vec4
#from bananas import Bananas
from panda3d.core import WindowProperties


class TestJoystickPandaEPL:
    def __init__(self):
        """
        Initialize the experiment
        """
        # Get experiment instance.
        exp = Experiment.getInstance()
        #exp.setSessionNum(0)
        # Set session to today's date and time
        exp.setSessionNum(datetime.datetime.now().strftime("%y_%m_%d_%H_%M"))
        print exp.getSessionNum()
        #config = Conf.getInstance().getConfig()  # Get configuration dictionary.

        # get rid of cursor
        win_props = WindowProperties()
        #print win_props
        win_props.setCursorHidden(True)
        #win_props.setOrigin(20, 20)  # make it so windows aren't on top of each other
        #win_props.setSize(800, 600)  # normal panda window
        # base is global, used by pandaepl from panda3d
        base.win.requestProperties(win_props)

        # plotting stuff
        self.y_mag = 0
        self.x_mag = 0
        self.old_x = 0
        self.old_y = 0
        vr = Vr.getInstance()
        #self.banana_models = Bananas(config)
        self.js = Joystick.Joystick.getInstance()
        #print self.js
        vr.inputListen("close", self.close)
        # set up task to be performed between frames
        vr.addTask(Task("checkJS",
                            lambda taskInfo:
                            self.check_position()))

    def check_position(self):
        joy_in = self.js.getEvents()
        if joy_in:
            for axis_event in joy_in:
                print axis_event
                print axis_event['turnLeft']

                #if test[mag_test[0]] == 'moveForward':
                #    self.y_mag = test[mag_test[1]]
                #    print('forward', self.y_mag)
                #elif test[mag_test[0]] == 'moveBackward':
                #    self.y_mag = -test[mag_test[1]]
                #    print('backward', self.y_mag)
                #elif test[mag_test[0]] == 'moveRight':
                #    self.x_mag = test[mag_test[1]]
                #    print('right', self.x_mag)
                #elif test[mag_test[0]] == 'moveLeft':
                #    self.x_mag = -test[mag_test[1]]
                #    print('left', self.x_mag)
        plot_xy = LineSegs()
        plot_xy.setThickness(2.0)
        plot_xy.setColor(Vec4(1, 1, 0, 1))
        plot_xy.moveTo(self.old_x, 55, self.old_y)
        plot_xy.drawTo(self.x_mag, 55, self.y_mag)
        self.old_x = self.x_mag
        self.old_y = self.y_mag

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
