from ursina import *


# # override the built in round to easily round Vec3 and tuples/lists
# from panda3d.core import Vec3 as PandaVec3
# builtin_round = round
# def round(value, decimals=0):
#     if isinstance(value, (Vec3, PandaVec3)):
#         return Vec3(builtin_round(value[0],decimals), builtin_round(value[1],decimals), builtin_round(value[2],decimals))
#
#     if isinstance(value, list):
#         return [builtin_round(e,decimals) for e in value]
#
#     if isinstance(value, tuple):
#         return tuple(builtin_round(e,decimals) for e in value)
#
#     return builtin_round(value, decimals)
# # from panda3d.core import Vec3




app = Ursina()
camera.orthographic = True
camera.fov = 30
camera.y = 10
# window.size *= .75

# make hexagon
w = 3.46
verts = list()
points = list()
random.seed(1)

# bottom part of the hexagon
for z in range(1, 6):
    for x in range(z):
        # points.append(Vec3((x+.5-(z/2))*w, z-1))
        verts.extend((
            Vec3((x+.5-(z/2))*w, 0, z-1), Vec3((x+1-(z/2))*w, 0, z,), Vec3((x+.5-(z/2))*w, 0, z+1),
            Vec3((x+.5-(z/2))*w, 0, z-1), Vec3((x+.5-(z/2))*w, 0, z+1), Vec3((x-(z/2))*w, 0, z),
        ))

# middle part of the hexagon
for z in range(1, 10):
    length = 6
    offset = .5
    if z%2 == 0:
        length -= 1
        offset = 1

    for x in range(length):
        # points.append(Vec3(((x+offset-(6/2))*w), z+4))
        if x == 0 and z < 10 and z%2 != 0:
            verts.extend((
                Vec3(((x+offset-(6/2))*w), 0, z+4), Vec3(((x+offset+.5-(6/2))*w), 0, z+5), Vec3(((x+offset-(6/2))*w), 0, z+6),
            ))
        elif x == length-1 and z < 10 and z%2 != 0:
            verts.extend((
            Vec3(((x+offset-(6/2))*w), 0, z+4), Vec3(((x+offset-(6/2))*w), 0, z+6), Vec3(((x+offset-.5-(6/2))*w), 0, z+5),
            ))

        else:
            verts.extend((
                Vec3(((x+offset-(6/2))*w), 0, z+4), Vec3(((x+offset+.5-(6/2))*w), 0, z+5), Vec3(((x+offset-(6/2))*w), 0, z+6),
                Vec3(((x+offset-(6/2))*w), 0, z+4), Vec3(((x+offset-(6/2))*w), 0, z+6), Vec3(((x+offset-.5-(6/2))*w), 0, z+5),
            ))

# top part of the hexagon
for z in range(5, 0, -1):
    for x in range(z):
        # points.append(Vec3((x+.5-(z/2))*w, 19-z))
        verts.extend((
            Vec3((x+.5-(z/2))*w, 0, 19-z), Vec3((x+1-(z/2))*w, 0, 20-z), Vec3((x+.5-(z/2))*w, 0, 21-z),
            Vec3((x+.5-(z/2))*w, 0, 19-z), Vec3((x+.5-(z/2))*w, 0, 21-z), Vec3((x-(z/2))*w, 0, 20-z),
        ))

outline_lines = (
    (Vec3(0*w, 0, 0)),
    Vec3(2.5*w, 0, 5),
    Vec3(2.5*w, 0, 15),
    Vec3(0*w, 0, 20),
    Vec3(-2.5*w, 0, 15),
    Vec3(-2.5*w, 0, 5),
    )
outline_lines = (
    (outline_lines[0], outline_lines[1]),
    (outline_lines[1], outline_lines[2]),
    (outline_lines[2], outline_lines[3]),
    (outline_lines[3], outline_lines[4]),
    (outline_lines[4], outline_lines[5]),
    (outline_lines[5], outline_lines[0]),
    )
