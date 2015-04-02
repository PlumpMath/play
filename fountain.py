from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, CardMaker, Plane, Vec3, Point3, BitMask32
from panda3d.core import CollisionTraverser, CollisionNode, CollisionPlane, CollisionSphere
from panda3d.core import LRotationf
from panda3d.physics import ForceNode, LinearVectorForce, ActorNode, PhysicsCollisionHandler


class Fountain(object):
    def __init__(self):
        self.base = ShowBase()
        self.thrust = 0.5
        self.wind = 0.2
        self.ball = self.base.loader.loadModel('smiley')
        self.ball.setPos(0, 0, 0)
        self.ball.reparentTo(self.base.render)
        self.UP = Vec3(0, 0, 1)  # might as well just make this a variable
        # set up camera
        self.base.disableMouse()
        self.base.camera.setPos(20, -20, 5)
        self.base.camera.lookAt(0, 0, 5)
        # tasks
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.last = 0

        # Set up the collision traverser.  If we bind it to base.cTrav, then Panda will handle
        # management of this traverser (for example, by calling traverse() automatically for us once per frame)
        self.base.cTrav = CollisionTraverser()

        # Now let's set up some collision bits for our masks
        ground_bit = 1
        ball_bit = 2

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
        groundColNode.setCollideMask(BitMask32().bit(ground_bit))

        # Why aren't we adding a collider?  There is no need to tell the collision traverser about this
        # collisionNode, as it will automatically be an Into object during traversal.

        # enable forces
        self.base.enableParticles()
        node = NodePath("PhysicsNode")
        node.reparentTo(self.base.render)

        # create an actor node for the balls
        ball_actor = self.base.render.attachNewNode(ActorNode("ball_actor_node"))
        self.ball.reparentTo(ball_actor)

        # apply forces to it
        self.base.physicsMgr.attachPhysicalNode(ball_actor.node())

        # Build a collisionNode for this smiley which is a sphere of the same diameter as the model
        ball_coll_node = ball_actor.attachNewNode(CollisionNode('ball_cnode'))
        ball_coll_sphere = CollisionSphere(0, 0, 0, 1)
        ball_coll_node.node().addSolid(ball_coll_sphere)

        # Watch for collisions with our brothers, so we'll push out of each other
        ball_coll_node.node().setIntoCollideMask(BitMask32().bit(ball_bit))

        # we're only interested in colliding with the ground and other smileys
        cMask = BitMask32()
        cMask.setBit (ground_bit)
        cMask.setBit (ball_bit)
        ball_coll_node.node().setFromCollideMask(cMask)

        # Now, to keep the spheres out of the ground plane and each other, let's attach a physics handler to them
        ball_handler = PhysicsCollisionHandler()

        # Set the physics handler to manipulate the smiley actor's transform.
        ball_handler.addCollider(ball_coll_node, ball_actor)

        # This call adds the physics handler to the traverser list
        # (not related to last call to addCollider!)
        self.base.cTrav.addCollider (ball_coll_node, ball_handler)

        # Now, let's set the collision handler so that it will also do a CollisionHandlerEvent callback
        # But...wait?  Aren't we using a PhysicsCollisionHandler?
        # The reason why we can get away with this is that all CollisionHandlerXs are inherited from CollisionHandlerEvent,
        # so all the pattern-matching event handling works, too
        ball_handler.addInPattern ('%fn-into-%in')

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
        # may want to have force dependent on mass eventually,
        # but at the moment assume all balls same weight
        self.force_mag = 30
        spurt_force = LinearVectorForce(0.0, 0.0, self.force_mag)
        #spurt_force.setMassDependent(True)
        self.spurt.addForce(spurt_force)
        self.apply_spurt(ball_actor.node(), spurt_force)
        #self.actor_node = ball_actor.node()
        # Tell the messenger system we're listening for smiley-into-ground messages and invoke our callback
        self.base.accept('ball_cnode-into-ground-cnode', self.ground_callback)

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.move_ball(dt)
        return task.cont

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
        if force is None:
            force = LinearVectorForce(0.0, 0.0, self.force_mag)
            self.spurt.addForce(force)
            print('new', force)
            self.force_mag -= 15
        # apply the spurt
        actor_node.getPhysical(0).addLinearForce(force)
        print('added force', self.spurt.getForce(0).getVector(actor_node.getPhysicsObject())[2])
        #print force, actor_node
        #for child in self.base.render.getChildren():
        #    print child
        # set a task that will clear this force a short moment later
        self.base.taskMgr.doMethodLater(0.1, self.remove_force, 'removeForceTask',
                                        extraArgs=[actor_node, force],
                                        appendTask=True)
        print 'set do method later'

    def ground_callback(self, entry):
        '''This is our ground collision message handler.  It is called whenever a collision message is
        triggered'''
        print 'callback'
        # Get our parent actor_node
        smiley_actor_node = entry.getFromNodePath().getParent().node()
        # Why do we call getParent?  Because we are passed the CollisionNode during the event and the
        # ActorNode is one level up from there.  Our node graph looks like so:
        # - ActorNode
        #   + ModelNode
        #   + CollisionNode

        self.apply_spurt(smiley_actor_node)

if __name__ == "__main__":
    MF = Fountain()
    MF.base.run()