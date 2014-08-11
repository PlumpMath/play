from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText, TextNode
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerQueue, CollisionNode, BitMask32
from panda3d.core import CollisionPlane, CollisionSphere, CollisionRay
from panda3d.core import Plane, Vec3, Point3
 
 
class World(DirectObject):
 
    def __init__(self):
        # Create a traverser that Panda3D will automatically use every frame.
        base.cTrav = CollisionTraverser()
        # Create a handler for the events.
        self.collHandler = CollisionHandlerQueue()
 
        # use one bitmast for smiley, change whether from mask is on 
        # frowney or ray, so frowney and ray change from mask between 
        # noMask and good mask
        self.goodMask = BitMask32(0x1)
        self.noMask = BitMask32(0x0)
        
        # Start with checking collisions between smiley and frowney
        # (0 is ray, 1 is frowney)
        self.maskList = ["ray", "frowney", "both"]
        self.maskPosition = 0
        # Create a collision sphere. Since the models we'll be colliding
        # are basically the same we can get away with just creating one
        # collision solid and adding the same solid to both collision nodes.
        collSphere = CollisionSphere(0, 0, 0, 1.5)
 
        # Make a smiley.
        smiley = loader.loadModel('smiley')
        smiley.reparentTo(render)
        smiley.setPos(-3, 3, 3)
        smiley.setName("Smiley")
        smileyCollisionNP = self.makeCollisionNodePath(smiley, collSphere)
        # Like with the floor plane we need to set the into mask.
        # Here we shortcut getting the actual collision node.
        smileyCollisionNP.node().setIntoCollideMask(self.goodMask)
        self.smileyCollisionNode = smileyCollisionNP.node()
 
        # Make a frowney.
        frowney = loader.loadModel('frowney')
        frowney.reparentTo(render)
        frowney.setPos(-3, 3, 5.5)
        frowney.setName("Frowney")
        frowneyCollisionNP = self.makeCollisionNodePath(frowney, collSphere)
        # Set a from mask for frowney so we can change whether we are looking
        # for collisions from frowney or ray
        self.frowneyCollisionNode = frowneyCollisionNP.node()
        # set into mask so never collides with frowney
        self.frowneyCollisionNode.setIntoCollideMask(0)
        # start with frowney not colliding with smiley
        self.frowneyCollisionNode.setFromCollideMask(self.noMask)
        # add frowney to collider
        base.cTrav.addCollider(frowneyCollisionNP, self.collHandler)
        
        # Note that we didn't set a from collide mask for previous objects
        # since we're not adding them to the traverser as from objects.
 
        # Make a collision ray that passes through all of the objects.
        self.pointerNode = render.attachNewNode("Main Collider")
        self.pointerNode.setPos(-3, 3, 10)
        # Create a ray collision solid that points downwards.
        raySolid = CollisionRay(0, 0, 0, 0, 0, -1)
        mainCollisionNP = self.makeCollisionNodePath(self.pointerNode, raySolid)
        self.mainCollisionNode = mainCollisionNP.node()
        # rays can't be into objects, so don't worry about into mask
        self.mainCollisionNode.setIntoCollideMask(0)
        # Set a from collide mask for this ray so that we can selectively
        # collide against the other objects. Start with ray colliding
        # with smiley
        self.mainCollisionNode.setFromCollideMask(self.goodMask)
        base.cTrav.addCollider(mainCollisionNP, self.collHandler)
 
        # Set up the camera.
        base.disableMouse()
        base.camera.setPos(20, -20, 5)
        base.camera.lookAt(0, 0, 5)
        # Debug mode for collision traversers; shows collisions visually.
        base.cTrav.showCollisions(render)
        
        #mainCollisionNP.show()
        #frowneyCollisionNP.show()
        #smileyCollisionNP.show()

        #print('ray', self.mainCollisionNode.getFromCollideMask())
        #print('smiley', self.smileyCollisionNode.getIntoCollideMask())
        #print('frowney', self.frowneyCollisionNode.getFromCollideMask())

        # Setup the title text.
        collideText = self.maskList[self.maskPosition]
        self.title = OnscreenText(text="Colliding with %s" % (collideText),
                                  mayChange=True,
                                  pos=(0.3, 0),
                                  align=TextNode.ALeft,
                                  fg=(1, 1, 1, 1))
        OnscreenText(text="Press space to change collision mask",
                     pos=(0, 0.8),
                     fg=(1,1,1,1))
 
        # Set space to change the from collision mask of the collision ray.
        base.accept("space", self.switchCollisionMask)
 
    def makeCollisionNodePath(self, nodepath, solid):
        '''
        Creates a collision node and attaches the collision solid to the
        supplied NodePath. Returns the nodepath of the collision node.
 
        '''
        # Creates a collision node named after the name of the NodePath.
        collNode = CollisionNode("%s c_node" % nodepath.getName()) 
        collNode.addSolid(solid)
        collisionNodepath = nodepath.attachNewNode(collNode)
        # Show the collision node, which makes the solids show up.
        collisionNodepath.show()
 
        return collisionNodepath
 
    def switchCollisionMask(self):
        #base.cTrav.traverse(render)
        # need a way to see who has noMask and who has goodMask,
        # then reverse them.
        # maskPosition 0 for ray, 1 for frowney
        
        self.title.setText("Colliding with %s" % (self.maskList[self.maskPosition]))
        print('ray', self.mainCollisionNode.getFromCollideMask())
        print('smiley', self.smileyCollisionNode.getIntoCollideMask())
        print('frowney', self.frowneyCollisionNode.getFromCollideMask())
        for i in range(self.collHandler.getNumEntries()):
            entry = self.collHandler.getEntry(i)
            print entry
        # change for next round
        if self.maskPosition == 0:
            # switch from ray to frowney
            self.mainCollisionNode.setFromCollideMask(self.noMask)
            self.frowneyCollisionNode.setFromCollideMask(self.goodMask)
            self.maskPosition = 1
        elif self.maskPosition == 1:
            # switch from frowney to both
            self.mainCollisionNode.setFromCollideMask(self.goodMask)
            self.frowneyCollisionNode.setFromCollideMask(self.goodMask)
            self.maskPosition = 2
        else:
            # switch from both back to ray
            self.mainCollisionNode.setFromCollideMask(self.goodMask)
            self.frowneyCollisionNode.setFromCollideMask(self.noMask)
            self.maskPosition = 0

ShowBase()
world = World()
run()