outline_points = list()
for line in outline_lines:
    segments = 10
    for j in range(segments):
        p = lerp(line[0], line[1], j/segments)
        p = round(p, 3)
        outline_points.append(p)


outline_mesh = Entity(model=Mesh(vertices=outline_points, mode='point', thickness=3), color=color.cyan, y=-.01, eternal=True)
hexagon = Entity(model=Mesh(vertices=verts), y=-.02, color=color.white33, eternal=True)
# hexagon_points = Entity(model=Mesh(vertices=verts, mode='point', thickness=5), y=-.1)
triangle_verts = [(verts[i], verts[i+1], verts[i+2]) for i in range(0, len(verts), 3)]

grid_mesh = Mesh(vertices=list(), triangles=list(), mode='line')
grid = Entity(model=grid_mesh, color=color.white, eternal=True)


def connect():
    current_tri = random.choice(triangle_verts)
    connections = list()

    for t in triangle_verts:
        if len(set(tuple(current_tri) + tuple(t))) == 4: # get pairs with only 4 unique points, they are valid neighbors
            connections.append(t)

    if not connections:
        # print('no valid connections found')
        return False

    random_neighbor = random.choice(connections)

    current_center = (current_tri[0] + current_tri[1] + current_tri[2]) / 3
    print('-----------', current_tri)
    neighbor_center = (random_neighbor[0] + random_neighbor[1] + random_neighbor[2]) / 3
    center = (current_center + neighbor_center) / 2
    center = round(center, 3)
    quad = tuple(set(current_tri + random_neighbor))


    if current_center[2] == neighbor_center[2]:  # flat ones <>
        s, n = [e for e in quad if not e[2] == center[2]]
        if s[2] > n[2]:
            s, n = n, s
        w, e = [e for e in quad if not e in (s,n)]
        if w[0] > e[0]:
            w, e = e, w

    elif current_center[0] < neighbor_center[0]:
        if current_center[2] < neighbor_center[2]:  # right up
            s,e,n,w = current_tri[0], current_tri[1], random_neighbor[1], current_tri[2]
        else:   # right down
            s,e,n,w = current_tri[0], random_neighbor[0], current_tri[1], current_tri[2]
    else:   # left up
        if current_center[2] < neighbor_center[2]:
            s,e,n,w = current_tri[0], current_tri[1], random_neighbor[2], current_tri[2]
        else:   # left down
            s,e,n,w = current_tri[0], current_tri[1], current_tri[2], random_neighbor[0]

    se,ne,nw,sw = (s+e)/2, (n+e)/2, (n+w)/2, (s+w)/2

    cc_shape = (s,se,e,ne,n,nw,w,sw) # points in counter clockwise order
    # print('--------------',  cc_shape[0], round(cc_shape[0]))
    cc_shape = [round(e, 3) for e in cc_shape]
    # print('ccccccccc', cc_shape[0])
    betweens = (cc_shape[1], cc_shape[3], cc_shape[5], cc_shape[7])

    grid_mesh.vertices.append(center)
    grid_mesh.vertices.extend(cc_shape)

    quads = ((center,se,e,ne), (center,ne,n,nw), (center,nw,w,sw), (center,sw,s,se))

    for q in quads:
        quad_tris = [grid_mesh.vertices.index(round(e, 3)) for e in q]
        # print('||||', quad_tris)
        grid_mesh.triangles.append(quad_tris)
        print(grid_mesh.triangles)

    grid_mesh.generate()

    triangle_verts.remove(current_tri)
    triangle_verts.remove(random_neighbor)
    return True




