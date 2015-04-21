from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, CardMaker, Plane, Vec3, Point3, BitMask32
from panda3d.core import CollisionTraverser, CollisionNode, CollisionPlane, CollisionSphere
from panda3d.core import LRotationf, TextureStage, VBase3
from panda3d.physics import ForceNode, LinearVectorForce, ActorNode, PhysicsCollisionHandler
import random


class Fountain(object):

    def __init__(self):
        self.base = ShowBase()
        self.thrust = 0.5
        self.wind = 0.2

        self.UP = Vec3(0, 0, 1)  # might as well just make this a variable
        # set up camera
        self.base.disableMouse()
        self.base.camera.setPos(20, -20, 5)
        self.base.camera.lookAt(0, 0, 5)

        # Set up the collision traverser.  If we bind it to base.cTrav, then Panda will handle
        # management of this traverser (for example, by calling traverse() automatically for us once per frame)
        self.base.cTrav = CollisionTraverser()

        # Now let's set up some collision bits for our masks
        self.ground_bit = 1
        self.ball_bit = 2

        self.base.setBackgroundColor(0.64, 0, 0)
        # First, we build a card to represent the ground
        cm = CardMaker('ground-card')
        cm.setFrame(-60, 60, -60, 60)
        card = self.base.render.attachNewNode(cm.generate())
        card.lookAt(0, 0, -1)  # align upright
        #tex = loader.loadTexture('maps/envir-ground.jpg')
        tex = loader.loadTexture('models/textures/rock12.bmp')
        card.setTexture(tex)

        # Then we build a collisionNode which has a plane solid which will be the ground's collision
        # representation
        groundColNode = card.attachNewNode(CollisionNode('ground-cnode'))
        groundColPlane = CollisionPlane(Plane(Vec3(0, -1, 0), Point3(0, 0, 0)))
        groundColNode.node().addSolid(groundColPlane)

        # Now, set the ground to the ground mask
        groundColNode.setCollideMask(BitMask32().bit(self.ground_bit))

        # Why aren't we adding a collider?  There is no need to tell the collision traverser about this
        # collisionNode, as it will automatically be an Into object during traversal.

        # enable forces
        self.base.enableParticles()
        node = NodePath("PhysicsNode")
        node.reparentTo(self.base.render)

        # may want to have force dependent on mass eventually,
        # but at the moment assume all balls same weight
        self.force_mag = 200

        # gravity
        gravity_fn = ForceNode('world-forces')
        gravity_fnp = self.base.render.attachNewNode(gravity_fn)
        gravity_force = LinearVectorForce(0.0, 0.0, -9.81)
        gravity_fn.addForce(gravity_force)
        self.base.physicsMgr.addLinearForce(gravity_force)

        # wind
        wind_fn = ForceNode('world-forces')
        wind_fnp = self.base.render.attachNewNode(wind_fn)
        wind_force = LinearVectorForce(1.0, 0.5, 0.0)
        wind_fn.addForce(wind_force)
        self.base.physicsMgr.addLinearForce(wind_force)

        # spurt out of fountain, bounce
        self.spurt = ForceNode("spurt")
        spurt_np = self.base.render.attachNewNode(self.spurt)

        # create a list for our ball actors, not sure if I need this, but seems likely
        self.ball_actors = []

        # make a teapot
        teapot = loader.loadModel('teapot.egg')
        tex = loader.loadTexture('maps/color-grid.rgb')
        #teapot.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        teapot.setTexture(tex)
        teapot.reparentTo(self.base.render)
        teapot.setPos(-5, 10, 10)
        # create the first ball:
        #ball = self.create_a_ball()
        #self.enliven_ball(ball)

        smiley = loader.loadModel('smiley.egg')
        lerper = NodePath('lerper')
        smiley.setTexProjector(TextureStage.getDefault(), NodePath(), lerper)
        smiley.reparentTo(self.base.render)
        smiley.setPos(5, 10, 10)
        i = lerper.posInterval(5, VBase3(0, 1, 0))
        i.loop()

        # Tell the messenger system we're listening for smiley-into-ground messages and invoke our callback
        self.base.accept('ball_cnode-into-ground-cnode', self.ground_callback)

        ball_fountain = taskMgr.doMethodLater(.5, self.spurt_balls, 'tickTask')

        # tasks
        #self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        #self.frameTask.last = 0

    def frame_loop(self, task):
        # Make more balls!
        dt = task.time - task.last
        task.last = task.time
        # self.move_ball(dt)
        return task.cont

    # This task increments itself so that the delay between task executions
    # gradually increases over time. If you do not change task.delayTime
    # the task will simply repeat itself every 2 seconds
    def spurt_balls(self, task):
        print "Delay:", task.delayTime
        print "Frame:", task.frame
        # task.delayTime += 1
        # for i in range(5):
        ball = self.create_a_ball()
        self.enliven_ball(ball)
        return task.again

    def move_ball(self, dt):
        pass
        #x, y, z = self.ball.getPos()
        #print x, y, z
        #print self.actor_node.getPhysicsObject().getPosition()
        # rotate ball
        #prevRot = LRotationf(self.ball.getQuat())
        #axis = self.UP.cross(self.ballV)
        #newRot = LRotationf(axis, 45, 5 * dt)
        #self.ball.setQuat(prevRot + newRot)
        #print x, y, z
        #z += dt * self.thrust
        #x += dt * self.wind
        #y += dt * self.wind
        #self.ball.setPos(x, y, z)

    def remove_force(self, actor, force, task):
        print('remove force', force)
        actor.getPhysical(0).removeLinearForce(force)
        self.spurt.removeForce(force)
        return task.done

    def apply_spurt(self, actor_node, force=None):
        print 'spurt'
        print('force', force)
        #print actor_node
        # really want this to remember its previous state with that
        # particular ball, and reduce the force from then by some amount.
        if force is None:
            # force = LinearVectorForce(0.0, 0.0, self.force_mag)
            force = LinearVectorForce(0.0, 0.0, self.force_mag)
            self.spurt.addForce(force)
            print('new', force)
            #self.force_mag -= 15
        else:
            force.getAmplitude()
        # apply the spurt
        actor_node.getPhysical(0).addLinearForce(force)
        print('added force', self.spurt.getForce(0).getVector(actor_node.getPhysicsObject())[2])
        #print force, actor_node
        #for child in self.base.render.getChildren():
        #    print child
        # set a task that will clear this force a short moment later
        self.base.taskMgr.doMethodLater(0.01, self.remove_force, 'removeForceTask',
                                        extraArgs=[actor_node, force],
                                        appendTask=True)
        print 'set do method later'

    def ground_callback(self, entry):
        '''This is our ground collision message handler.  It is called whenever a collision message is
        triggered'''
        print 'callback'
        # Get our parent actor_node
        ball_actor_node = entry.getFromNodePath().getParent().node()
        # Why do we call getParent?  Because we are passed the CollisionNode during the event and the
        # ActorNode is one level up from there.  Our node graph looks like so:
        # - ActorNode
        #   + ModelNode
        #   + CollisionNode
        # add bounce!
        self.apply_spurt(ball_actor_node)

    def create_a_ball(self):
        print 'new ball'
        ball = self.base.loader.loadModel('smiley')
        texture = self.base.loader.loadTexture('models/textures/rock12.bmp')
        #ball.setTexture(texture)
        #tex = loader.loadTexture('maps/noise.rgb')
        ball.setPos(0, 0, 0)
        ball.reparentTo(self.base.render)
        ball.setTexture(texture, 1)
        return ball

    def enliven_ball(self, ball):
        # create an actor node for the balls
        ball_actor = self.base.render.attachNewNode(ActorNode("ball_actor_node"))
        # choose a random color
        #ball_actor.setColor(random.random(), random.random(), random.random(), random.random())
        self.create_ball_coll(ball_actor)
        # apply forces to it
        self.base.physicsMgr.attachPhysicalNode(ball_actor.node())
        #spurt_force = LinearVectorForce(0.0, 0.0, self.force_mag)
        #spurt_force.setMassDependent(True)
        #self.spurt.addForce(spurt_force)
        #self.spurt.addForce()
        self.apply_spurt(ball_actor.node())
        ball.reparentTo(ball_actor)
        self.ball_actors.append(ball_actor)

    def create_ball_coll(self, ball_actor):
        # Build a collisionNode for this smiley which is a sphere of the same diameter as the model
        ball_coll_node = ball_actor.attachNewNode(CollisionNode('ball_cnode'))
        ball_coll_sphere = CollisionSphere(0, 0, 0, 1)
        ball_coll_node.node().addSolid(ball_coll_sphere)
        # Watch for collisions with our brothers, so we'll push out of each other
        ball_coll_node.node().setIntoCollideMask(BitMask32().bit(self.ball_bit))
        # we're only interested in colliding with the ground and other smileys
        cMask = BitMask32()
        cMask.setBit(self.ground_bit)
        cMask.setBit(self.ball_bit)
        ball_coll_node.node().setFromCollideMask(cMask)

        # Now, to keep the spheres out of the ground plane and each other, let's attach a physics handler to them
        ball_handler = PhysicsCollisionHandler()

        # Set the physics handler to manipulate the smiley actor's transform.
        ball_handler.addCollider(ball_coll_node, ball_actor)

        # This call adds the physics handler to the traverser list
        # (not related to last call to addCollider!)
        self.base.cTrav.addCollider(ball_coll_node, ball_handler)

        # Now, let's set the collision handler so that it will also do a CollisionHandlerEvent callback
        # But...wait?  Aren't we using a PhysicsCollisionHandler?
        # The reason why we can get away with this is that all CollisionHandlerXs are inherited from
        # CollisionHandlerEvent,
        # so all the pattern-matching event handling works, too
        ball_handler.addInPattern('%fn-into-%in')

        return ball_coll_node

if __name__ == "__main__":
    MF = Fountain()
    MF.base.run()