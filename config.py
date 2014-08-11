# change individual config files, and have script copy to config.py
# configuration file for goBananas
from panda3d.core import Point3, Point4

environ = 'original'
manual = True
numBananas = 2
bananaRepeat = False
repeatNumber = 0
path_models = '../goBananas/'
bananaDir = '../goBananas/models/bananas/'
# Load 2 bananas for testing, know where they are!
# (no effect if manual False)
bananaModel = '../goBananas/models/bananas/banana.bam'
posBananas = [[-5, 0], [0, -5]]
#bananaLoc = Point3(-10, 0, 1)
bananaScale = 1
bananaH = 0
#bananaLoc2 = Point3(0, -10, 1)
#posBananas = [bananaLoc, bananaLoc2]
# stuff so mobananas works
tooClose = 1
avatarRadius = 0.2
minXDistance = -10
maxXDistance = 10
minYDistance = -10
maxYDistance = 10

#### Core PandaEPL settings ####

FOV = 60

# Movement
linearAcceleration = 30
fullForwardSpeed = 2.8
fullBackwardSpeed = 0
turningAcceleration = 130
fullTurningSpeed = 55
# turningLinearSpeed = 2
# maxTurningLinearSpeed = 90.0
# minTurningLinearSpeedReqd = 1.0
# minTurningLinearSpeed = 1.5
# minTurningLinearSpeedIncrement = 0.5

# Point3 is global from panda3d.core
initialPos = Point3(0, 0, 1)

# If you want to collide with bananas at a closer or 
# further distance, change this, but does no good if 
# thing running into has huge radius
#avatarRadius = 0.3
#avatarRadius = 0.2

cameraPos = Point3(0, 0, 0)
friction = 0.4  # 0.4
movementType = 'walking'  # car | walking

#instructSize = 0.1
#instructFont = '/c/Windows/Fonts/times.ttf'
#instructBgColor = Point4(0, 0, 0, 1)
#instructFgColor = Point4(1, 1, 1, 1)
#instructMargin = 0.06
#instructSeeAll = False

# (Non-default) command keys.
# Keyboard is global from pandaepl.common
if 'Keyboard' in globals():
    keyboard = Keyboard.getInstance()
    keyboard.bind("change_axis", "space")
    keyboard.bind("close", ["escape", "q"])
    keyboard.bind("restart", "y")
    keyboard.bind("toggleDebug", ["escape", "d"])
