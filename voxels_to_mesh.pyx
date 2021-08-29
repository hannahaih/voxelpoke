from ursina import *
import cython
# from cpython cimport array
from libc.stdlib cimport malloc, free

cube_verts = [
    (0,0,0), (1,0,0), (1,0,1), (0,0,1),
    (0,1,0), (1,1,0), (1,1,1), (0,1,1)
]

'''
   7-------6
  /|      /|
 / |     / |
4--|----5  |
|  3----|--2
| /     | /
0-------1
'''

cube_side_uvs = ((0,0), (1,0), (0,1), (0,1), (1,0), (1,1))
cube_sides = (
    [cube_verts[i] for i in (1,2,5, 5,2,6)], # right
    [cube_verts[i] for i in (3,0,7, 7,0,4)], # left
    [cube_verts[i] for i in (4,5,7, 7,5,6)], # up
    [cube_verts[i] for i in (3,2,0, 0,2,1)], # down
    [cube_verts[i] for i in (2,3,6, 6,3,7)], # forward
    [cube_verts[i] for i in (0,1,4, 4,1,5)]  # back
)



@cython.ccall
@cython.locals(
width=cython.int, height=cython.int, depth=cython.int,
x=cython.int, y=cython.int, z=cython.int,
r=cython.int, l=cython.int, u=cython.int, d=cython.int, f=cython.int, b=cython.int,
)
def voxels_to_mesh(voxels):
    vertices = []
    uvs = []
    width = len(voxels)
    height = len(voxels[0])
    depth = len(voxels[0][0])
    cdef bint *neighbors = <bint *> malloc(6 * sizeof(bint))

    for x in range(width):
        for y in range(height):
            for z in range(depth):

                if voxels[x][y][z] == 0:
                    continue

                r, l, u, d, f, b = 0, 0, 0, 0, 0, 0     # right, left, up, down, forward, back

                # make sure we only get neighbors within bounds, otherwise stay as 0
                if x < width-1:
                    r = voxels[x+1][y][z]
                if x > 0:
                    l = voxels[x-1][y][z]
                if y < height-1:
                    u = voxels[x][y+1][z]
                if y > 0:
                    d = voxels[x][y-1][z]
                if z < depth-1:
                    f = voxels[x][y][z+1]
                if z > 0:
                    b = voxels[x][y][z-1]

                # neighbors = (r, l, u, d, f, b)
                neighbors[0] = r
                neighbors[1] = l
                neighbors[2] = u
                neighbors[3] = d
                neighbors[4] = f
                neighbors[5] = b

                if neighbors[0] > 0 and neighbors[1] > 0 and neighbors[2] > 0 and neighbors[3] > 0 and neighbors[4] > 0 and neighbors[5] > 0:
                    continue


                for i in range(6):
                    e = neighbors[i]
                    if not e:
                        vertices.extend([(e[0]+x, e[1]+y, e[2]+z) for e in cube_sides[i]])

                        y_offset = 0
                        y_offset += int(i==2) * 2       # top
                        y_offset += int(i not in (2,3)) * int(not u)    # sides without block above

                        # uvs.extend([e + Vec2((voxels[x][y][z]-1) / 8, y_offset/8) for e in cube_side_uvs])
                        uvs.extend([((e[0] + (voxels[x][y][z]-1))/8, (e[1] + y_offset)/8) for e in cube_side_uvs])

    free(neighbors)
    return vertices, uvs
