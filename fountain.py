from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath
from panda3d.physics import ForceNode, LinearVectorForce, ActorNode


class Fountain(object):
    def __init__(self):
        self.base = ShowBase()
        self.thrust = 0.5
        self.wind = 0.2
        self.ball = self.base.loader.loadModel('smiley')
        self.ball.setPos(0, 0, 0)
        self.ball.reparentTo(self.base.render)
        # set up camera
        self.base.disableMouse()
        self.base.camera.setPos(20, -20, 5)
        self.base.camera.lookAt(0, 0, 5)
        # tasks
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.last = 0
        # enable forces
        self.base.enableParticles()
        node = NodePath("PhysicsNode")
        node.reparentTo(self.base.render)
        an = ActorNode("balls")
        anp = node.attachNewNode(an)
        self.base.physicsMgr.attachPhysicalNode(an)
        self.ball.reparentTo(anp)

        # gravity
        gravity_fn = ForceNode('world-forces')
        gravity_fnp = self.base.render.attachNewNode(gravity_fn)
        gravity_force = LinearVectorForce(0.0, 0.0, -9.81)
        gravity_fn.addForce(gravity_force)
        self.base.physicsMgr.addLinearForce(gravity_force)

        # spurt out of fountain
        spurt = ForceNode("spurt")
        spurt_np = self.base.render.attachNewNode(spurt)
        # may want to have force dependent on mass eventually,
        # but at the moment assume all balls same weight
        self.spurt_force = LinearVectorForce(0.0, 0.0, 30)
        #spurt_force.setMassDependent(True)
        spurt.addForce(self.spurt_force)

        # apply the spurt
        an.getPhysical(0).addLinearForce(self.spurt_force)

        # set a task that will clear this force a short moment later
        self.base.taskMgr.doMethodLater(0.1, self.remove_force, 'removeForceTask', extraArgs=[an], appendTask=True)

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.move_ball(dt)
        return task.cont

    def move_ball(self, dt):
        x, y, z = self.ball.getPos()
        #print x, y, z
        #z += dt * self.thrust
        x += dt * self.wind
        y += dt * self.wind
        self.ball.setPos(x, y, z)

    def remove_force(self, actor, task):
        actor.getPhysical(0).removeLinearForce(self.spurt_force)
        return(task.done)

if __name__ == "__main__":
    MF = Fountain()
    MF.base.run()