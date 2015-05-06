from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import GeomNode
from panda3d.core import LVector3


# You can't normalize inline so this is a helper function
def normalized(*args):
    my_vec = LVector3(*args)
    my_vec.normalize()
    return my_vec


# helper function to make a square given the Lower-Left-Hand and
# Upper-Right-Hand corners
def make_square(sq_color):
    # sq_color is a list of tuples, describing each vertex:
    # (r, g, b, a) for [bl, br, tr, tl]
    x1 = -1
    y1 = -1
    z1 = -1
    x2 = 1
    y2 = -1
    z2 = 1
    v_format = GeomVertexFormat.getV3n3cpt2()
    v_data = GeomVertexData('square', v_format, Geom.UHDynamic)

    vertex = GeomVertexWriter(v_data, 'vertex')
    normal = GeomVertexWriter(v_data, 'normal')
    color = GeomVertexWriter(v_data, 'color')
    tex_coord = GeomVertexWriter(v_data, 'texcoord')

    # make sure we draw the sqaure in the right plane
    if x1 != x2:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y1, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y2, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y2 - 1, 2 * z2 - 1))

    else:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y2, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y1, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z2 - 1))

    # adding different colors to the vertex for visibility
    # color.addData4f(1.0, 0.0, 0.0, 1.0)
    # color.addData4f(0.0, 1.0, 0.0, 1.0)
    # color.addData4f(0.0, 0.0, 1.0, 1.0)
    # color.addData4f(1.0, 0.0, 1.0, 1.0)
    color.addData4f(sq_color[0])  # (0, 0) bottom left
    color.addData4f(sq_color[1])  # (0.5, 0) bottom right
    color.addData4f(sq_color[2])  # (0.5, 0.5) top right
    color.addData4f(sq_color[3])  # (0, 0.5) top left

    tex_coord.addData2f(0.0, 1.0)
    tex_coord.addData2f(0.0, 0.0)
    tex_coord.addData2f(1.0, 0.0)
    tex_coord.addData2f(1.0, 1.0)

    # Quads aren't directly supported by the Geom interface
    # you might be interested in the CardMaker class if you are
    # interested in rectangle though
    tris = GeomTriangles(Geom.UHDynamic)
    tris.addVertices(0, 1, 3)
    tris.addVertices(1, 2, 3)

    square = Geom(v_data)
    square.addPrimitive(tris)
    return square


class ColorWorld(object):
    def __init__(self):
        self.base = ShowBase()
        self.base.disableMouse()
        self.base.camera.setPos(0, -10, 0)
        color_vertices = [(0.2, 0.2, 0.1, 1),
                          (0.2, 0.7, 0.1, 1),
                          (0.7, 0.7, 0.1, 1),
                          (0.7, 0.2, 0.1, 1)]
        square = make_square(color_vertices)
        sq_node = GeomNode('square')
        sq_node.addGeom(square)
        self.base.render.attachNewNode(sq_node)

if __name__ == "__main__":
    CW = ColorWorld()
    CW.base.run()