def subdivide_triangles():
    for current_tri in triangle_verts:
        center = (current_tri[0] + current_tri[1] + current_tri[2]) / 3
        center = round(center, 3)

        a, b, c = current_tri
        ab, bc, ca = (a+b)/2, (b+c)/2, (c+a)/2

        cc_shape = (a,ab,b,bc,c,ca) # points in counter clockwise order
        cc_shape = [round(e,3) for e in cc_shape]
        betweens = (cc_shape[1], cc_shape[3], cc_shape[5])

        grid_mesh.vertices.append(center)
        grid_mesh.vertices.extend(cc_shape)

        quads = ((center,ab,b,bc), (center,bc,c,ca), (center,ca,a,ab))

        for q in quads:
            quad_tris = [grid_mesh.vertices.index(round(e, 3)) for e in q]
            grid_mesh.triangles.append(quad_tris)

    triangle_verts.remove(current_tri)
    grid_mesh.generate()


def relax():
    # remove duplicate verts
    unique_verts = tuple(set(grid_mesh.vertices))
    print('reducing vertices from', len(grid_mesh.vertices), 'to', len(unique_verts))

    new_tris = list()
    for quad in grid_mesh.triangles:
        quad = [unique_verts.index(grid_mesh.vertices[i]) for i in quad]
        new_tris.append(quad)

    grid_mesh.triangles = new_tris
    grid_mesh.vertices = unique_verts


    relaxed_verts = list()
    for i, v in enumerate(grid_mesh.vertices):

        if v in outline_points:
            relaxed_verts.append(v)
            continue

        surrounding_quads = [e for e in grid_mesh.triangles if i in e]
        surrounding_quads = [item for sublist in surrounding_quads for item in sublist] # flatten list
        surrounding_quads = [e for e in surrounding_quads if not e == i] # ignore center vert
        surrounding_quads = tuple(set(surrounding_quads)) # remove duplicates

        mean = Vec3(0,0,0)
        for j in surrounding_quads:
            mean += grid_mesh.vertices[j]

        mean /= len(surrounding_quads)
        relaxed_verts.append(mean)


    grid_mesh.vertices = relaxed_verts
    grid_mesh.generate()



def connect_randomly():
    misses = 0
    while misses < 16:
        if connect() == False:
            misses += 1

def extrude(quad_index, amount=1, regenerate=True):
    quad = grid_mesh.triangles[quad_index]
    extra_tris = list()

    added_verts = [grid_mesh.vertices[i] + Vec3(0,amount,0) for i in quad]
    grid_mesh.vertices.extend(added_verts)

    added_tris = [len(grid_mesh.vertices)-4+i for i in range(4)]
    extra_tris.append(added_tris)
    # add sides
    side_quad = [e for e in quad]
    side_quad.append(side_quad[0])
    side_tris = [e for e in added_tris]
    side_tris.append(side_tris[0])

    for i in range(4):
        extra_tris.append([side_quad[i], side_quad[i+1], side_tris[i+1], side_tris[i]])

    # added_cols = (color.color(0,0,extrusion_amount/5), ) * 4
    # print(added_cols)
    # grid_mesh.colors.extend(added_cols)
    # print('lol', extra_tris)
    grid_mesh.triangles.extend(extra_tris)

    if regenerate:
        grid_mesh.generate()



test_index = 0
# test_model = Entity(model=Mesh(vertices=list(), mode='point', thickness=8), color=color.blue, y=-3)
# test_origin = Entity(model='quad', scale=.25, color=color.orange)

def input(key):
    global test_index
    if key == 'space' or key == 'space hold':
        connect()

    if key == 'r':
        connect_randomly()
        connect_randomly()
        print('finished connecting quads')

    if key == 't':
        subdivide_triangles()

    if key == 's':
        relax()


    if key == 'enter':
        connect_randomly()
        connect_randomly()
        print('finished connecting quads')
        subdivide_triangles()
        relax()
        grid_mesh.save('irregular_grid')

    if key == 'e':
        number_of_quads = len(grid_mesh.triangles)
        for i in range(number_of_quads):
            if random.random() < .1:
                continue

            extrusion_amount = random.randint(0, 4)
            extrude(i, extrusion_amount, False)

        grid_mesh.mode = 'triangle'
        grid_mesh.colorize(smooth=False)

EditorCamera()



app.run()
